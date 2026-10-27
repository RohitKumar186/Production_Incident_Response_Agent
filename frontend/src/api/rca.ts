
import apiClient from './client'

export interface RCAResponse {
  incidentId?: string
  incident_id?: string
  status?: string

  payload?: {
    incident?: Record<string, unknown>
    root_cause?: {
      description?: string
      category?: string
      confidence?: number
    } | string
    supporting_evidence?: unknown[]
    rag_context?: unknown[]
    recommended_action?: {
      action?: string
      action_type?: string
      target?: string
      risk?: string
      requires_human_approval?: boolean
    } | string
    target_version?: string
    rollback_plan?: {
      description?: string
    }
  }

  root_cause?: string | Record<string, unknown>
  rootCause?: string
  confidence?: number
  contributing_factors?: unknown[]
  contributingFactors?: string[]
  recommended_action?: string
  evidence?: unknown[]
  generatedAt?: string

  schema_version?: string
  correlation_id?: string
  timestamp?: string
  producer?: string
  consumer?: string

  [key: string]: unknown
}

export async function getRCA(
  incidentId: string,
): Promise<RCAResponse> {
  const response = await apiClient.get<RCAResponse[] | RCAResponse>(
    `/api/rca/${encodeURIComponent(incidentId)}`,
  )

  const body = response.data
  const result = Array.isArray(body) ? body[0] : body

  if (!result) {
    throw new Error(`No RCA result found for ${incidentId}`)
  }

  return result
}
