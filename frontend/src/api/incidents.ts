import apiClient from './client'
import type {
  Incident,
  IncidentSeverity,
  IncidentStatus,
} from '../types/incident'

interface BackendIncident {
  id?: string
  incident_id?: string
  type?: string
  incident_type?: string
  severity?: string
  status?: string
  service?: string
  affected_component?: string
  title?: string
  description?: string
  root_cause?: string
  createdAt?: string
  updatedAt?: string
  timestamp?: string
}

interface IncidentListResponse {
  status?: string
  incidents?: BackendIncident[]
}

interface IncidentResponse {
  status?: string
  incident?: BackendIncident
  data?: {
    incident?: BackendIncident
  }
}

function normalizeSeverity(
  value?: string,
): IncidentSeverity {
  const severity = value?.toLowerCase()

  if (
    severity === 'critical' ||
    severity === 'high' ||
    severity === 'medium' ||
    severity === 'low'
  ) {
    return severity
  }

  return 'unknown'
}

function normalizeStatus(
  value?: string,
): IncidentStatus {
  const status = value?.toLowerCase()

  switch (status) {
    case 'resolved':
      return 'resolved'

    case 'remediated':
    case 'remediating':
      return 'remediating'

    case 'investigating':
    case 'investigated':
      return 'investigating'

    case 'awaiting_approval':
      return 'awaiting_approval'

    case 'verifying':
      return 'verifying'

    case 'failed':
    case 'verification_failed':
      return 'failed'

    case 'active':
    case 'detected':
      return 'active'

    default:
      return 'active'
  }
}

function normalizeIncident(
  raw: BackendIncident,
): Incident {
  const id =
    raw.id ??
    raw.incident_id ??
    ''

  const type =
    raw.type ??
    raw.incident_type ??
    'UNKNOWN'

  const service =
    raw.service ??
    raw.affected_component ??
    'Unknown Service'

  const timestamp =
    raw.timestamp ??
    raw.createdAt ??
    new Date().toISOString()

  const title =
    raw.title ??
    raw.description ??
    raw.root_cause ??
    `${type} incident`

  return {
    id,
    type,
    severity: normalizeSeverity(
      raw.severity,
    ),
    status: normalizeStatus(
      raw.status,
    ),
    service,
    title,
    createdAt:
      raw.createdAt ??
      timestamp,
    updatedAt:
      raw.updatedAt ??
      timestamp,
  }
}

export async function getIncidents(): Promise<Incident[]> {
  const response =
    await apiClient.get<
      BackendIncident[] | IncidentListResponse
    >('/api/incidents')

  const body = response.data

  const rawIncidents = Array.isArray(body)
    ? body
    : body.incidents ?? []

  return rawIncidents.map(
    normalizeIncident,
  )
}

export async function getIncident(
  incidentId: string,
): Promise<Incident> {
  const response =
    await apiClient.get<IncidentResponse>(
      `/api/incidents/${incidentId}`,
    )

  const body = response.data

  const rawIncident =
    body.incident ??
    body.data?.incident

  if (!rawIncident) {
    throw new Error(
      `Incident not found: ${incidentId}`,
    )
  }

  return normalizeIncident(
    rawIncident,
  )
}

export async function createIncident(): Promise<Incident> {
  const response =
    await apiClient.post<
      IncidentResponse | BackendIncident
    >('/api/incidents')

  const body = response.data

  const rawIncident =
    'incident' in body
      ? body.incident
      : 'data' in body
        ? body.data?.incident
        : body

  if (!rawIncident) {
    throw new Error(
      'Backend did not return the created incident.',
    )
  }

  return normalizeIncident(
    rawIncident,
  )
}