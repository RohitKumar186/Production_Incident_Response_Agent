import json

from fastapi import APIRouter, HTTPException

from backend.database.connection import get_connection
from backend.schemas.verification import (
    VerificationCreate,
    VerificationResponse,
)


router = APIRouter(
    prefix="/api/verifications",
    tags=["Verification"],
)


@router.post("/", response_model=VerificationResponse)
def create_verification(
    verification: VerificationCreate,
):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        # Check incident
        cursor.execute(
            """
            SELECT
                incident_id,
                incident_type,
                severity,
                affected_service,
                title,
                metadata,
                detected_at
            FROM incidents
            WHERE incident_id = %s;
            """,
            (verification.incident_id,),
        )

        incident = cursor.fetchone()

        if incident is None:
            raise HTTPException(
                status_code=404,
                detail="Incident not found",
            )

        # Check execution
        cursor.execute(
            """
            SELECT id
            FROM remediation_executions
            WHERE id = %s
              AND incident_id = %s;
            """,
            (
                verification.execution_id,
                verification.incident_id,
            ),
        )

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail="Execution not found",
            )

        # Save verification
        cursor.execute(
            """
            INSERT INTO verification_results (
                incident_id,
                execution_id,
                verification_status,
                service_recovered,
                verification_details,
                recommended_next_step
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING
                id,
                incident_id,
                execution_id,
                verification_status,
                service_recovered,
                verification_details,
                recommended_next_step,
                verified_at;
            """,
            (
                verification.incident_id,
                verification.execution_id,
                verification.verification_status,
                verification.service_recovered,
                json.dumps(verification.verification_details),
                verification.recommended_next_step,
            ),
        )

        result = cursor.fetchone()

        # Update incident status based on verification
        incident_status = (
            "VERIFIED"
            if verification.service_recovered
            else "FAILED"
        )

        cursor.execute(
            """
            UPDATE incidents
            SET status = %s
            WHERE incident_id = %s;
            """,
            (
                incident_status,
                verification.incident_id,
            ),
        )

        # Agent run
        cursor.execute(
            """
            INSERT INTO agent_runs (
                incident_id,
                agent_name,
                stage,
                status,
                input_data,
                output_data,
                completed_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP);
            """,
            (
                verification.incident_id,
                "VERIFICATION_AGENT",
                "VERIFICATION",
                verification.verification_status,
                json.dumps({
                    "execution_id": verification.execution_id,
                }),
                json.dumps({
                    "service_recovered": verification.service_recovered,
                    "verification_details":
                        verification.verification_details,
                    "recommended_next_step":
                        verification.recommended_next_step,
                }),
            ),
        )

        # Audit log
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
                verification.incident_id,
                "VERIFICATION_COMPLETED",
                "VERIFICATION_AGENT",
                "verification_api",
                json.dumps({
                    "execution_id": verification.execution_id,
                    "verification_status":
                        verification.verification_status,
                    "service_recovered":
                        verification.service_recovered,
                }),
            ),
        )

        # Move recovered incident to historical incidents
        if verification.service_recovered:

            cursor.execute(
                """
                SELECT root_cause
                FROM rca_results
                WHERE incident_id = %s
                ORDER BY created_at DESC
                LIMIT 1;
                """,
                (verification.incident_id,),
            )

            rca = cursor.fetchone()

            root_cause = (
                rca["root_cause"]
                if rca
                else None
            )

            cursor.execute(
                """
                INSERT INTO historical_incidents (
                    incident_id,
                    incident_type,
                    severity,
                    affected_service,
                    title,
                    root_cause,
                    resolution,
                    metadata,
                    occurred_at
                )
                VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s
                );
                """,
                (
                    incident["incident_id"],
                    incident["incident_type"],
                    incident["severity"],
                    incident["affected_service"],
                    incident["title"],
                    root_cause,
                    "Service recovered successfully",
                    json.dumps(incident["metadata"]),
                    incident["detected_at"],
                ),
            )

        conn.commit()

        return result

    except HTTPException:
        conn.rollback()
        raise

    except Exception as e:
        conn.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

    finally:
        conn.close()


@router.get(
    "/{incident_id}",
    response_model=list[VerificationResponse],
)
def get_verifications(incident_id: str):

    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                id,
                incident_id,
                execution_id,
                verification_status,
                service_recovered,
                verification_details,
                recommended_next_step,
                verified_at
            FROM verification_results
            WHERE incident_id = %s
            ORDER BY verified_at DESC;
            """,
            (incident_id,),
        )

        return cursor.fetchall()

    finally:
        conn.close()