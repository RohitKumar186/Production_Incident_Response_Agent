import apiClient from './client'

interface BackendResponse<T> {
  status: string
  data: T
}

export interface VerificationResponse {
  incidentId?: string
  incident_id?: string
  status: string

  recoveryStatus?: string
  recovery_status?: string

  checks?: unknown[]
  summary?: string
  verifiedAt?: string
  verified_at?: string

  result?: string
  next_step?: string
  recommended_next_step?: string

  service_recovered?: boolean
  recovery_metrics?: unknown

  schema_version?: string
  correlation_id?: string
  timestamp?: string
  producer?: string
  consumer?: string

  message?: string
}

export async function getVerification(
  incidentId: string,
): Promise<VerificationResponse> {
  const response = await apiClient.get<BackendResponse<VerificationResponse>>(
    `/api/incidents/${incidentId}/verification`,
  )

  return response.data.data
}