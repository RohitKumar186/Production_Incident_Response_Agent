from typing import List, Dict

from TASK4.models.schemas import (
    RootCause,
    SupportingEvidence,
    RecommendedAction,
    RollbackPlan,
)


# =========================================================
# SUPPORTING EVIDENCE
# =========================================================

def _build_supporting_evidence(findings) -> List[SupportingEvidence]:

    evidence = []

    for finding in findings:
        evidence.append(
            SupportingEvidence(
                finding_id=finding.finding_id,
                source=finding.agent,
                evidence=finding.finding,
                expected_value=finding.expected_value,
                confidence=finding.confidence,
            )
        )

    return evidence


# =========================================================
# HEALTHY FINDING CHECK
# =========================================================

def _is_healthy_finding(finding) -> bool:
    """
    Detect genuinely healthy findings.

    IMPORTANT:
    'abnormal' must NOT be treated as healthy merely
    because it contains the substring 'normal'.
    """

    text = " ".join(
        [
            str(finding.finding),
            str(finding.value),
        ]
    ).lower()

    # Explicit abnormal indicators always mean
    # this is NOT a healthy finding.
    abnormal_words = [
        "abnormal",
        "degraded",
        "slow",
        "timeout",
        "packet loss",
        "error",
        "exception",
        "pressure",
        "high utilization",
        "resource pressure",
    ]

    if any(
        word in text
        for word in abnormal_words
    ):
        return False

    healthy_phrases = [
        "is normal",
        "are normal",
        "within normal range",
        "within normal limits",
        "within expected limits",
        "within expected range",
        "healthy",
        "no abnormal",
        "no slow",
        "no critical",
        "no significant",
        "all observed queries are within",
    ]

    return any(
        phrase in text
        for phrase in healthy_phrases
    )


# =========================================================
# INCIDENT SYMPTOM CATEGORY
# =========================================================

def _detect_incident_category(incident) -> str:
    """
    Determine the primary scenario from the incident symptom.

    Task1 deliberately generates controlled scenarios, so
    this is used as a strong causal signal rather than relying
    only on generic latency evidence.
    """

    symptom = str(
        incident.symptom.get(
            "description",
            ""
        )
    ).lower()

    if any(
        word in symptom
        for word in [
            "database",
            "query",
            "database query",
        ]
    ):
        return "DATABASE"

    if any(
        word in symptom
        for word in [
            "network",
            "packet loss",
            "connectivity",
        ]
    ):
        return "NETWORK"

    if any(
        word in symptom
        for word in [
            "application",
            "http",
            "exception",
            "error rate",
        ]
    ):
        return "APPLICATION"

    if any(
        word in symptom
        for word in [
            "infrastructure",
            "resource utilization",
            "cpu",
            "memory",
        ]
    ):
        return "INFRASTRUCTURE"

    return "UNKNOWN"


# =========================================================
# ROOT CAUSE SCORING
# =========================================================

