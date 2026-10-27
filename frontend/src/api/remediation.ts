
import apiClient from './client'

export interface RemediationPayload {
  remediation?: {
    action?: string
    action_type?: string
    target?: string
    risk?: string
  }
  approval?: {
    required?: boolean
    status?: string
    feedback?: string
  }
  execution?: {
    status?: string
    message?: string
  }
  verification?: {
    status?: string
    service_recovered?: boolean
    checks?: Record<string, unknown>
    message?: string
    recommended_next_step?: string
  }
  rollback_plan?: {
    description?: string
  }
}

export interface RemediationProposal {
  id?: number
  status?: string
  payload?: RemediationPayload
  incidentId?: string
  incident_id?: string
  schema_version?: string
  correlation_id?: string
  timestamp?: string
  producer?: string
  consumer?: string
  message?: string
  action?: string
  description?: string
  risk?: string
  proposedBy?: string
  createdAt?: string
  approval_status?: string
  execution_status?: string
  rationale?: string
  risk_level?: string
  [key: string]: unknown
}

function normalizeResponse(body: unknown): RemediationProposal {
  let data: any = body

  if (data?.data !== undefined) {
    data = data.data
  }

  if (Array.isArray(data)) {
    data = data[0] ?? {}
  }

  if (!data || typeof data !== 'object') {
    data = {}
  }

  const executionResult = data.execution_result ?? {}
  const resultPayload = executionResult.payload ?? {}
  const payload = data.payload ?? resultPayload
  const remediation = payload.remediation ?? {}

  const approval = payload.approval ?? {
    status: data.approval_status,
    approved_by: data.approved_by,
    approved_at: data.approved_at,
  }

  const execution = payload.execution ?? {
    status: data.execution_status,
    message: executionResult.message ?? executionResult.status,
  }

  const verification = payload.verification ?? {}

  return {
    ...data,
    payload: {
      ...payload,
      remediation: {
        ...remediation,
        action: remediation.action ?? data.action,
        risk: remediation.risk ?? data.risk_level,
      },
      approval,
      execution,
      verification,
    },
    action:
      data.action ??
      remediation.action ??
      data.recommended_action,
    description:
      data.description ??
      remediation.action ??
      data.recommended_action,
    risk:
      data.risk ??
      data.risk_level ??
      remediation.risk,
    incidentId: data.incidentId ?? data.incident_id,
    incident_id: data.incident_id ?? data.incidentId,
    status:
      data.status ??
      approval.status ??
      data.approval_status ??
      execution.status ??
      data.execution_status ??
      'UNKNOWN',
  }
}

export interface ApprovalResponse extends RemediationProposal {
  decision?: string
  approvedBy?: string
  approvedAt?: string
}

export async function getRemediation(
  incidentId: string,
): Promise<RemediationProposal> {
  const response = await apiClient.get(
    `/api/remediation/${encodeURIComponent(incidentId)}`,
  )

  return normalizeResponse(response.data)
}

async function getActualRemediationId(
  incidentId: string,
): Promise<number> {
  const proposal = await getRemediation(incidentId)
  const id = Number(proposal.id)

  if (!Number.isInteger(id) || id <= 0) {
    throw new Error(
      `No valid remediation proposal ID found for incident ${incidentId}. Check the remediation API response.`,
    )
  }

  return id
}

export async function approveRemediation(
  incidentId: string,
): Promise<ApprovalResponse> {
  const remediationId = await getActualRemediationId(incidentId)

  const response = await apiClient.post(
    `/api/incidents/${encodeURIComponent(incidentId)}/approve`,
    {
      remediation_id: remediationId,
      approved_by: 'Rohit',
      feedback: 'Approved from frontend',
    },
  )

  const result = normalizeResponse(response.data)

  return {
    ...result,
    incidentId,
    decision:
      (result.decision as string | undefined) ??
      result.payload?.approval?.status ??
      'APPROVED',
    message:
      result.message ??
      result.payload?.execution?.message ??
      'Remediation approved successfully.',
  }
}

export async function rejectRemediation(
  incidentId: string,
): Promise<ApprovalResponse> {
  const remediationId = await getActualRemediationId(incidentId)

  const response = await apiClient.post(
    `/api/incidents/${encodeURIComponent(incidentId)}/reject`,
    {
      remediation_id: remediationId,
      rejected_by: 'Rohit',
      reason: 'Rejected from frontend',
    },
  )

  const result = normalizeResponse(response.data)

  return {
    ...result,
    incidentId,
    decision:
      (result.decision as string | undefined) ??
      result.payload?.approval?.status ??
      'REJECTED',
    message:
      result.message ??
      result.payload?.approval?.feedback ??
      'Remediation rejected.',
  }
}
