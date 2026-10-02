export type IncidentStatus =
  | 'active'
  | 'investigating'
  | 'awaiting_approval'
  | 'remediating'
  | 'verifying'
  | 'resolved'
  | 'failed'

export type IncidentSeverity =
  | 'critical'
  | 'high'
  | 'medium'
  | 'low'
  | 'unknown'

export interface Incident {
  id: string
  type: string
  severity: IncidentSeverity
  status: IncidentStatus
  service: string
  title: string
  createdAt: string
  updatedAt: string
}