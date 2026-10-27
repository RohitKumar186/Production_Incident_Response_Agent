# backend/api/incidents.py

import json
from dataclasses import asdict
from typing import Any

from fastapi import APIRouter, HTTPException

from backend.database.connection import get_connection
from backend.schemas.incident import IncidentCreate, IncidentResponse
from backend.services.pira_service import run_investigation_and_rca


router = APIRouter(
    prefix="/api/incidents",
    tags=["Incidents"],
)


# =========================================================
# HELPER
# =========================================================

def serialize_object(obj: Any) -> Any:
    """
    Convert objects into JSON-serializable Python objects.

    Handles:
    - datetime / date
    - Pydantic models
    - dataclasses
    - dictionaries / RealDictRow
    - lists
    - tuples
    - normal Python objects
    """

    if obj is None:
        return None

    # -----------------------------------------------------
    # datetime / date
    # -----------------------------------------------------

    if hasattr(obj, "isoformat"):
        return obj.isoformat()

    # -----------------------------------------------------
    # Pydantic v2
    # -----------------------------------------------------

    if hasattr(obj, "model_dump"):
        return serialize_object(
            obj.model_dump()
        )

    # -----------------------------------------------------
    # Pydantic v1
    # -----------------------------------------------------

    if hasattr(obj, "dict"):
        return serialize_object(
            obj.dict()
        )

    # -----------------------------------------------------
    # Dataclass
    # -----------------------------------------------------

    if hasattr(obj, "__dataclass_fields__"):
        return serialize_object(
            asdict(obj)
        )

    # -----------------------------------------------------
    # Dictionary / RealDictRow
    # -----------------------------------------------------

    if isinstance(obj, dict):
        return {
            key: serialize_object(value)
            for key, value in obj.items()
        }

    # -----------------------------------------------------
    # List
    # -----------------------------------------------------

    if isinstance(obj, list):
        return [
            serialize_object(item)
            for item in obj
        ]

    # -----------------------------------------------------
    # Tuple
    # -----------------------------------------------------

    if isinstance(obj, tuple):
        return [
            serialize_object(item)
            for item in obj
        ]

    # -----------------------------------------------------
    # Normal Python object
    # -----------------------------------------------------

    if hasattr(obj, "__dict__"):
        return {
            key: serialize_object(value)
            for key, value in obj.__dict__.items()
            if not key.startswith("_")
        }

    return obj


# =========================================================
# CREATE INCIDENT
# =========================================================

