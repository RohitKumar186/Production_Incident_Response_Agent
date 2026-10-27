
import apiClient from './client'

export interface InvestigationResponse {
  incidentId?: string
  status?: string
  summary?: string
  findings?: unknown[]
  evidence?: unknown[]
  startedAt?: string
  completedAt?: string

  // Backend InvestigationCard fields
  incident_id?: string
  timestamp?: string
  incident_type?: string
  affected_component?: string
  technology_stack?: unknown
  observed_symptoms?: unknown
  current_state?: unknown
  producer?: string
  consumer?: string
  schema_version?: string

  [key: string]: unknown
}

function unwrapResponse<T>(responseData: unknown): T {
  let data: any = responseData

  if (data?.data !== undefined) {
    data = data.data
  }

  if (Array.isArray(data)) {
    data = data.length > 0 ? data[0] : {}
  }

  if (data?.payload !== undefined) {
    data = data.payload
  }

  return data as T
}

export async function getInvestigation(
  incidentId: string,
): Promise<InvestigationResponse> {
  const response = await apiClient.get(
    `/api/investigations/${encodeURIComponent(incidentId)}`,
  )

  return unwrapResponse<InvestigationResponse>(response.data)
}

export async function getIncidentEvidence(
  incidentId: string,
): Promise<unknown[]> {
  const response = await apiClient.get(
    `/api/investigations/incident/${encodeURIComponent(incidentId)}/evidence`,
  )

  const data: any = response.data

  if (Array.isArray(data)) {
    return data
  }

  if (Array.isArray(data?.data)) {
    return data.data
  }

  if (Array.isArray(data?.evidence)) {
    return data.evidence
  }

  if (Array.isArray(data?.payload?.evidence)) {
    return data.payload.evidence
  }

  return []
}
