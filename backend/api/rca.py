
import json
from typing import Any

from fastapi import APIRouter, HTTPException

from backend.database.connection import get_connection
from backend.schemas.rca import RCACreate, RCAResponse

router = APIRouter(prefix="/api/rca", tags=["RCA"])


def serialize_value(value: Any) -> Any:
    """Convert database JSON values into API-safe Python values."""
    if isinstance(value, str):
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value
    return value


def serialize_rca(row: Any) -> dict:
    """Normalize RCA data for the API response."""
    data = dict(row)

    data["root_cause"] = serialize_value(data.get("root_cause"))

    factors = serialize_value(data.get("contributing_factors"))

    if factors is None:
        factors = []
    elif isinstance(factors, dict):
        factors = [factors]
    elif not isinstance(factors, list):
        factors = [factors]

    data["contributing_factors"] = factors

    return data



@router.post("/", response_model=RCAResponse)
def create_rca(rca: RCACreate):
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT incident_id FROM incidents WHERE incident_id = %s;",
            (rca.incident_id,),
        )

        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Incident not found")

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
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING
                id, incident_id, root_cause, confidence,
                contributing_factors, recommended_action, status;
            """,
            (
                rca.incident_id,
                rca.root_cause,
                rca.confidence,
                json.dumps(rca.contributing_factors),
                rca.recommended_action,
                "COMPLETED",
            ),
        )

        result = serialize_rca(cursor.fetchone())

        cursor.execute(
            """
            INSERT INTO agent_runs (
                incident_id, agent_name, stage, status,
                input_data, output_data, completed_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP);
            """,
            (
                rca.incident_id,
                "RCA_AGENT",
                "RCA",
                "SUCCESS",
                json.dumps({}),
                json.dumps({
                    "root_cause": rca.root_cause,
                    "confidence": rca.confidence,
                    "contributing_factors": rca.contributing_factors,
                    "recommended_action": rca.recommended_action,
                }),
            ),
        )

        cursor.execute(
            """
            INSERT INTO audit_logs (
                incident_id, action, actor, component, details
            )
            VALUES (%s, %s, %s, %s, %s);
            """,
            (
                rca.incident_id,
                "RCA_COMPLETED",
                "RCA_AGENT",
                "rca_api",
                json.dumps({
                    "root_cause": rca.root_cause,
                    "confidence": rca.confidence,
                    "recommended_action": rca.recommended_action,
                }),
            ),
        )

        conn.commit()
        return result

    except HTTPException:
        if conn:
            conn.rollback()
        raise

    except Exception as exc:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=str(exc))

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@router.get("/{incident_id}", response_model=list[RCAResponse])
def get_rca_results(incident_id: str):
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                id, incident_id, root_cause, confidence,
                contributing_factors, recommended_action, status
            FROM rca_results
            WHERE incident_id = %s
            ORDER BY created_at DESC, id DESC;
            """,
            (incident_id,),
        )

        rows = cursor.fetchall()
        return [serialize_rca(row) for row in rows]

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