@router.post(
    "/",
    response_model=IncidentResponse,
)
def create_incident(
    incident: IncidentCreate,
):

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        # =================================================
        # 1. INSERT INCIDENT
        # =================================================

        cursor.execute(
            """
            INSERT INTO incidents (
                incident_id,
                incident_type,
                severity,
                affected_service,
                title,
                description,
                detected_at,
                metadata,
                status
            )
            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            RETURNING *;
            """,
            (
                incident.incident_id,
                incident.incident_type,
                incident.severity,
                incident.affected_service,
                incident.title,
                incident.description,
                incident.detected_at,
                json.dumps(
                    incident.metadata
                ),
                "OPEN",
            ),
        )

        created_incident = cursor.fetchone()

        # =================================================
        # 2. AUDIT: INCIDENT CREATED
        # =================================================

        cursor.execute(
            """
            INSERT INTO audit_logs (
                incident_id,
                action,
                actor,
                component,
                details
            )
            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s
            );
            """,
            (
                incident.incident_id,
                "INCIDENT_CREATED",
                "API",
                "incidents_api",
                json.dumps({
                    "status": "OPEN"
                }),
            ),
        )

        # =================================================
        # 3. STATUS → INVESTIGATING
        # =================================================

        cursor.execute(
            """
            UPDATE incidents
            SET status = %s
            WHERE incident_id = %s;
            """,
            (
                "INVESTIGATING",
                incident.incident_id,
            ),
        )

        # =================================================
        # 4. AUDIT: INVESTIGATION STARTED
        # =================================================

        cursor.execute(
            """
            INSERT INTO audit_logs (
                incident_id,
                action,
                actor,
                component,
                details
            )
            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s
            );
            """,
            (
                incident.incident_id,
                "INVESTIGATION_STARTED",
                "PIRA",
                "incidents_api",
                json.dumps({
                    "status": "INVESTIGATING"
                }),
            ),
        )

        connection.commit()

        # =================================================
        # 5. TASK 1 → TASK 2 → TASK 3 → TASK 4
        # =================================================

        try:

            pipeline_result = (
                run_investigation_and_rca(
                    created_incident
                )
            )

            investigation_card = (
                pipeline_result["investigation"]
            )

            rca_output = (
                pipeline_result["rca"]
            )

            # =================================================
            # 6. SERIALIZE INVESTIGATION
            # =================================================

            investigation_data = serialize_object(
                investigation_card
            )

            # =================================================
            # 7. SERIALIZE RCA
            # =================================================

            rca_data = serialize_object(
                rca_output
            )

            # =================================================
            # 8. INVESTIGATION DATA
            # =================================================

            # IMPORTANT:
            # Task 1 → Task 4 returns a Knowledge Card.
            # Actual findings are inside payload.

            investigation_payload = investigation_data.get(
                "payload",
                {},
            )

            if not isinstance(
                investigation_payload,
                dict,
            ):
                investigation_payload = {}

            investigation_findings = (
                investigation_payload.get(
                    "findings",
                    [],
                )
            )

            if investigation_findings is None:
                investigation_findings = []

            # Findings themselves contain the detailed evidence.
            investigation_evidence = (
                investigation_payload.get(
                    "evidence",
                    investigation_findings,
                )
            )

            if investigation_evidence is None:
                investigation_evidence = investigation_findings

            investigation_summary = (
                investigation_data.get("summary")
                or investigation_payload.get("summary")
                or (
                    f"Investigation completed. "
                    f"Total findings: "
                    f"{len(investigation_findings)}"
                )
            )

            # =================================================
            # 9. SAVE INVESTIGATION
            # =================================================

            cursor.execute(
                """
                INSERT INTO investigations (
                    incident_id,
                    investigator,
                    summary,
                    findings,
                    evidence,
                    status
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                RETURNING id;
                """,
                (
                    incident.incident_id,
                    "PIRA_INVESTIGATION",
                    investigation_summary,
                    json.dumps(
                        serialize_object(
                            investigation_findings
                        ),
                        default=str,
                    ),
                    json.dumps(
                        serialize_object(
                            investigation_evidence
                        ),
                        default=str,
                    ),
                    "SUCCESS",
                ),
            )

            investigation_id = (
                cursor.fetchone()["id"]
            )

            # =================================================
            # 10. SAVE EVIDENCE
            # =================================================

            # Each investigation finding becomes
            # one evidence row in PostgreSQL.

            if isinstance(
                investigation_findings,
                list,
            ):

                for finding in investigation_findings:

                    evidence_data = (
                        serialize_object(
                            finding
                        )
                    )

                    if not isinstance(
                        evidence_data,
                        dict,
                    ):
                        evidence_data = {
                            "value": evidence_data
                        }

                    evidence_type = (
                        evidence_data.get(
                            "category"
                        )
                        or evidence_data.get(
                            "evidence_type"
                        )
                        or evidence_data.get(
                            "type"
                        )
                        or evidence_data.get(
                            "agent"
                        )
                        or "UNKNOWN"
                    )

                    source = (
                        evidence_data.get(
                            "agent"
                        )
                        or evidence_data.get(
                            "source"
                        )
                        or "PIRA"
                    )

                    description = (
                        evidence_data.get(
                            "finding"
                        )
                        or evidence_data.get(
                            "description"
                        )
                        or evidence_data.get(
                            "summary"
                        )
                        or evidence_data.get(
                            "value"
                        )
                        or str(evidence_data)
                    )

                    cursor.execute(
                        """
                        INSERT INTO evidence (
                            incident_id,
                            investigation_id,
                            evidence_type,
                            source,
                            description,
                            data
                        )
                        VALUES (
                            %s,
                            %s,
                            %s,
                            %s,
                            %s,
                            %s
                        );
                        """,
                        (
                            incident.incident_id,
                            investigation_id,
                            str(
                                evidence_type
                            ).upper(),
                            source,
                            description,
                            json.dumps(
                                evidence_data,
                                default=str,
                            ),
                        ),
                    )

            # =================================================
            # 11. SAVE INVESTIGATION AGENT RUN
            # =================================================

            cursor.execute(
                """
                INSERT INTO agent_runs (
                    incident_id,
                    agent_name,
                    stage,
                    status,
                    input_data,
                    output_data
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                );
                """,
                (
                    incident.incident_id,
                    "PIRA_INVESTIGATION",
                    "INVESTIGATION",
                    "SUCCESS",
                    json.dumps(
                        serialize_object(
                            created_incident
                        ),
                        default=str,
                    ),
                    json.dumps(
                        investigation_data,
                        default=str,
                    ),
                ),
            )

                        # =================================================
            # 12. RCA DATA
            # =================================================

            # Support both raw RCA output and Knowledge Cards.
            rca_payload = rca_data.get("payload", {})

            if not isinstance(rca_payload, dict):
                rca_payload = {}

            rca_source = rca_payload if rca_payload else rca_data

            nested_rca = rca_source.get("rca")
            if isinstance(nested_rca, dict):
                rca_source = nested_rca

            root_cause = (
                rca_source.get("root_cause")
                or rca_source.get("root_cause_analysis")
                or {}
            )

            if isinstance(root_cause, dict):
                root_cause_text = (
                    root_cause.get("description")
                    or root_cause.get("root_cause")
                    or root_cause.get("finding")
                    or json.dumps(root_cause, default=str)
                )
                root_cause_confidence = root_cause.get("confidence")
            else:
                root_cause_text = str(root_cause)
                root_cause_confidence = None

            confidence = (
                rca_source.get("confidence")
                or root_cause_confidence
                or 0.0
            )

            contributing_factors = (
                rca_source.get("contributing_factors")
                or rca_source.get("supporting_evidence")
                or []
            )

            recommended_action = (
                rca_source.get("recommended_action")
                or rca_source.get("recommendation")
                or {}
            )

            if isinstance(recommended_action, dict):
                recommended_action_text = (
                    recommended_action.get("action")
                    or recommended_action.get("description")
                    or recommended_action.get("recommended_action")
                    or recommended_action.get("summary")
                    or "No remediation action specified"
                )
            else:
                recommended_action_text = str(recommended_action)

            # =================================================
            # 13. SAVE RCA RESULT
            # =================================================

            cursor.execute(
                """
                INSERT INTO rca_results (
                    incident_id,
                    root_cause,
                    confidence,
                    contributing_factors,
                    recommended_action,
                    status
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                );
                """,
                (
                    incident.incident_id,
                    root_cause_text,
                    float(confidence),
                    json.dumps(
                        serialize_object(
                            contributing_factors
                        ),
                        default=str,
                    ),
                    recommended_action_text,
                    "SUCCESS",
                ),
            )

            # =================================================
            # 14. SAVE RCA AGENT RUN
            # =================================================

            cursor.execute(
                """
                INSERT INTO agent_runs (
                    incident_id,
                    agent_name,
                    stage,
                    status,
                    input_data,
                    output_data
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                );
                """,
                (
                    incident.incident_id,
                    "PIRA_RCA",
                    "RCA",
                    "SUCCESS",
                    json.dumps(
                        investigation_data,
                        default=str,
                    ),
                    json.dumps(
                        rca_data,
                        default=str,
                    ),
                ),
            )

            # =================================================
            # 15. AUDIT: RCA COMPLETED
            # =================================================

            cursor.execute(
                """
                INSERT INTO audit_logs (
                    incident_id,
                    action,
                    actor,
                    component,
                    details
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                );
                """,
                (
                    incident.incident_id,
                    "RCA_COMPLETED",
                    "PIRA_RCA",
                    "incidents_api",
                    json.dumps({
                        "root_cause":
                            root_cause_text,
                        "confidence":
                            confidence,
                    }),
                ),
            )

            # =================================================
            # 16. CREATE REMEDIATION PROPOSAL
            # =================================================

            proposal_risk = (
                recommended_action.get(
                    "risk"
                )
                or recommended_action.get(
                    "risk_level"
                )
                or "MEDIUM"
            )

            proposal_rationale = json.dumps({
                "root_cause":
                    root_cause_text,

                "confidence":
                    confidence,

                "target":
                    recommended_action.get(
                        "target"
                    ),

                "action_type":
                    recommended_action.get(
                        "action_type"
                    ),

                "requires_human_approval":
                    recommended_action.get(
                        "requires_human_approval",
                        True,
                    ),
            })

            cursor.execute(
                """
                INSERT INTO remediation_proposals (
                    incident_id,
                    action,
                    rationale,
                    risk_level,
                    proposed_by,
                    approval_status,
                    execution_status
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                RETURNING id;
                """,
                (
                    incident.incident_id,
                    recommended_action_text,
                    proposal_rationale,
                    proposal_risk,
                    "PIRA_RCA",
                    "PENDING",
                    "PENDING",
                ),
            )

            remediation_id = (
                cursor.fetchone()["id"]
            )

            # =================================================
            # 17. AUDIT: REMEDIATION PROPOSED
            # =================================================

            cursor.execute(
                """
                INSERT INTO audit_logs (
                    incident_id,
                    action,
                    actor,
                    component,
                    details
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                );
                """,
                (
                    incident.incident_id,
                    "REMEDIATION_PROPOSED",
                    "PIRA_RCA",
                    "incidents_api",
                    json.dumps({
                        "remediation_id":
                            remediation_id,

                        "action":
                            recommended_action_text,

                        "risk_level":
                            proposal_risk,

                        "approval_status":
                            "PENDING",
                    }),
                ),
            )

            # =================================================
            # 18. INCIDENT STATUS → RCA_COMPLETED
            # =================================================

            cursor.execute(
                """
                UPDATE incidents
                SET status = %s
                WHERE incident_id = %s;
                """,
                (
                    "RCA_COMPLETED",
                    incident.incident_id,
                ),
            )

            connection.commit()

        except Exception as pipeline_error:

            connection.rollback()

            # =================================================
            # MARK INCIDENT FAILED
            # =================================================

            try:

                cursor.execute(
                    """
                    UPDATE incidents
                    SET status = %s
                    WHERE incident_id = %s;
                    """,
                    (
                        "FAILED",
                        incident.incident_id,
                    ),
                )

                cursor.execute(
                    """
                    INSERT INTO audit_logs (
                        incident_id,
                        action,
                        actor,
                        component,
                        details
                    )
                    VALUES (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
                    );
                    """,
                    (
                        incident.incident_id,
                        "PIPELINE_FAILED",
                        "PIRA",
                        "incidents_api",
                        json.dumps({
                            "error":
                                str(
                                    pipeline_error
                                )
                        }),
                    ),
                )

                connection.commit()

            except Exception:
                connection.rollback()

            raise HTTPException(
                status_code=500,
                detail={
                    "message":
                        "Incident processing failed",

                    "incident_id":
                        incident.incident_id,

                    "error":
                        str(
                            pipeline_error
                        ),
                },
            )

        # =================================================
        # 19. GET FINAL INCIDENT
        # =================================================

        cursor.execute(
            """
            SELECT *
            FROM incidents
            WHERE incident_id = %s;
            """,
            (
                incident.incident_id,
            ),
        )

        final_incident = (
            cursor.fetchone()
        )

        if not final_incident:

            raise HTTPException(
                status_code=404,
                detail=
                    "Incident not found after creation",
            )

        return final_incident

    # =====================================================
    # OUTER ERROR
    # =====================================================

    except HTTPException:
        raise

    except Exception as error:

        if connection:
            connection.rollback()

        raise HTTPException(
            status_code=500,
            detail={
                "message":
                    "Failed to create incident",

                "error":
                    str(error),
            },
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# GET INCIDENT HISTORY
# =========================================================

@router.get("/history")
def get_incident_history():

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM incidents
            ORDER BY created_at DESC;
            """
        )

        return cursor.fetchall()

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# GET INCIDENT HISTORY BY ID
# =========================================================

@router.get(
    "/history/{incident_id}"
)
def get_incident_history_by_id(
    incident_id: str,
):

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM incidents
            WHERE incident_id = %s;
            """,
            (
                incident_id,
            ),
        )

        incident = cursor.fetchone()

        if not incident:

            raise HTTPException(
                status_code=404,
                detail="Incident not found",
            )

        return incident

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# GET SINGLE INCIDENT
# =========================================================

