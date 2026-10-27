# backend/api/execution.py

import json

from fastapi import APIRouter, HTTPException

from backend.database.connection import get_connection


router = APIRouter(
    prefix="/api/execution",
    tags=["Execution"],
)


# =========================================================
# GET EXECUTION BY INCIDENT
# =========================================================

@router.get(
    "/{incident_id}"
)
def get_execution(
    incident_id: str,
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
        # GET EXECUTIONS
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT *
            FROM remediation_executions
            WHERE incident_id = %s
            ORDER BY id DESC;
            """,
            (
                incident_id,
            ),
        )

        executions = cursor.fetchall()

        return {
            "incident_id":
                incident_id,
            "executions":
                executions,
        }

    except HTTPException:
        raise

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
# GET SINGLE EXECUTION
# =========================================================

@router.get(
    "/{incident_id}/{execution_id}"
)
def get_single_execution(
    incident_id: str,
    execution_id: int,
):

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM remediation_executions
            WHERE id = %s
              AND incident_id = %s;
            """,
            (
                execution_id,
                incident_id,
            ),
        )

        execution = cursor.fetchone()

        if not execution:

            raise HTTPException(
                status_code=404,
                detail="Execution not found",
            )

        return execution

    except HTTPException:
        raise

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