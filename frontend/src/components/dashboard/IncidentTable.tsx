import { ArrowRight } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

import type { Incident } from '../../types/incident'
import IncidentStatusBadge from './IncidentStatusBadge'

interface IncidentTableProps {
  incidents: Incident[]
}

function formatTime(dateString: string) {
  const date = new Date(dateString)

  return date.toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  })
}

function IncidentTable({
  incidents,
}: IncidentTableProps) {
  const navigate = useNavigate()

  if (incidents.length === 0) {
    return (
      <div className="incident-table-empty">
        <p>No active incidents.</p>

        <span>
          There are currently no incidents requiring attention.
        </span>
      </div>
    )
  }

  return (
    <div className="incident-table-wrapper">
      <table className="incident-table">
        <thead>
          <tr>
            <th>Incident</th>
            <th>Severity</th>
            <th>Service</th>
            <th>Status</th>
            <th>Updated</th>
            <th aria-label="Actions" />
          </tr>
        </thead>

        <tbody>
          {incidents.map((incident) => (
            <tr key={incident.id}>
              <td>
                <div className="incident-cell">
                  <strong>{incident.id}</strong>
                  <span>{incident.title}</span>
                </div>
              </td>

              <td>
                <span
                  className={`severity severity-${incident.severity}`}
                >
                  {incident.severity}
                </span>
              </td>

              <td>
                <span className="service-name">
                  {incident.service}
                </span>
              </td>

              <td>
                <IncidentStatusBadge
                  status={incident.status}
                />
              </td>

              <td>
                <span className="incident-time">
                  {formatTime(incident.updatedAt)}
                </span>
              </td>

              <td>
                <button
                  type="button"
                  className="incident-action-button"
                  onClick={() =>
                    navigate(`/incidents/${incident.id}`)
                  }
                  aria-label={`Open ${incident.id}`}
                  title={`Open ${incident.id}`}
                >
                  <ArrowRight size={18} />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default IncidentTable