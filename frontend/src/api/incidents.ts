import apiClient from './client'
import type {
  Incident,
  IncidentSeverity,
  IncidentStatus,
} from '../types/incident'

interface BackendIncident {
  id?: number | string
  incident_id?: string
  type?: string
  incident_type?: string
  severity?: string
  status?: string
  service?: string
  affected_service?: string
  affected_component?: string
  title?: string
  description?: string
  root_cause?: string
  created_at?: string
  createdAt?: string
  updated_at?: string
  updatedAt?: string
  detected_at?: string
  timestamp?: string
}

interface IncidentListResponse {
  status?: string
  incidents?: BackendIncident[]
  data?: BackendIncident[]
}

interface IncidentResponse {
  status?: string
  incident?: BackendIncident
  data?: {
    incident?: BackendIncident
  }
  incident_id?: string
  [key: string]: unknown
}

function normalizeSeverity(value?: string): IncidentSeverity {
  switch (value?.toLowerCase()) {
    case 'critical':
      return 'critical'
    case 'high':
      return 'high'
    case 'medium':
      return 'medium'
    case 'low':
      return 'low'
    default:
      return 'unknown'
  }
}

function normalizeStatus(value?: string): IncidentStatus {
  switch (value?.toUpperCase()) {
    case 'VERIFIED':
    case 'RESOLVED':
    case 'CLOSED':
      return 'resolved'

    case 'REMEDIATION_REJECTED':
    case 'FAILED':
    case 'VERIFICATION_FAILED':
      return 'failed'

    case 'APPROVED':
    case 'REMEDIATING':
    case 'EXECUTING':
      return 'remediating'

    case 'VERIFYING':
      return 'verifying'

    case 'RCA_COMPLETED':
    case 'PENDING_APPROVAL':
    case 'AWAITING_APPROVAL':
      return 'awaiting_approval'

    case 'INVESTIGATING':
    case 'INVESTIGATION_COMPLETED':
    case 'INVESTIGATED':
      return 'investigating'

    case 'OPEN':
    case 'ACTIVE':
    case 'DETECTED':
    default:
      return 'active'
  }
}

function normalizeIncident(raw: BackendIncident): Incident {
  const id = String(raw.incident_id ?? raw.id ?? '')

  const type =
    raw.incident_type ??
    raw.type ??
    'UNKNOWN'

  const service =
    raw.affected_service ??
    raw.affected_component ??
    raw.service ??
    'Unknown Service'

  const timestamp =
    raw.created_at ??
    raw.createdAt ??
    raw.detected_at ??
    raw.timestamp ??
    new Date().toISOString()

  return {
    id,
    type,
    severity: normalizeSeverity(raw.severity),
    status: normalizeStatus(raw.status),
    service,
    title:
      raw.title ??
      raw.description ??
      raw.root_cause ??
      `${type} incident`,
    createdAt: raw.created_at ?? raw.createdAt ?? timestamp,
    updatedAt: raw.updated_at ?? raw.updatedAt ?? timestamp,
  }
}

export async function getIncidents(): Promise<Incident[]> {
  const response = await apiClient.get<
    BackendIncident[] | IncidentListResponse
  >('/api/incidents/')

  const body = response.data

  const rawIncidents = Array.isArray(body)
    ? body
    : body.incidents ?? body.data ?? []

  return rawIncidents.map(normalizeIncident)
}

export async function getIncident(
  incidentId: string,
): Promise<Incident> {
  const response = await apiClient.get<
    BackendIncident | IncidentResponse
  >(`/api/incidents/${encodeURIComponent(incidentId)}`)

  const body = response.data

  const rawIncident =
    ('incident' in body ? body.incident : undefined) ??
    ('data' in body ? body.data?.incident : undefined) ??
    body

  if (
    !rawIncident ||
    typeof rawIncident !== 'object' ||
    !('incident_id' in rawIncident || 'id' in rawIncident)
  ) {
    throw new Error(`Incident not found: ${incidentId}`)
  }

  return normalizeIncident(rawIncident as BackendIncident)
}

export async function createIncident(): Promise<Incident> {
  const incidentId = `INC-UI-${Date.now()}`

  const payload = {
    incident_id: incidentId,
    incident_type: 'LATENCY',
    severity: 'HIGH',
    affected_service: 'order-api',
    title: 'Frontend generated test incident',
    description: 'Incident created from the PIRA dashboard',
    detected_at: new Date().toISOString(),
    metadata: {
      environment: 'development',
      source: 'frontend',
      current_latency_ms: 400,
      baseline_latency_ms: 100,
      increase_percent: 300,
    },
  }

  const response = await apiClient.post<
    BackendIncident | IncidentResponse
  >('/api/incidents/', payload)

  const body = response.data

  const rawIncident =
    ('incident' in body ? body.incident : undefined) ??
    ('data' in body ? body.data?.incident : undefined) ??
    body

  if (
    !rawIncident ||
    typeof rawIncident !== 'object' ||
    !('incident_id' in rawIncident || 'id' in rawIncident)
  ) {
    throw new Error(
      'Backend did not return the created incident.',
    )
  }

  return normalizeIncident(rawIncident as BackendIncident)
}
