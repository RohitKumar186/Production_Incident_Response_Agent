from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.pipeline import pipeline


router = APIRouter()


class ApprovalRequest(BaseModel):
    feedback: str | None = None


@router.get("/api/incidents")
def list_incidents():
    return pipeline.list_incidents()


@router.post("/api/incidents")
def create_incident():
    return pipeline.generate_and_investigate()


@router.get("/api/incidents/{incident_id}")
def get_incident(incident_id: str):
    try:
        return pipeline.get_incident(incident_id)
    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


@router.get("/api/incidents/{incident_id}/investigation")
def get_investigation(incident_id: str):
    try:
        return pipeline.get_investigation(incident_id)
    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


@router.get("/api/incidents/{incident_id}/evidence")
def get_evidence(incident_id: str):
    try:
        return pipeline.get_evidence(incident_id)
    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


@router.get("/api/incidents/{incident_id}/rca")
def get_rca(incident_id: str):
    try:
        return pipeline.get_rca(incident_id)
    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


@router.get("/api/incidents/{incident_id}/remediation")
def get_remediation(incident_id: str):
    try:
        return pipeline.get_remediation(incident_id)
    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


@router.get("/api/incidents/{incident_id}/verification")
def get_verification(incident_id: str):
    try:
        return pipeline.get_verification(incident_id)
    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


@router.post("/api/incidents/{incident_id}/approve")
def approve_incident(
    incident_id: str,
    request: ApprovalRequest,
):
    try:
        incident = pipeline.get_incident(incident_id)

        # Check whether remediation has actually been
        # persisted for this incident.
        remediation = pipeline.get_remediation(incident_id)

        if remediation.get("status") != "PENDING":
            raise HTTPException(
                status_code=409,
                detail=(
                    "Incident has already been approved "
                    "and remediation has already been processed."
                ),
            )

        # Do not allow approval of an incident that has
        # already reached a terminal state.
        if incident.get("status") in {
            "RESOLVED",
            "REJECTED",
            "VERIFICATION_FAILED",
        }:
            raise HTTPException(
                status_code=409,
                detail=(
                    f"Incident is already in terminal state: "
                    f"{incident.get('status')}"
                ),
            )

        return pipeline.remediate(
            incident_id=incident_id,
            approved=True,
            feedback=request.feedback,
        )

    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


@router.post("/api/incidents/{incident_id}/reject")
def reject_incident(
    incident_id: str,
    request: ApprovalRequest,
):
    try:
        incident = pipeline.get_incident(incident_id)

        if incident.get("status") in {
            "RESOLVED",
            "REJECTED",
            "VERIFICATION_FAILED",
        }:
            raise HTTPException(
                status_code=409,
                detail=(
                    f"Incident is already in terminal state: "
                    f"{incident.get('status')}"
                ),
            )

        return pipeline.remediate(
            incident_id=incident_id,
            approved=False,
            feedback=request.feedback,
        )

    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )