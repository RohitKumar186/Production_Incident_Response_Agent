import {
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import {
  AlertCircle,
  ArrowLeft,
  CheckCircle2,
  FileText,
  GitBranch,
  Loader2,
  Server,
  ShieldCheck,
  XCircle,
} from 'lucide-react'
import { useNavigate, useParams } from 'react-router-dom'

import InvestigationPanel from '../components/investigation/InvestigationPanel'

import { getIncident } from '../api/incidents'
import {
  getIncidentEvidence,
  getInvestigation,
} from '../api/investigation'
import { getRCA } from '../api/rca'
import {
  approveRemediation,
  getRemediation,
  rejectRemediation,
} from '../api/remediation'
import { getVerification } from '../api/verification'

import { incidents as mockIncidents } from '../mock/incidents'
import { getIncidentWorkflow } from '../mock/incidentWorkflows'

import type {
  Incident,
  IncidentSeverity,
} from '../types/incident'

import type {
  IncidentWorkflow,
  WorkflowItemStatus,
} from '../mock/incidentWorkflows'

import './IncidentDetails.css'

interface ApiState {
  investigation?: unknown
  evidence?: unknown
  rca?: unknown
  remediation?: unknown
  verification?: unknown
}

function getSeverityClass(
  severity: IncidentSeverity,
) {
  return `severity-${severity}`
}

function normalizeStatus(
  value: unknown,
): string {
  return String(value ?? '')
    .trim()
    .toLowerCase()
}

function isSuccess(value: unknown) {
  const status = normalizeStatus(value)

  return (
    status === 'success' ||
    status === 'completed' ||
    status === 'approved' ||
    status === 'resolved'
  )
}

function mapWorkflowStatus(
  value: unknown,
): WorkflowItemStatus {
  const status = normalizeStatus(value)

  if (
    status === 'success' ||
    status === 'completed' ||
    status === 'approved' ||
    status === 'resolved'
  ) {
    return 'completed'
  }

  if (
    status === 'active' ||
    status === 'in_progress' ||
    status === 'running' ||
    status === 'pending_approval' ||
    status === 'awaiting_approval'
  ) {
    return 'active'
  }

  return 'pending'
}

function getConfidenceText(
  confidence: unknown,
  fallback = 'Not available',
) {
  if (typeof confidence !== 'number') {
    return fallback
  }

  const percentage =
    confidence <= 1
      ? confidence * 100
      : confidence

  return `${Math.round(percentage)}%`
}

function stringifyValue(
  value: unknown,
  fallback = 'Pending',
): string {
  if (
    value === undefined ||
    value === null ||
    value === ''
  ) {
    return fallback
  }

  if (typeof value === 'string') {
    return value
  }

  if (
    typeof value === 'number' ||
    typeof value === 'boolean'
  ) {
    return String(value)
  }

  try {
    return JSON.stringify(value)
  } catch {
    return fallback
  }
}

function getPayload(
  value: unknown,
): any {
  const data = value as any

  return (
    data?.payload ??
    data?.data?.payload ??
    data?.data ??
    data ??
    {}
  )
}

function getArray(
  value: unknown,
  keys: string[],
): any[] {
  const data = value as any

  for (const key of keys) {
    if (Array.isArray(data?.[key])) {
      return data[key]
    }

    if (
      Array.isArray(
        data?.payload?.[key],
      )
    ) {
      return data.payload[key]
    }

    if (
      Array.isArray(
        data?.data?.[key],
      )
    ) {
      return data.data[key]
    }
  }

  return []
}

function evidenceText(
  item: any,
): string {
  if (typeof item === 'string') {
    return item
  }

  return (
    item?.evidence ??
    item?.finding ??
    item?.description ??
    item?.message ??
    item?.value ??
    item?.result ??
    ''
  )
}

function findEvidenceByCategory(
  evidence: any[],
  category: string,
): string {
  const normalizedCategory =
    category.toLowerCase()

  const matches = evidence.filter(
    (item) => {
      const source = String(
        item?.source ??
          item?.agent ??
          item?.category ??
          item?.type ??
          '',
      ).toLowerCase()

      return source.includes(
        normalizedCategory,
      )
    },
  )

  return matches
    .map(evidenceText)
    .filter(Boolean)
    .join(' ')
}

function formatChecks(
  checks: any,
): string {
  if (!checks) {
    return 'Pending'
  }

  if (
    typeof checks === 'string'
  ) {
    return checks
  }

  if (
    typeof checks === 'object'
  ) {
    return Object.entries(checks)
      .map(
        ([key, value]) =>
          `${key}: ${stringifyValue(value)}`,
      )
      .join(' · ')
  }

  return stringifyValue(checks)
}

function createEmptyWorkflow(
  status: string,
): IncidentWorkflow {
  const normalizedStatus =
    normalizeStatus(status)

  const currentPhase =
    normalizedStatus === 'resolved'
      ? 'resolved'
      : 'investigation'

  return {
    currentPhase,

    investigation: {
      status: 'pending',
      progress: 0,
      completedAgents: 0,
      totalAgents: 4,
      agents: [],
      evidence: {
        logs: 'Pending',
        metrics: 'Pending',
        database: 'Pending',
        network: 'Pending',
      },
      findings: {
        logs: 'Pending',
        metrics: 'Pending',
        database: 'Pending',
        network: 'Pending',
      },
      timeline: [],
    },

    rca: {
      status: 'pending',
      rootCause: 'Pending',
      confidence: 'Not available',
      evidence: 'Pending',
      historicalContext: 'Pending',
      recommendedAction: 'Pending',
    },

    remediation: {
      status: 'pending',
      action: 'Pending',
      risk: 'Not assessed',
      executionState: 'Not started',
      result: 'Pending',
    },

    approval: {
      status: 'pending',
      message: 'Pending',
      approvedBy: '—',
      timestamp: '—',
    },

    verification: {
      status: 'pending',
      recoveryStatus: 'Pending',
      recoveryMetrics: 'Pending',
      result: 'Pending',
      nextStep: 'Pending',
    },
  }
}

function WorkflowStep({
  number,
  title,
  status,
  icon,
}: {
  number: number
  title: string
  status: WorkflowItemStatus
  icon: ReactNode
}) {
  const completed =
    status === 'completed'

  const active =
    status === 'active'

  return (
    <div
      className={`workflow-step workflow-step-${status}`}
    >
      <div className="workflow-step-number">
        {completed ? (
          <CheckCircle2 size={17} />
        ) : active ? (
          <Loader2
            size={17}
            className="spin"
          />
        ) : (
          number
        )}
      </div>

      <div className="workflow-step-icon">
        {icon}
      </div>

      <div className="workflow-step-content">
        <span className="workflow-step-title">
          {title}
        </span>

        <span className="workflow-step-status">
          {completed
            ? 'Completed'
            : active
              ? 'In Progress'
              : 'Pending'}
        </span>
      </div>
    </div>
  )
}

function WorkflowSection({
  title,
  icon,
  status,
  children,
}: {
  title: string
  icon: ReactNode
  status: WorkflowItemStatus
  children: ReactNode
}) {
  return (
    <section className="workflow-section">
      <div className="workflow-section-header">
        <div className="workflow-section-title">
          <span className="workflow-section-icon">
            {icon}
          </span>

          <h2>{title}</h2>
        </div>

        <span
          className={`workflow-section-status ${status}`}
        >
          {status === 'completed'
            ? 'Completed'
            : status === 'active'
              ? 'In Progress'
              : 'Pending'}
        </span>
      </div>

      <div className="workflow-section-body">
        {children}
      </div>
    </section>
  )
}

function DetailItem({
  label,
  value,
}: {
  label: string
  value: ReactNode
}) {
  return (
    <div className="workflow-detail-item">
      <span className="workflow-detail-label">
        {label}
      </span>

      <span className="workflow-detail-value">
        {value}
      </span>
    </div>
  )
}

function buildApiWorkflow(
  baseWorkflow: IncidentWorkflow,
  apiState: ApiState,
): IncidentWorkflow {
  const workflow: IncidentWorkflow = {
    ...baseWorkflow,

    investigation: {
      ...baseWorkflow.investigation,
    },

    rca: {
      ...baseWorkflow.rca,
    },

    remediation: {
      ...baseWorkflow.remediation,
    },

    approval: {
      ...baseWorkflow.approval,
    },

    verification: {
      ...baseWorkflow.verification,
    },
  }

  /*
   * =========================================================
   * TASK 2 — INVESTIGATION
   * =========================================================
   */

  const investigation =
    apiState.investigation as any

  const evidenceResponse =
    apiState.evidence as any

  const investigationPayload =
    getPayload(
      investigation,
    )

  const evidence =
    getArray(
      evidenceResponse,
      [
        'evidence',
        'findings',
        'items',
      ],
    ).length > 0
      ? getArray(
          evidenceResponse,
          [
            'evidence',
            'findings',
            'items',
          ],
        )
      : getArray(
          investigationPayload,
          [
            'evidence',
            'findings',
            'items',
          ],
        )

  if (
    apiState.investigation ||
    evidence.length > 0
  ) {
    const investigationStatus =
      normalizeStatus(
        investigation?.status ??
          investigationPayload?.status,
      )

    const completed =
      isSuccess(
        investigationStatus,
      ) ||
      evidence.length > 0

    const logs =
      findEvidenceByCategory(
        evidence,
        'log',
      )

    const metrics =
      findEvidenceByCategory(
        evidence,
        'metric',
      )

    const database =
      findEvidenceByCategory(
        evidence,
        'database',
      )

    const network =
      findEvidenceByCategory(
        evidence,
        'network',
      )

    const fallback = (
      index: number,
    ) =>
      evidence[index]
        ? evidenceText(
            evidence[index],
          )
        : 'Pending'

    workflow.investigation = {
      ...workflow.investigation,

      status: completed
        ? 'completed'
        : mapWorkflowStatus(
              investigationStatus,
            ) === 'active'
          ? 'in_progress'
          : 'pending',

      progress: completed
        ? 100
        : 0,

      completedAgents:
        completed ? 4 : 0,

      totalAgents: 4,

      agents: [
        {
          name: 'Log Analysis Agent',
          detail:
            logs ||
            fallback(0) ||
            'Log analysis completed',
          status: completed
            ? 'completed'
            : 'pending',
        },
        {
          name: 'Metrics Agent',
          detail:
            metrics ||
            fallback(1) ||
            'Metrics analysis completed',
          status: completed
            ? 'completed'
            : 'pending',
        },
        {
          name: 'Database Agent',
          detail:
            database ||
            fallback(2) ||
            'Database analysis completed',
          status: completed
            ? 'completed'
            : 'pending',
        },
        {
          name: 'Network Agent',
          detail:
            network ||
            fallback(3) ||
            'Network analysis completed',
          status: completed
            ? 'completed'
            : 'pending',
        },
      ],

      evidence: {
        logs:
          logs ||
          fallback(0) ||
          workflow.investigation
            .evidence.logs,

        metrics:
          metrics ||
          fallback(1) ||
          workflow.investigation
            .evidence.metrics,

        database:
          database ||
          fallback(2) ||
          workflow.investigation
            .evidence.database,

        network:
          network ||
          fallback(3) ||
          workflow.investigation
            .evidence.network,
      },

      findings: {
        logs:
          logs ||
          fallback(0) ||
          workflow.investigation
            .findings.logs,

        metrics:
          metrics ||
          fallback(1) ||
          workflow.investigation
            .findings.metrics,

        database:
          database ||
          fallback(2) ||
          workflow.investigation
            .findings.database,

        network:
          network ||
          fallback(3) ||
          workflow.investigation
            .findings.network,
      },

      timeline: completed
        ? [
            {
              time: '—',
              title:
                'Investigation completed',
              description:
                'PIRA investigation agents completed evidence collection.',
              state: 'completed',
            },
          ]
        : [],
    }
  }

  /*
   * =========================================================
   * TASK 4 — RCA
   * =========================================================
   */

  if (apiState.rca) {
    const rca =
      apiState.rca as any

    const payload =
      getPayload(rca)

    const rootCause =
      payload?.root_cause

    const supportingEvidence =
      Array.isArray(
        payload?.supporting_evidence,
      )
        ? payload.supporting_evidence
        : []

    const ragContext =
      Array.isArray(
        payload?.rag_context,
      )
        ? payload.rag_context
        : []

    const recommendedAction =
      payload?.recommended_action

    const rootCauseText =
      typeof rootCause === 'string'
        ? rootCause
        : rootCause?.description ??
          rootCause?.name ??
          payload?.rootCause ??
          'Pending'

    const confidence =
      rootCause?.confidence ??
      payload?.confidence

    const supportingEvidenceText =
      supportingEvidence
        .map(
          (item: any) =>
            evidenceText(item),
        )
        .filter(Boolean)
        .join(' ')

    const historicalContext =
      ragContext
        .map((item: any) => {
          if (
            typeof item === 'string'
          ) {
            return item
          }

          return (
            item?.title ??
            item?.description ??
            item?.source_id ??
            ''
          )
        })
        .filter(Boolean)
        .join(' · ')

    const recommendedActionText =
      typeof recommendedAction ===
      'string'
        ? recommendedAction
        : recommendedAction?.action ??
          recommendedAction?.description ??
          'Pending'

    const rcaStatus =
      mapWorkflowStatus(
        rca?.status ??
          payload?.status,
      )

    workflow.rca = {
      ...workflow.rca,

      status: rcaStatus,

      rootCause:
        rootCauseText,

      confidence:
        getConfidenceText(
          confidence,
          workflow.rca.confidence,
        ),

      evidence:
        supportingEvidenceText ||
        'No supporting evidence available.',

      historicalContext:
        historicalContext ||
        'No historical context returned.',

      recommendedAction:
        recommendedActionText,
    }

    if (
      rcaStatus === 'completed'
    ) {
      workflow.remediation = {
        ...workflow.remediation,

        status:
          workflow.remediation.status ===
          'completed'
            ? 'completed'
            : 'active',

        action:
          recommendedActionText,

        executionState:
          workflow.remediation
            .executionState ===
          'Executed successfully'
            ? 'Executed successfully'
            : 'Awaiting human approval',

        result:
          workflow.remediation
            .result === 'Pending'
            ? 'Awaiting human approval.'
            : workflow.remediation
                .result,
      }

      if (
        workflow.remediation
          .status !== 'completed'
      ) {
        workflow.approval = {
          ...workflow.approval,

          status: 'active',

          message:
            'Review the proposed remediation before execution.',
        }
      }
    }
  }

  /*
   * =========================================================
   * TASK 5 + TASK 6 — REMEDIATION
   * =========================================================
   */

  if (apiState.remediation) {
    const remediation =
      apiState.remediation as any

    const payload =
      getPayload(remediation)

    const remediationInfo =
      payload?.remediation ?? {}

    const approval =
      payload?.approval ?? {}

    const execution =
      payload?.execution ?? {}

    const embeddedVerification =
      payload?.verification ?? {}

    const approvalStatus =
      normalizeStatus(
        approval?.status,
      )

    const executionStatus =
      normalizeStatus(
        execution?.status,
      )

    const successfulExecution =
      executionStatus === 'success'

    const approved =
      approvalStatus ===
      'approved'

    const rejected =
      approvalStatus ===
      'rejected'

    workflow.remediation = {
      ...workflow.remediation,

      status:
        successfulExecution
          ? 'completed'
          : approved
            ? 'completed'
            : 'active',

      action:
        remediationInfo?.action ??
        workflow.remediation.action,

      risk:
        remediationInfo?.risk ??
        workflow.remediation.risk,

      executionState:
        successfulExecution
          ? 'Executed successfully'
          : approved
            ? 'Approved'
            : rejected
              ? 'Rejected'
              : 'Awaiting human approval',

      result:
        execution?.message ??
        workflow.remediation.result,
    }

    if (approved) {
      workflow.approval = {
        ...workflow.approval,

        status: 'completed',

        message:
          'Remediation approved successfully.',

        approvedBy:
          'Incident Operator',

        timestamp:
          remediation?.timestamp ??
          workflow.approval.timestamp,
      }
    } else if (rejected) {
      workflow.approval = {
        ...workflow.approval,

        status: 'completed',

        message:
          'Remediation rejected by operator.',

        timestamp:
          remediation?.timestamp ??
          workflow.approval.timestamp,
      }
    } else if (
      remediationInfo?.requires_human_approval !==
      false
    ) {
      workflow.approval = {
        ...workflow.approval,

        status: 'active',

        message:
          'Review the proposed remediation before execution.',
      }
    }

    /*
     * Embedded verification is returned by the
     * backend after successful remediation.
     */
    if (
      embeddedVerification &&
      Object.keys(
        embeddedVerification,
      ).length > 0
    ) {
      const verificationStatus =
        normalizeStatus(
          embeddedVerification.status,
        )

      workflow.verification = {
        ...workflow.verification,

        status:
          isSuccess(
            verificationStatus,
          )
            ? 'completed'
            : 'active',

        recoveryStatus:
          embeddedVerification
            .service_recovered
            ? 'Recovered'
            : 'Not recovered',

        recoveryMetrics:
          formatChecks(
            embeddedVerification.checks,
          ),

        result:
          embeddedVerification.message ??
          'Verification pending.',

        nextStep:
          embeddedVerification.recommended_next_step ??
          'Pending',
      }
    }
  }

  /*
   * =========================================================
   * TASK 6 — VERIFICATION ENDPOINT
   * =========================================================
   */

  if (apiState.verification) {
    const verification =
      apiState.verification as any

    const payload =
      getPayload(verification)

    const verificationStatus =
      normalizeStatus(
        verification?.status ??
          payload?.status,
      )

    const serviceRecovered =
      payload?.service_recovered ??
      verification?.service_recovered

    workflow.verification = {
      ...workflow.verification,

      status:
        isSuccess(
          verificationStatus,
        ) || serviceRecovered
          ? 'completed'
          : mapWorkflowStatus(
                verificationStatus,
              ),

      recoveryStatus:
        serviceRecovered === true
          ? 'Recovered'
          : serviceRecovered === false
            ? 'Not recovered'
            : workflow.verification
                .recoveryStatus,

      recoveryMetrics:
        formatChecks(
          payload?.checks ??
            verification?.checks,
        ),

      result:
        payload?.message ??
        verification?.message ??
        workflow.verification
          .result,

      nextStep:
        payload?.recommended_next_step ??
        verification?.recommended_next_step ??
        workflow.verification
          .nextStep,
    }
  }

  /*
   * Determine the current overall phase.
   */
  if (
    workflow.verification.status ===
    'completed'
  ) {
    workflow.currentPhase =
      'resolved'
  } else if (
    workflow.approval.status ===
    'active'
  ) {
    workflow.currentPhase =
      'approval'
  } else if (
    workflow.remediation.status ===
    'active'
  ) {
    workflow.currentPhase =
      'remediation'
  } else if (
    workflow.rca.status ===
    'completed'
  ) {
    workflow.currentPhase =
      'remediation'
  } else if (
    workflow.investigation.status ===
    'completed'
  ) {
    workflow.currentPhase =
      'rca'
  } else {
    workflow.currentPhase =
      'investigation'
  }

  return workflow
}

export default function IncidentDetails() {
  const {
    incidentId: routeIncidentId,
  } = useParams<{
    incidentId: string
  }>()

  const navigate = useNavigate()

  const [incident, setIncident] =
    useState<
      Incident | undefined
    >()

  const [baseWorkflow, setBaseWorkflow] =
    useState<
      IncidentWorkflow | undefined
    >()

  const [apiState, setApiState] =
    useState<ApiState>({})

  const [loading, setLoading] =
    useState(true)

  const [apiError, setApiError] =
    useState<string | null>(null)

  const [approvalLoading, setApprovalLoading] =
    useState(false)

  const [approvalDecision, setApprovalDecision] =
    useState<
      'approved' | 'rejected' | null
    >(null)

  const [approvalError, setApprovalError] =
    useState<string | null>(null)

  async function loadBackendData(
    incidentId: string,
  ) {
    const results =
      await Promise.allSettled([
        getInvestigation(
          incidentId,
        ),

        getIncidentEvidence(
          incidentId,
        ),

        getRCA(
          incidentId,
        ),

        getRemediation(
          incidentId,
        ),

        getVerification(
          incidentId,
        ),
      ])

    const nextState: ApiState =
      {}

    if (
      results[0].status ===
      'fulfilled'
    ) {
      nextState.investigation =
        results[0].value
    }

    if (
      results[1].status ===
      'fulfilled'
    ) {
      nextState.evidence =
        results[1].value
    }

    if (
      results[2].status ===
      'fulfilled'
    ) {
      nextState.rca =
        results[2].value
    }

    if (
      results[3].status ===
      'fulfilled'
    ) {
      nextState.remediation =
        results[3].value
    }

    if (
      results[4].status ===
      'fulfilled'
    ) {
      nextState.verification =
        results[4].value
    }

    setApiState(nextState)

    return nextState
  }

  useEffect(() => {
    if (!routeIncidentId) {
      setLoading(false)
      return
    }

    let cancelled = false

    async function loadIncident() {
      setLoading(true)
      setApiError(null)
      setApiState({})
      setApprovalDecision(null)
      setApprovalError(null)

      const localIncident =
        mockIncidents.find(
          (item) =>
            item.id ===
            routeIncidentId,
        )

      /*
       * Local mock fallback.
       */
      if (localIncident) {
        setIncident(
          localIncident,
        )

        setBaseWorkflow(
          getIncidentWorkflow(
            routeIncidentId!,
            localIncident.status,
          ),
        )
      }

      try {
        /*
         * This is the important part:
         * real backend incident becomes the
         * source of truth.
         */
        const apiIncident =
          await getIncident(
            routeIncidentId!,
          )

        if (cancelled) {
          return
        }

        setIncident(
          apiIncident,
        )

        /*
         * DO NOT call getIncidentWorkflow()
         * for backend-generated incidents.
         *
         * It only contains mock incidents.
         */
        setBaseWorkflow(
          localIncident
            ? getIncidentWorkflow(
                routeIncidentId!,
                apiIncident.status,
              )
            : createEmptyWorkflow(
                apiIncident.status,
              ),
        )

        await loadBackendData(
          routeIncidentId!,
        )
      } catch {
        if (cancelled) {
          return
        }

        /*
         * If the backend is unavailable,
         * retain the local mock workflow.
         */
        if (!localIncident) {
          setIncident(undefined)
          setBaseWorkflow(undefined)
        }

        setApiError(
          'Backend API is currently unavailable. Showing local incident data where available.',
        )
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    void loadIncident()

    return () => {
      cancelled = true
    }
  }, [routeIncidentId])

  const displayWorkflow =
    useMemo(() => {
      if (!baseWorkflow) {
        return undefined
      }

      return buildApiWorkflow(
        baseWorkflow,
        apiState,
      )
    }, [
      baseWorkflow,
      apiState,
    ])

  async function refreshWorkflow() {
    if (!routeIncidentId) {
      return
    }

    try {
      const nextState =
        await loadBackendData(
          routeIncidentId,
        )

      const remediation =
        nextState.remediation as any

      const payload =
        getPayload(
          remediation,
        )

      const approvalStatus =
        normalizeStatus(
          payload?.approval?.status,
        )

      if (
        approvalStatus ===
        'approved'
      ) {
        setApprovalDecision(
          'approved',
        )
      }

      if (
        approvalStatus ===
        'rejected'
      ) {
        setApprovalDecision(
          'rejected',
        )
      }
    } catch {
      // Individual API failures are already
      // handled by Promise.allSettled().
    }
  }

  async function handleApprove() {
    if (
      !routeIncidentId ||
      approvalLoading
    ) {
      return
    }

    setApprovalLoading(true)
    setApprovalError(null)

    try {
      await approveRemediation(
        routeIncidentId,
      )

      setApprovalDecision(
        'approved',
      )

      await refreshWorkflow()
    } catch {
      setApprovalError(
        'Unable to approve remediation. Please check the backend connection and try again.',
      )
    } finally {
      setApprovalLoading(false)
    }
  }

  async function handleReject() {
    if (
      !routeIncidentId ||
      approvalLoading
    ) {
      return
    }

    setApprovalLoading(true)
    setApprovalError(null)

    try {
      await rejectRemediation(
        routeIncidentId,
      )

      setApprovalDecision(
        'rejected',
      )

      await refreshWorkflow()
    } catch {
      setApprovalError(
        'Unable to reject remediation. Please check the backend connection and try again.',
      )
    } finally {
      setApprovalLoading(false)
    }
  }

  if (!routeIncidentId) {
    return (
      <div className="incident-details-page">
        <div className="incident-details-empty">
          <AlertCircle size={32} />

          <h2>
            Incident not specified
          </h2>

          <p>
            The requested incident could
            not be identified.
          </p>

          <button
            type="button"
            onClick={() =>
              navigate('/incidents')
            }
          >
            Back to Incidents
          </button>
        </div>
      </div>
    )
  }

  if (
    loading &&
    !incident
  ) {
    return (
      <div className="incident-details-page">
        <div className="incident-details-loading">
          <Loader2
            size={32}
            className="spin"
          />

          <span>
            Loading incident details...
          </span>
        </div>
      </div>
    )
  }

  if (
    !incident ||
    !displayWorkflow
  ) {
    return (
      <div className="incident-details-page">
        <div className="incident-details-empty">
          <XCircle size={32} />

          <h2>
            Incident not found
          </h2>

          <p>
            No incident with ID{' '}
            <strong>
              {routeIncidentId}
            </strong>{' '}
            was found.
          </p>

          <button
            type="button"
            onClick={() =>
              navigate('/incidents')
            }
          >
            Back to Incidents
          </button>
        </div>
      </div>
    )
  }

  const investigationStatus =
    displayWorkflow.investigation
      .status === 'completed'
      ? 'completed'
      : displayWorkflow.investigation
            .status === 'in_progress'
        ? 'active'
        : 'pending'

  return (
    <div className="incident-details-page">
      <div className="incident-details-header">
        <button
          type="button"
          className="back-button"
          onClick={() =>
            navigate('/incidents')
          }
        >
          <ArrowLeft size={17} />
          Back to Incidents
        </button>

        <div className="incident-header-main">
          <div>
            <div className="incident-id-row">
              <span className="incident-id">
                {incident.id}
              </span>

              <span
                className={`severity-badge ${getSeverityClass(
                  incident.severity,
                )}`}
              >
                {incident.severity}
              </span>

              <span
                className={`status-badge status-${incident.status}`}
              >
                {incident.status.replace(
                  /_/g,
                  ' ',
                )}
              </span>
            </div>

            <h1>
              {incident.title}
            </h1>

            <p className="incident-subtitle">
              {incident.service} ·{' '}
              {incident.type}
            </p>
          </div>
        </div>
      </div>

      {apiError && (
        <div className="api-status-banner">
          <AlertCircle size={18} />

          <span>
            {apiError}
          </span>
        </div>
      )}

      <section className="incident-overview-card">
        <div className="incident-overview-grid">
          <DetailItem
            label="Incident ID"
            value={incident.id}
          />

          <DetailItem
            label="Service"
            value={
              incident.service
            }
          />

          <DetailItem
            label="Incident Type"
            value={
              incident.type
            }
          />

          <DetailItem
            label="Severity"
            value={
              <span
                className={`severity-text ${getSeverityClass(
                  incident.severity,
                )}`}
              >
                {incident.severity}
              </span>
            }
          />

          <DetailItem
            label="Created"
            value={new Date(
              incident.createdAt,
            ).toLocaleString()}
          />

          <DetailItem
            label="Last Updated"
            value={new Date(
              incident.updatedAt,
            ).toLocaleString()}
          />
        </div>
      </section>

      <section className="workflow-progress-card">
        <div className="workflow-progress-header">
          <div>
            <span className="section-eyebrow">
              Incident Response Workflow
            </span>

            <h2>
              {displayWorkflow.currentPhase}
            </h2>
          </div>

          <span className="workflow-progress-label">
            Response workflow
          </span>
        </div>

        <div className="workflow-steps">
          <WorkflowStep
            number={1}
            title="Investigation"
            status={
              investigationStatus
            }
            icon={
              <FileText size={18} />
            }
          />

          <WorkflowStep
            number={2}
            title="Root Cause Analysis"
            status={
              displayWorkflow.rca
                .status
            }
            icon={
              <GitBranch
                size={18}
              />
            }
          />

          <WorkflowStep
            number={3}
            title="Remediation"
            status={
              displayWorkflow
                .remediation
                .status
            }
            icon={
              <Server size={18} />
            }
          />

          <WorkflowStep
            number={4}
            title="Verification"
            status={
              displayWorkflow
                .verification
                .status
            }
            icon={
              <ShieldCheck
                size={18}
              />
            }
          />
        </div>
      </section>

      <div className="incident-workflow-content">
        <WorkflowSection
          title="Investigation"
          icon={
            <FileText size={20} />
          }
          status={
            investigationStatus
          }
        >
          <InvestigationPanel
            workflow={
              displayWorkflow.investigation
            }
          />
        </WorkflowSection>

        <WorkflowSection
          title="Root Cause Analysis"
          icon={
            <GitBranch
              size={20}
            />
          }
          status={
            displayWorkflow.rca
              .status
          }
        >
          <div className="workflow-detail-grid">
            <DetailItem
              label="Root Cause"
              value={
                displayWorkflow.rca
                  .rootCause
              }
            />

            <DetailItem
              label="Confidence"
              value={
                displayWorkflow.rca
                  .confidence
              }
            />

            <DetailItem
              label="Analysis Status"
              value={
                displayWorkflow.rca
                  .status
              }
            />
          </div>

          <div className="workflow-list-block">
            <h3>
              Supporting Evidence
            </h3>

            <p>
              {
                displayWorkflow
                  .rca.evidence
              }
            </p>
          </div>

          <div className="workflow-list-block">
            <h3>
              Historical Context
            </h3>

            <p>
              {
                displayWorkflow
                  .rca
                  .historicalContext
              }
            </p>
          </div>

          <div className="workflow-list-block">
            <h3>
              Recommended Action
            </h3>

            <p>
              {
                displayWorkflow
                  .rca
                  .recommendedAction
              }
            </p>
          </div>
        </WorkflowSection>

        <WorkflowSection
          title="Remediation"
          icon={
            <Server size={20} />
          }
          status={
            displayWorkflow
              .remediation
              .status
          }
        >
          <div className="workflow-detail-grid">
            <DetailItem
              label="Action"
              value={
                displayWorkflow
                  .remediation
                  .action
              }
            />

            <DetailItem
              label="Execution State"
              value={
                displayWorkflow
                  .remediation
                  .executionState
              }
            />

            <DetailItem
              label="Risk"
              value={
                <span className="remediation-risk">
                  {
                    displayWorkflow
                      .remediation
                      .risk
                  }
                </span>
              }
            />

            <DetailItem
              label="Result"
              value={
                displayWorkflow
                  .remediation
                  .result
              }
            />
          </div>
        </WorkflowSection>

        <WorkflowSection
          title="Human Approval"
          icon={
            <ShieldCheck
              size={20}
            />
          }
          status={
            approvalDecision ===
            'approved'
              ? 'completed'
              : approvalDecision ===
                  'rejected'
                ? 'completed'
                : displayWorkflow
                    .approval
                    .status
          }
        >
          <div className="approval-content">
            <div className="workflow-detail-grid">
              <DetailItem
                label="Approval Status"
                value={
                  approvalDecision ??
                  displayWorkflow
                    .approval
                    .status
                }
              />

              <DetailItem
                label="Approver"
                value={
                  displayWorkflow
                    .approval
                    .approvedBy
                }
              />

              <DetailItem
                label="Timestamp"
                value={
                  displayWorkflow
                    .approval
                    .timestamp
                }
              />
            </div>

            <p className="approval-message">
              {
                displayWorkflow
                  .approval
                  .message
              }
            </p>

            {approvalError && (
              <div className="approval-error">
                <AlertCircle
                  size={17}
                />

                <span>
                  {approvalError}
                </span>
              </div>
            )}

            {!approvalDecision &&
  (
    displayWorkflow.approval.status === 'active' ||
    displayWorkflow.approval.status === 'pending' ||
    normalizeStatus(incident.status) === 'awaiting_approval'
  ) && (
                <div className="approval-actions">
                  <button
                    type="button"
                    className="approval-button approval-button-reject"
                    onClick={
                      handleReject
                    }
                    disabled={
                      approvalLoading
                    }
                  >
                    {approvalLoading ? (
                      <Loader2
                        size={17}
                        className="approval-spinner"
                      />
                    ) : (
                      <XCircle
                        size={17}
                      />
                    )}

                    Reject Remediation
                  </button>

                  <button
                    type="button"
                    className="approval-button approval-button-approve"
                    onClick={
                      handleApprove
                    }
                    disabled={
                      approvalLoading
                    }
                  >
                    {approvalLoading ? (
                      <Loader2
                        size={17}
                        className="approval-spinner"
                      />
                    ) : (
                      <CheckCircle2
                        size={17}
                      />
                    )}

                    Approve Remediation
                  </button>
                </div>
              )}

            {approvalDecision ===
              'approved' && (
              <div className="approval-success">
                <CheckCircle2
                  size={18}
                />

                <span>
                  Remediation approved
                  successfully.
                </span>
              </div>
            )}

            {approvalDecision ===
              'rejected' && (
              <div className="approval-rejected">
                <XCircle size={18} />

                <span>
                  Remediation rejected
                  by operator.
                </span>
              </div>
            )}
          </div>
        </WorkflowSection>

        <WorkflowSection
          title="Verification"
          icon={
            <ShieldCheck
              size={20}
            />
          }
          status={
            displayWorkflow
              .verification
              .status
          }
        >
          <div className="workflow-detail-grid">
            <DetailItem
              label="Verification Status"
              value={
                displayWorkflow
                  .verification
                  .status
              }
            />

            <DetailItem
              label="Recovery Status"
              value={
                displayWorkflow
                  .verification
                  .recoveryStatus
              }
            />

            <DetailItem
              label="Recovery Metrics"
              value={
                displayWorkflow
                  .verification
                  .recoveryMetrics
              }
            />

            <DetailItem
              label="Result"
              value={
                displayWorkflow
                  .verification
                  .result
              }
            />

            <DetailItem
              label="Next Step"
              value={
                displayWorkflow
                  .verification
                  .nextStep
              }
            />
          </div>
        </WorkflowSection>
      </div>
    </div>
  )
}