@router.get(
    "/{incident_id}",
    response_model=IncidentResponse,
)
def get_incident(
    incident_id: str,
):

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM incidents
            WHERE incident_id = %s;
            """,
            (
                incident_id,
            ),
        )

        incident = cursor.fetchone()

        if not incident:

            raise HTTPException(
                status_code=404,
                detail="Incident not found",
            )

        return incident

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# GET ALL INCIDENTS
# =========================================================

@router.get("/")
def get_incidents():

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM incidents
            ORDER BY created_at DESC;
            """
        )

        return cursor.fetchall()

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# UPDATE INCIDENT STATUS
# =========================================================

@router.patch(
    "/{incident_id}/status"
)
def update_incident_status(
    incident_id: str,
    status: str,
):

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        # -------------------------------------------------
        # CHECK INCIDENT
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT incident_id
            FROM incidents
            WHERE incident_id = %s;
            """,
            (
                incident_id,
            ),
        )

        if not cursor.fetchone():

            raise HTTPException(
                status_code=404,
                detail="Incident not found",
            )

        # -------------------------------------------------
        # UPDATE STATUS
        # -------------------------------------------------

        cursor.execute(
            """
            UPDATE incidents
            SET status = %s
            WHERE incident_id = %s
            RETURNING *;
            """,
            (
                status,
                incident_id,
            ),
        )

        updated_incident = (
            cursor.fetchone()
        )

        # -------------------------------------------------
        # AUDIT
        # -------------------------------------------------

        cursor.execute(
            """
            INSERT INTO audit_logs (
                incident_id,
                action,
                actor,
                component,
                details
            )
            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s
            );
            """,
            (
                incident_id,
                "STATUS_UPDATED",
                "API",
                "incidents_api",
                json.dumps({
                    "new_status": status
                }),
            ),
        )

        connection.commit()

        return updated_incident

    except HTTPException:
        raise

    except Exception as error:

        if connection:
            connection.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()