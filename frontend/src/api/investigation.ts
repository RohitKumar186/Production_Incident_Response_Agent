import apiClient from './client'

interface BackendResponse<T> {
  status: string
  data: T
}

export interface InvestigationResponse {
  incidentId: string
  status: string
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
}

export async function getInvestigation(
  incidentId: string,
): Promise<InvestigationResponse> {
  const response = await apiClient.get<BackendResponse<InvestigationResponse>>(
    `/api/incidents/${incidentId}/investigation`,
  )

  return response.data.data
}

export async function getIncidentEvidence(
  incidentId: string,
): Promise<unknown[]> {
  const response = await apiClient.get<BackendResponse<unknown[]>>(
    `/api/incidents/${incidentId}/evidence`,
  )

  return response.data.data
}