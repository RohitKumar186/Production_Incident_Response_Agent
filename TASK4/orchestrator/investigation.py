from dataclasses import asdict
from datetime import datetime, timezone

from TASK4.models.schemas import RCAOutput
from TASK4.rag.retriever import retrieve
from TASK4.rca.analyzer import analyze


def run_rca(investigation_card):
    """
    Consume Task 2 aggregated investigation output
    and produce Task 4 RCA output.
    """

    print("\n" + "=" * 60)
    print("TASK 4 - RAG + ROOT CAUSE ANALYSIS")
    print("=" * 60)

    incident = investigation_card.payload.incident
    findings = investigation_card.payload.findings

    print(f"Incident ID : {incident.incident_id}")
    print(f"Service     : {incident.service['name']}")
    print(f"Findings    : {len(findings)}")

    # ---------------------------------
    # Build RAG query
    # ---------------------------------

    query_parts = [
        incident.symptom.get("description", ""),
    ]

    for finding in findings:
        query_parts.append(finding.finding)
        query_parts.append(finding.category)

    query = " ".join(query_parts)

    print("\n[RAG] Retrieving relevant knowledge...")

    rag_context = retrieve(query, top_k=3)

    print(f"[RAG] Retrieved: {len(rag_context)} sources")

    for context in rag_context:
        print(
            f"  - {context.source_id}: "
            f"{context.title} "
            f"(score={context.relevance_score})"
        )

    # ---------------------------------
    # RCA
    # ---------------------------------

    print("\n[RCA] Analyzing investigation evidence...")

    (
        root_cause,
        supporting_evidence,
        recommended_action,
        target_version,
        rollback_plan,
    ) = analyze(
        findings=findings,
        incident=incident,
        rag_context=rag_context,
    )

    print(f"\nRoot Cause : {root_cause.description}")
    print(f"Category   : {root_cause.category}")
    print(f"Confidence : {root_cause.confidence}")

    print(
        f"Recommended Action : "
        f"{recommended_action.action}"
    )

    # ---------------------------------
    # Output
    # ---------------------------------

    payload = {
        # Task4Incident is a dataclass, not a Pydantic model.
        # Therefore use asdict() instead of model_dump().
        "incident": asdict(incident),

        "root_cause": root_cause.model_dump(),

        "supporting_evidence": [
            evidence.model_dump()
            for evidence in supporting_evidence
        ],

        "rag_context": [
            context.model_dump()
            for context in rag_context
        ],

        "recommended_action": recommended_action.model_dump(),

        "target_version": target_version,

        "rollback_plan": rollback_plan.model_dump(),
    }

    output = RCAOutput(
        schema_version="1.0",
        incident_id=investigation_card.incident_id,
        correlation_id=(
            f"{investigation_card.incident_id}-RCA-001"
        ),
        timestamp=datetime.now(timezone.utc).isoformat(),
        producer="rca",
        consumer="remediation",
        status="SUCCESS",
        payload=payload,
    )

    print("\nTASK 4 STATUS: SUCCESS")
    print("=" * 60)

    return output