import json
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.database.connection import get_connection
from backend.orchestrator.pira_orchestrator import pira_orchestrator

from TASK5.approval.approval import ApprovalDecision
from TASK4.models.schemas import RCAOutput


router = APIRouter(
    prefix="/api/incidents",
    tags=["Approval"]
)


# =========================================================
# REQUEST MODELS
# =========================================================

class ApprovalRequest(BaseModel):
    remediation_id: int
    approved_by: str = "operator"
    reason: str | None = None


class RejectRequest(BaseModel):
    remediation_id: int
    rejected_by: str = "operator"
    reason: str | None = None


# =========================================================
# SERIALIZATION HELPER
# =========================================================

def serialize_object(obj: Any) -> Any:

    if obj is None:
        return None

    if hasattr(obj, "model_dump"):
        return serialize_object(obj.model_dump())

    if hasattr(obj, "dict"):
        return serialize_object(obj.dict())

    if isinstance(obj, dict):
        return {
            key: serialize_object(value)
            for key, value in obj.items()
        }

    if isinstance(obj, (list, tuple)):
        return [
            serialize_object(item)
            for item in obj
        ]

    if hasattr(obj, "isoformat"):
        return obj.isoformat()

    return obj


# =========================================================
# LOAD RCA OUTPUT
# =========================================================

def load_rca_output(cursor, incident_id: str) -> RCAOutput:

    cursor.execute(
        """
        SELECT output_data
        FROM agent_runs
        WHERE incident_id = %s
          AND stage = %s
          AND status = %s
        ORDER BY id DESC
        LIMIT 1;
        """,
        (
            incident_id,
            "RCA",
            "SUCCESS"
        )
    )

    row = cursor.fetchone()

    if not row:
        raise HTTPException(
            status_code=404,
            detail="Successful RCA result not found"
        )

    output_data = row["output_data"]

    # PostgreSQL JSONB may already be a dict.
    # Handle string JSON as well.
    if isinstance(output_data, str):

        try:
            output_data = json.loads(output_data)

        except json.JSONDecodeError:

            raise HTTPException(
                status_code=500,
                detail="Invalid JSON stored in RCA output"
            )

    if not isinstance(output_data, dict):

        raise HTTPException(
            status_code=500,
            detail="Invalid RCA output stored in agent_runs"
        )

    try:

        # IMPORTANT:
        # RCAOutput expects the complete Knowledge Card.
        return RCAOutput.model_validate(output_data)

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail={
                "message": "Could not reconstruct RCA output",
                "error": str(error)
            }
        )


# =========================================================
# APPROVE REMEDIATION
# =========================================================

@router.post("/{incident_id}/approve")
def approve_remediation(
    incident_id: str,
    request: ApprovalRequest
):

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        # -------------------------------------------------
        # 1. CHECK INCIDENT
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT *
            FROM incidents
            WHERE incident_id = %s;
            """,
            (incident_id,)
        )

        incident = cursor.fetchone()

        if not incident:

            raise HTTPException(
                status_code=404,
                detail="Incident not found"
            )

        # -------------------------------------------------
        # 2. CHECK REMEDIATION PROPOSAL
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT *
            FROM remediation_proposals
            WHERE id = %s
              AND incident_id = %s;
            """,
            (
                request.remediation_id,
                incident_id
            )
        )

        remediation = cursor.fetchone()

        if not remediation:

            raise HTTPException(
                status_code=404,
                detail="Remediation proposal not found"
            )

        # -------------------------------------------------
        # 3. CHECK APPROVAL STATUS
        # -------------------------------------------------

        if remediation["approval_status"] != "PENDING":

            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Remediation is not pending approval",
                    "current_status": remediation["approval_status"]
                }
            )

        # -------------------------------------------------
        # 4. CREATE APPROVAL RECORD
        # -------------------------------------------------

        cursor.execute(
            """
            INSERT INTO approvals (
                incident_id,
                remediation_id,
                decision,
                approved_by,
                reason
            )
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
            """,
            (
                incident_id,
                request.remediation_id,
                "APPROVED",
                request.approved_by,
                request.reason
            )
        )

        approval_id = cursor.fetchone()["id"]

        # -------------------------------------------------
        # 5. UPDATE REMEDIATION APPROVAL STATE
        # -------------------------------------------------

        cursor.execute(
            """
            UPDATE remediation_proposals
            SET
                approval_status = %s,
                approved_by = %s,
                approved_at = NOW()
            WHERE id = %s
              AND incident_id = %s;
            """,
            (
                "APPROVED",
                request.approved_by,
                request.remediation_id,
                incident_id
            )
        )

        # -------------------------------------------------
        # 6. AUDIT APPROVAL
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
            VALUES (%s, %s, %s, %s, %s);
            """,
            (
                incident_id,
                "REMEDIATION_APPROVED",
                request.approved_by,
                "approval_api",
                json.dumps(
                    {
                        "approval_id": approval_id,
                        "remediation_id": request.remediation_id
                    }
                )
            )
        )

        # -------------------------------------------------
        # 7. UPDATE INCIDENT STATUS
        # -------------------------------------------------

        cursor.execute(
            """
            UPDATE incidents
            SET status = %s
            WHERE incident_id = %s;
            """,
            (
                "REMEDIATION_APPROVED",
                incident_id
            )
        )

        connection.commit()

        # -------------------------------------------------
        # 8. LOAD RCA
        # -------------------------------------------------

        rca_output = load_rca_output(
            cursor,
            incident_id
        )

        # -------------------------------------------------
        # 9. RUN TASK 5 + TASK 6
        # -------------------------------------------------

        try:

            result = pira_orchestrator.run_after_approval(
                rca_output=rca_output,
                decision=ApprovalDecision.APPROVED,
                feedback=request.reason
            )

        except Exception as execution_error:

            connection.rollback()

            cursor.execute(
                """
                UPDATE remediation_proposals
                SET execution_status = %s
                WHERE id = %s
                  AND incident_id = %s;
                """,
                (
                    "FAILED",
                    request.remediation_id,
                    incident_id
                )
            )

            cursor.execute(
                """
                UPDATE incidents
                SET status = %s
                WHERE incident_id = %s;
                """,
                (
                    "REMEDIATION_FAILED",
                    incident_id
                )
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
                VALUES (%s, %s, %s, %s, %s);
                """,
                (
                    incident_id,
                    "REMEDIATION_FAILED",
                    "PIRA",
                    "approval_api",
                    json.dumps(
                        {
                            "error": str(execution_error)
                        }
                    )
                )
            )

            connection.commit()

            raise HTTPException(
                status_code=500,
                detail={
                    "message": "Approved remediation failed",
                    "error": str(execution_error)
                }
            )

        # -------------------------------------------------
        # 10. EXTRACT TASK 5 + TASK 6 RESULTS
        # -------------------------------------------------

        task5_result = result.get(
            "task5",
            {}
        )

        task6_result = result.get(
            "task6",
            {} 
        )

        # -------------------------------------------------
        # TASK 5 STATUS
        # -------------------------------------------------

        task5_status = task5_result.get(
            "status",
            task5_result.get(
                "execution_status",
                "SUCCESS"
            )
        )

        execution_result = serialize_object(
            task5_result
        )

        # -------------------------------------------------
        # 11. SAVE REMEDIATION EXECUTION
        # -------------------------------------------------

        cursor.execute(
            """
            INSERT INTO remediation_executions (
                incident_id,
                remediation_id,
                execution_status,
                started_at,
                completed_at,
                execution_result,
                executed_by
            )
            VALUES (
                %s,
                %s,
                %s,
                NOW(),
                NOW(),
                %s,
                %s
            )
            RETURNING id;
            """,
            (
                incident_id,
                request.remediation_id,
                str(task5_status),
                json.dumps(execution_result),
                "PIRA"
            )
        )

        execution_id = cursor.fetchone()["id"]

        # -------------------------------------------------
        # 12. UPDATE REMEDIATION PROPOSAL
        # -------------------------------------------------

        cursor.execute(
            """
            UPDATE remediation_proposals
            SET
                execution_status = %s,
                execution_result = %s
            WHERE id = %s
              AND incident_id = %s;
            """,
            (
                str(task5_status),
                json.dumps(execution_result),
                request.remediation_id,
                incident_id
            )
        )

        # -------------------------------------------------
        # 13. AUDIT EXECUTION
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
            VALUES (%s, %s, %s, %s, %s);
            """,
            (
                incident_id,
                "REMEDIATION_EXECUTED",
                "PIRA",
                "execution_api",
                json.dumps(
                    {
                        "execution_id": execution_id,
                        "remediation_id": request.remediation_id,
                        "status": task5_status
                    }
                )
            )
        )

        # =================================================
        # 14. TASK 6 VERIFICATION
        # =================================================

        # Task 6 returns a Knowledge Card.
        #
        # Structure:
        #
        # task6_result
        #   ├── schema_version
        #   ├── incident_id
        #   ├── ...
        #   ├── status
        #   └── payload
        #        └── verification
        #             ├── status
        #             ├── service_recovered
        #             └── recommended_next_step
        #
        # Therefore we MUST read the nested verification
        # payload.

        verification_payload = (
            task6_result
            .get("payload", {})
            .get("verification", {})
        )

        verification_status = verification_payload.get(
            "status",
            task6_result.get(
                "status",
                "FAILED"
            )
        )

        service_recovered = verification_payload.get(
            "service_recovered",
            False
        )

        verification_details = serialize_object(
            task6_result
        )

        recommended_next_step = verification_payload.get(
            "recommended_next_step",
            "INVESTIGATE"
        )

        # -------------------------------------------------
        # 15. SAVE VERIFICATION RESULT
        # -------------------------------------------------

        cursor.execute(
            """
            INSERT INTO verification_results (
                incident_id,
                execution_id,
                verification_status,
                service_recovered,
                verification_details,
                recommended_next_step,
                verified_at
            )
            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                NOW()
            )
            RETURNING id;
            """,
            (
                incident_id,
                execution_id,
                str(verification_status),
                bool(service_recovered),
                json.dumps(verification_details),
                recommended_next_step
            )
        )

        verification_id = cursor.fetchone()["id"]

        # -------------------------------------------------
        # 16. FINAL INCIDENT STATUS
        # -------------------------------------------------

        final_status = (
            "VERIFIED"
            if service_recovered
            else "VERIFICATION_FAILED"
        )

        cursor.execute(
            """
            UPDATE incidents
            SET status = %s
            WHERE incident_id = %s;
            """,
            (
                final_status,
                incident_id
            )
        )

        # -------------------------------------------------
        # 17. SAVE TASK 5 AGENT RUN
        # -------------------------------------------------

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
            VALUES (%s, %s, %s, %s, %s, %s);
            """,
            (
                incident_id,
                "TASK5_REMEDIATION",
                "REMEDIATION",
                str(task5_status),
                json.dumps(
                    {
                        "remediation_id": request.remediation_id,
                        "approval": "APPROVED"
                    }
                ),
                json.dumps(
                    serialize_object(task5_result)
                )
            )
        )

        # -------------------------------------------------
        # 18. SAVE TASK 6 AGENT RUN
        # -------------------------------------------------

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
            VALUES (%s, %s, %s, %s, %s, %s);
            """,
            (
                incident_id,
                "TASK6_VERIFICATION",
                "VERIFICATION",
                str(verification_status),
                json.dumps(
                    serialize_object(task5_result)
                ),
                json.dumps(
                    serialize_object(task6_result)
                )
            )
        )

        # -------------------------------------------------
        # 19. AUDIT VERIFICATION
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
            VALUES (%s, %s, %s, %s, %s);
            """,
            (
                incident_id,
                "VERIFICATION_COMPLETED",
                "TASK6",
                "verification_api",
                json.dumps(
                    {
                        "verification_id": verification_id,
                        "status": verification_status,
                        "service_recovered": service_recovered,
                        "final_status": final_status
                    }
                )
            )
        )

        # -------------------------------------------------
        # 20. COMMIT EVERYTHING
        # -------------------------------------------------

        connection.commit()

        # -------------------------------------------------
        # 21. FINAL RESPONSE
        # -------------------------------------------------

        return {
            "incident_id": incident_id,

            "approval": {
                "approval_id": approval_id,
                "remediation_id": request.remediation_id,
                "decision": "APPROVED",
                "approved_by": request.approved_by
            },

            "remediation": {
                "execution_id": execution_id,
                "status": task5_status,
                "result": serialize_object(
                    task5_result
                )
            },

            "verification": {
                "verification_id": verification_id,
                "status": verification_status,
                "service_recovered": service_recovered,
                "recommended_next_step": recommended_next_step
            },

            "final_status": final_status
        }

    except HTTPException:
        raise

    except Exception as error:

        if connection:
            connection.rollback()

        raise HTTPException(
            status_code=500,
            detail={
                "message": "Approval/execution pipeline failed",
                "incident_id": incident_id,
                "error": str(error)
            }
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# REJECT REMEDIATION
# =========================================================

@router.post("/{incident_id}/reject")
def reject_remediation(
    incident_id: str,
    request: RejectRequest
):

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        # -------------------------------------------------
        # 1. CHECK INCIDENT
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT incident_id
            FROM incidents
            WHERE incident_id = %s;
            """,
            (incident_id,)
        )

        if not cursor.fetchone():

            raise HTTPException(
                status_code=404,
                detail="Incident not found"
            )

        # -------------------------------------------------
        # 2. CHECK REMEDIATION
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT *
            FROM remediation_proposals
            WHERE id = %s
              AND incident_id = %s;
            """,
            (
                request.remediation_id,
                incident_id
            )
        )

        remediation = cursor.fetchone()

        if not remediation:

            raise HTTPException(
                status_code=404,
                detail="Remediation proposal not found"
            )

        # -------------------------------------------------
        # 3. CHECK PENDING STATUS
        # -------------------------------------------------

        if remediation["approval_status"] != "PENDING":

            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Remediation is not pending approval",
                    "current_status": remediation[
                        "approval_status"
                    ]
                }
            )

        # -------------------------------------------------
        # 4. SAVE REJECTION
        # -------------------------------------------------

        cursor.execute(
            """
            INSERT INTO approvals (
                incident_id,
                remediation_id,
                decision,
                approved_by,
                reason
            )
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
            """,
            (
                incident_id,
                request.remediation_id,
                "REJECTED",
                request.rejected_by,
                request.reason
            )
        )

        approval_id = cursor.fetchone()["id"]

        # -------------------------------------------------
        # 5. UPDATE PROPOSAL
        # -------------------------------------------------

        cursor.execute(
            """
            UPDATE remediation_proposals
            SET approval_status = %s
            WHERE id = %s
              AND incident_id = %s;
            """,
            (
                "REJECTED",
                request.remediation_id,
                incident_id
            )
        )

        # -------------------------------------------------
        # 6. UPDATE INCIDENT
        # -------------------------------------------------

        cursor.execute(
            """
            UPDATE incidents
            SET status = %s
            WHERE incident_id = %s;
            """,
            (
                "REMEDIATION_REJECTED",
                incident_id
            )
        )

        # -------------------------------------------------
        # 7. AUDIT REJECTION
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
            VALUES (%s, %s, %s, %s, %s);
            """,
            (
                incident_id,
                "REMEDIATION_REJECTED",
                request.rejected_by,
                "approval_api",
                json.dumps(
                    {
                        "approval_id": approval_id,
                        "remediation_id": request.remediation_id,
                        "reason": request.reason
                    }
                )
            )
        )

        connection.commit()

        return {
            "incident_id": incident_id,
            "approval_id": approval_id,
            "remediation_id": request.remediation_id,
            "decision": "REJECTED",
            "status": "REMEDIATION_REJECTED"
        }

    except HTTPException:
        raise

    except Exception as error:

        if connection:
            connection.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()