import type { IncidentStatus } from '../../types/incident'

interface IncidentStatusBadgeProps {
  status: IncidentStatus
}

const statusLabels: Record<IncidentStatus, string> = {
  active: 'Active',
  investigating: 'Investigating',
  awaiting_approval: 'Awaiting Approval',
  remediating: 'Remediating',
  verifying: 'Verifying',
  resolved: 'Resolved',
  failed: 'Failed',
}

function IncidentStatusBadge({
  status,
}: IncidentStatusBadgeProps) {
  return (
    <span className={`status-badge status-${status}`}>
      <span className="status-dot" />
      {statusLabels[status]}
    </span>
  )
}

export default IncidentStatusBadge