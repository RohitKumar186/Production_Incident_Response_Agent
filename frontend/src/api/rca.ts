import apiClient from './client'

interface BackendResponse<T> {
  status: string
  data: T
}

export interface RCAResponse {
  incidentId?: string
  incident_id?: string
  status: string

  payload?: {
    incident?: Record<string, unknown>

    root_cause?: {
      description?: string
      category?: string
      confidence?: number
    }

    supporting_evidence?: unknown[]

    rag_context?: unknown[]

    recommended_action?: {
      action?: string
      action_type?: string
      target?: string
      risk?: string
      requires_human_approval?: boolean
    }

    target_version?: string

    rollback_plan?: {
      description?: string
    }
  }

  // Compatibility fields
  rootCause?: string
  confidence?: number
  contributingFactors?: string[]
  evidence?: unknown[]
  generatedAt?: string

  // Backend fields
  schema_version?: string
  correlation_id?: string
  timestamp?: string
  producer?: string
  consumer?: string
}

export async function getRCA(
  incidentId: string,
): Promise<RCAResponse> {
  const response = await apiClient.get<BackendResponse<RCAResponse>>(
    `/api/incidents/${incidentId}/rca`,
  )

  return response.data.data
}