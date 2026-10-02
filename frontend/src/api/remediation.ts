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
  status: string
  payload?: RemediationPayload

  incidentId?: string
  incident_id?: string

  schema_version?: string
  correlation_id?: string
  timestamp?: string
  producer?: string
  consumer?: string

  message?: string

  // Compatibility fields used by the existing UI.
  action?: string
  description?: string
  risk?: string
  proposedBy?: string
  createdAt?: string
}

function normalizeResponse(
  body: RemediationProposal,
): RemediationProposal {
  return {
    ...body,

    payload: body.payload ?? {},

    action:
      body.action ??
      body.payload?.remediation?.action,

    description:
      body.description ??
      body.payload?.remediation?.action,

    risk:
      body.risk ??
      body.payload?.remediation?.risk,

    incidentId:
      body.incidentId ??
      body.incident_id,

    incident_id:
      body.incident_id ??
      body.incidentId,
  }
}

export interface ApprovalResponse
  extends RemediationProposal {
  decision?: string
  approvedBy?: string
  approvedAt?: string
}

export async function getRemediation(
  incidentId: string,
): Promise<RemediationProposal> {
  const response =
    await apiClient.get<RemediationProposal>(
      `/api/incidents/${incidentId}/remediation`,
    )

  return normalizeResponse(
    response.data,
  )
}

export async function approveRemediation(
  incidentId: string,
): Promise<ApprovalResponse> {
  const response =
    await apiClient.post<RemediationProposal>(
      `/api/incidents/${incidentId}/approve`,
      {
        feedback: 'Approved from frontend',
      },
    )

  const result =
    normalizeResponse(
      response.data,
    )

  return {
    ...result,

    incidentId,

    decision:
      result.payload?.approval?.status ??
      'APPROVED',

    message:
      result.payload?.execution?.message ??
      'Remediation approved successfully.',
  }
}

export async function rejectRemediation(
  incidentId: string,
): Promise<ApprovalResponse> {
  const response =
    await apiClient.post<RemediationProposal>(
      `/api/incidents/${incidentId}/reject`,
      {
        feedback: 'Rejected from frontend',
      },
    )

  const result =
    normalizeResponse(
      response.data,
    )

  return {
    ...result,

    incidentId,

    decision:
      result.payload?.approval?.status ??
      'REJECTED',

    message:
      result.payload?.approval?.feedback ??
      'Remediation rejected.',
  }
}