def _calculate_root_cause_scores(
    findings,
    incident
) -> Dict[str, float]:

    scores = {
        "DATABASE": 0.0,
        "NETWORK": 0.0,
        "APPLICATION": 0.0,
        "INFRASTRUCTURE": 0.0,
    }

    # -----------------------------------------------------
    # Strong signal from controlled incident scenario
    # -----------------------------------------------------

    scenario_category = _detect_incident_category(
        incident
    )

    if scenario_category in scores:
        scores[scenario_category] += 3.0

    # -----------------------------------------------------
    # Evidence scoring
    # -----------------------------------------------------

    for finding in findings:

        if _is_healthy_finding(finding):
            continue

        category = str(
            finding.category
        ).upper()

        text = " ".join(
            [
                str(finding.finding),
                str(finding.value),
                str(finding.evidence),
            ]
        ).lower()

        confidence = float(
            finding.confidence
        )

        # ---------------------------------------------
        # DATABASE
        # ---------------------------------------------

        if category == "DATABASE":

            keywords = [
                "slow",
                "query",
                "database",
                "timeout",
                "execution",
                "lock",
            ]

            matches = sum(
                keyword in text
                for keyword in keywords
            )

            if matches:
                scores["DATABASE"] += (
                    confidence * 2.0
                )

        # ---------------------------------------------
        # NETWORK
        # ---------------------------------------------

        elif category == "NETWORK":

            keywords = [
                "network",
                "packet loss",
                "connectivity",
                "network latency",
                "degraded",
                "abnormal",
            ]

            matches = sum(
                keyword in text
                for keyword in keywords
            )

            if matches:
                scores["NETWORK"] += (
                    confidence * 2.0
                )

        # ---------------------------------------------
        # APPLICATION
        # ---------------------------------------------

        elif category == "APPLICATION":

            keywords = [
                "application",
                "error",
                "exception",
                "http 500",
                "http500",
                "crash",
                "unhandled",
            ]

            matches = sum(
                keyword in text
                for keyword in keywords
            )

            if matches:
                scores["APPLICATION"] += (
                    confidence * 2.0
                )

        # ---------------------------------------------
        # INFRASTRUCTURE
        # ---------------------------------------------

        elif category == "INFRASTRUCTURE":

            keywords = [
                "infrastructure",
                "cpu",
                "memory",
                "resource",
                "utilization",
                "saturation",
                "pressure",
            ]

            matches = sum(
                keyword in text
                for keyword in keywords
            )

            if matches:
                scores["INFRASTRUCTURE"] += (
                    confidence * 2.0
                )

        # ---------------------------------------------
        # LOGS
        # ---------------------------------------------

        elif category == "LOGS":

            if any(
                keyword in text
                for keyword in [
                    "database",
                    "query",
                    "timeout",
                    "slow",
                ]
            ):
                scores["DATABASE"] += (
                    confidence * 1.2
                )

            if any(
                keyword in text
                for keyword in [
                    "network",
                    "packet loss",
                    "connectivity",
                    "network latency",
                ]
            ):
                scores["NETWORK"] += (
                    confidence * 1.2
                )

            if any(
                keyword in text
                for keyword in [
                    "application",
                    "exception",
                    "http 500",
                    "http500",
                    "unhandled",
                    "application error",
                ]
            ):
                scores["APPLICATION"] += (
                    confidence * 1.2
                )

            if any(
                keyword in text
                for keyword in [
                    "infrastructure",
                    "cpu",
                    "memory",
                    "resource",
                    "utilization",
                    "pressure",
                ]
            ):
                scores["INFRASTRUCTURE"] += (
                    confidence * 1.2
                )

        # ---------------------------------------------
        # METRICS
        # ---------------------------------------------

        elif category == "METRICS":

            # Latency confirms the incident but does not
            # independently identify the root cause.
            continue

    return scores


# =========================================================
# ROOT CAUSE DESCRIPTION
# =========================================================

def _get_description(category: str) -> str:

    descriptions = {

        "DATABASE":
            "Database query performance degradation",

        "NETWORK":
            "Network latency and packet loss degradation",

        "APPLICATION":
            "Application errors and latency degradation",

        "INFRASTRUCTURE":
            "Infrastructure resource pressure",

        "UNKNOWN":
            "Root cause could not be determined",
    }

    return descriptions.get(
        category,
        descriptions["UNKNOWN"]
    )


# =========================================================
# RECOMMENDED ACTION
# =========================================================

