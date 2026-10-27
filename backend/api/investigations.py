import json

from fastapi import APIRouter, HTTPException

from backend.database.connection import get_connection
from backend.schemas.investigation import (
    InvestigationCreate,
    InvestigationResponse,
)


router = APIRouter(
    prefix="/api/investigations",
    tags=["Investigations"],
)


@router.post("/", response_model=InvestigationResponse)
def create_investigation(
    investigation: InvestigationCreate,
):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT incident_id
            FROM incidents
            WHERE incident_id = %s;
            """,
            (investigation.incident_id,),
        )

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail="Incident not found",
            )

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
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING
                id,
                incident_id,
                investigator,
                summary,
                findings,
                evidence,
                status;
            """,
            (
                investigation.incident_id,
                investigation.investigator,
                investigation.summary,
                json.dumps(investigation.findings),
                json.dumps(investigation.evidence),
                "COMPLETED",
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


# ---------------------------------------------------------
# EXISTING INVESTIGATION API
# ---------------------------------------------------------

@router.get("/{incident_id}")
def get_investigations(incident_id: str):

    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                id,
                incident_id,
                investigator,
                summary,
                findings,
                evidence,
                status,
                created_at
            FROM investigations
            WHERE incident_id = %s
            ORDER BY created_at DESC;
            """,
            (incident_id,),
        )

        results = cursor.fetchall()

        if not results:
            raise HTTPException(
                status_code=404,
                detail="Investigation not found",
            )

        return {
            "incident_id": incident_id,
            "investigations": results,
        }

    finally:
        conn.close()


# ---------------------------------------------------------
# ARCHITECTURE CONTRACT
# GET /api/incidents/{id}/investigation
# ---------------------------------------------------------

@router.get("/incident/{incident_id}")
def get_incident_investigation(incident_id: str):

    conn = get_connection()

    try:
        cursor = conn.cursor()

        # Check incident
        cursor.execute(
            """
            SELECT incident_id
            FROM incidents
            WHERE incident_id = %s;
            """,
            (incident_id,),
        )

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail="Incident not found",
            )

        # Get investigation
        cursor.execute(
            """
            SELECT
                id,
                incident_id,
                investigator,
                summary,
                findings,
                evidence,
                status,
                created_at
            FROM investigations
            WHERE incident_id = %s
            ORDER BY created_at DESC
            LIMIT 1;
            """,
            (incident_id,),
        )

        investigation = cursor.fetchone()

        if investigation is None:
            raise HTTPException(
                status_code=404,
                detail="Investigation not found",
            )

        return {
            "incident_id": incident_id,
            "investigation": investigation,
        }

    finally:
        conn.close()


# ---------------------------------------------------------
# ARCHITECTURE CONTRACT
# GET /api/incidents/{id}/evidence
# ---------------------------------------------------------

@router.get("/incident/{incident_id}/evidence")
def get_incident_evidence(incident_id: str):

    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT incident_id
            FROM incidents
            WHERE incident_id = %s;
            """,
            (incident_id,),
        )

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail="Incident not found",
            )

        cursor.execute(
            """
            SELECT
                id,
                incident_id,
                investigation_id,
                evidence_type,
                source,
                description,
                data,
                collected_at
            FROM evidence
            WHERE incident_id = %s
            ORDER BY collected_at DESC;
            """,
            (incident_id,),
        )

        return {
            "incident_id": incident_id,
            "evidence": cursor.fetchall(),
        }

    finally:
        conn.close()