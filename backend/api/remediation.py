from fastapi import APIRouter, HTTPException

from backend.database.connection import get_connection
from backend.schemas.remediation import (
    RemediationCreate,
    RemediationResponse,
)


router = APIRouter(
    prefix="/api/remediation",
    tags=["Remediation"],
)


@router.post("/", response_model=RemediationResponse)
def create_remediation(
    remediation: RemediationCreate,
):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        # Make sure the incident exists
        cursor.execute(
            """
            SELECT incident_id
            FROM incidents
            WHERE incident_id = %s;
            """,
            (remediation.incident_id,),
        )

        incident = cursor.fetchone()

        if incident is None:
            raise HTTPException(
                status_code=404,
                detail="Incident not found",
            )

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
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING
                id,
                incident_id,
                action,
                rationale,
                risk_level,
                proposed_by,
                approval_status,
                approved_by,
                approved_at,
                execution_status,
                execution_result;
            """,
            (
                remediation.incident_id,
                remediation.action,
                remediation.rationale,
                remediation.risk_level,
                remediation.proposed_by,
                "PENDING",
                "NOT_STARTED",
            ),
        )

        result = cursor.fetchone()

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
    response_model=list[RemediationResponse],
)
def get_remediation(incident_id: str):

    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                id,
                incident_id,
                action,
                rationale,
                risk_level,
                proposed_by,
                approval_status,
                approved_by,
                approved_at,
                execution_status,
                execution_result
            FROM remediation_proposals
            WHERE incident_id = %s
            ORDER BY created_at DESC;
            """,
            (incident_id,),
        )

        return cursor.fetchall()

    finally:
        conn.close()