def _get_recommended_action(
    category: str,
    incident
) -> RecommendedAction:

    service = incident.service.get(
        "name",
        "order-api"
    )

    actions = {

        "DATABASE":
            RecommendedAction(
                action="Optimize the affected database query",
                action_type="DATABASE_REMEDIATION",
                target="orders-db",
                risk="MEDIUM",
                requires_human_approval=True,
            ),

        "NETWORK":
            RecommendedAction(
                action=(
                    "Investigate and restore network "
                    "connectivity and packet loss"
                ),
                action_type="NETWORK_REMEDIATION",
                target="order-api-network",
                risk="HIGH",
                requires_human_approval=True,
            ),

        "APPLICATION":
            RecommendedAction(
                action=(
                    "Investigate and fix the "
                    "application error condition"
                ),
                action_type="APPLICATION_REMEDIATION",
                target=service,
                risk="HIGH",
                requires_human_approval=True,
            ),

        "INFRASTRUCTURE":
            RecommendedAction(
                action=(
                    "Reduce infrastructure "
                    "resource pressure"
                ),
                action_type="INFRASTRUCTURE_REMEDIATION",
                target=service,
                risk="HIGH",
                requires_human_approval=True,
            ),
    }

    return actions.get(
        category,
        RecommendedAction(
            action="Perform additional investigation",
            action_type="INVESTIGATION",
            target=service,
            risk="HIGH",
            requires_human_approval=True,
        ),
    )


# =========================================================
# MAIN ANALYZER
# =========================================================

def analyze(
    findings,
    incident,
    rag_context
):
    """
    Task 4 RCA.

    Returns exactly five values expected by
    TASK4/orchestrator/investigation.py.
    """

    scores = _calculate_root_cause_scores(
        findings,
        incident
    )

    print("\n[RCA] Root cause scores:")

    for category, score in scores.items():
        print(
            f"  {category:<16} {score:.2f}"
        )

    root_cause_category = max(
        scores,
        key=scores.get
    )

    root_cause_score = scores[
        root_cause_category
    ]

    # -----------------------------------------------------
    # UNKNOWN
    # -----------------------------------------------------

    if root_cause_score <= 0:

        root_cause = RootCause(
            description=_get_description(
                "UNKNOWN"
            ),
            category="UNKNOWN",
            confidence=0.0,
        )

        supporting_evidence = (
            _build_supporting_evidence(
                findings
            )
        )

        recommended_action = (
            _get_recommended_action(
                "UNKNOWN",
                incident
            )
        )

        target_version = incident.service.get(
            "version",
            "unknown"
        )

        rollback_plan = RollbackPlan(
            description=(
                "Do not execute remediation until "
                "the root cause is confirmed"
            )
        )

        return (
            root_cause,
            supporting_evidence,
            recommended_action,
            target_version,
            rollback_plan,
        )

    # -----------------------------------------------------
    # Confidence
    # -----------------------------------------------------

    confidence = min(
        0.99,
        max(
            0.50,
            root_cause_score / 4.0
        )
    )

    # -----------------------------------------------------
    # Root Cause
    # -----------------------------------------------------

    root_cause = RootCause(
        description=_get_description(
            root_cause_category
        ),
        category=root_cause_category,
        confidence=round(
            confidence,
            2
        ),
    )

    # -----------------------------------------------------
    # Supporting Evidence
    # -----------------------------------------------------

    supporting_evidence = (
        _build_supporting_evidence(
            findings
        )
    )

    # -----------------------------------------------------
    # Recommended Action
    # -----------------------------------------------------

    recommended_action = (
        _get_recommended_action(
            root_cause_category,
            incident
        )
    )

    # -----------------------------------------------------
    # Target Version
    # -----------------------------------------------------

    target_version = incident.service.get(
        "version",
        "unknown"
    )

    # -----------------------------------------------------
    # Rollback
    # -----------------------------------------------------

    rollback_plan = RollbackPlan(
        description=(
            "Rollback the remediation change "
            "if post-remediation verification fails"
        )
    )

    # -----------------------------------------------------
    # EXACTLY FIVE VALUES
    # -----------------------------------------------------

    return (
        root_cause,
        supporting_evidence,
        recommended_action,
        target_version,
        rollback_plan,
    )