import { useEffect, useMemo, useState } from 'react'
import { AlertTriangle, ArrowRight, CheckCircle2, Clock3, RefreshCw } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

import { getIncidents } from '../api/incidents'
import { incidents as mockIncidents } from '../mock/incidents'
import type { Incident } from '../types/incident'

import './Dashboard.css'

function Dashboard() {
  const navigate = useNavigate()

  const [incidentData, setIncidentData] =
    useState<Incident[]>(mockIncidents)

  const [loading, setLoading] = useState(true)
  const [apiError, setApiError] = useState(false)

  async function loadIncidents() {
    setLoading(true)

    try {
      const data = await getIncidents()

      setIncidentData(data)
      setApiError(false)
    } catch {
      setIncidentData(mockIncidents)
      setApiError(true)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void loadIncidents()
  }, [])

  const stats = useMemo(() => {
    const active = incidentData.filter(
      (incident) =>
        incident.status !== 'resolved' &&
        incident.status !== 'failed',
    ).length

    const investigating = incidentData.filter(
      (incident) => incident.status === 'investigating',
    ).length

    const awaitingApproval = incidentData.filter(
      (incident) => incident.status === 'awaiting_approval',
    ).length

    const resolved = incidentData.filter(
      (incident) => incident.status === 'resolved',
    ).length

    return {
      active,
      investigating,
      awaitingApproval,
      resolved,
    }
  }, [incidentData])

  const activeIncidents = useMemo(() => {
    return incidentData
      .filter(
        (incident) =>
          incident.status !== 'resolved' &&
          incident.status !== 'failed',
      )
      .sort(
        (a, b) =>
          new Date(b.updatedAt).getTime() -
          new Date(a.updatedAt).getTime(),
      )
      .slice(0, 5)
  }, [incidentData])

  function getSeverityClass(severity: Incident['severity']) {
    return `dashboard-severity-${severity}`
  }

  function getStatusLabel(status: Incident['status']) {
    switch (status) {
      case 'active':
        return 'Active'
      case 'investigating':
        return 'Investigating'
      case 'awaiting_approval':
        return 'Awaiting Approval'
      case 'remediating':
        return 'Remediating'
      case 'verifying':
        return 'Verifying'
      case 'resolved':
        return 'Resolved'
      case 'failed':
        return 'Failed'
      default:
        return status
    }
  }

  function formatTime(value: string) {
    return new Date(value).toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  if (loading) {
    return (
      <div className="page dashboard-page">
        <div className="dashboard-loading">
          <RefreshCw
            size={22}
            className="dashboard-loading-icon"
          />
          <h2>Loading dashboard...</h2>
          <p>Fetching current incident data.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="page dashboard-page">
      <div className="page-heading dashboard-heading">
        <div>
          <h1>Incident Dashboard</h1>
          <p>
            Monitor production incidents and response activity.
          </p>
        </div>

        <button
          type="button"
          className="dashboard-view-all"
          onClick={() => navigate('/incidents')}
        >
          View all incidents
          <ArrowRight size={15} />
        </button>
      </div>

      {apiError && (
        <div className="dashboard-api-notice">
          <AlertTriangle size={15} />
          <span>
            Backend API is currently unavailable. Showing local
            incident data.
          </span>
        </div>
      )}

      <div className="dashboard-stats">
        <div className="dashboard-stat-card">
          <div className="dashboard-stat-icon dashboard-stat-icon-alert">
            <AlertTriangle size={18} />
          </div>

          <div>
            <span className="dashboard-stat-label">
              Active Incidents
            </span>
            <strong>{stats.active}</strong>
          </div>
        </div>

        <div className="dashboard-stat-card">
          <div className="dashboard-stat-icon dashboard-stat-icon-investigating">
            <Clock3 size={18} />
          </div>

          <div>
            <span className="dashboard-stat-label">
              Investigating
            </span>
            <strong>{stats.investigating}</strong>
          </div>
        </div>

        <div className="dashboard-stat-card">
          <div className="dashboard-stat-icon dashboard-stat-icon-approval">
            <AlertTriangle size={18} />
          </div>

          <div>
            <span className="dashboard-stat-label">
              Awaiting Approval
            </span>
            <strong>{stats.awaitingApproval}</strong>
          </div>
        </div>

        <div className="dashboard-stat-card">
          <div className="dashboard-stat-icon dashboard-stat-icon-resolved">
            <CheckCircle2 size={18} />
          </div>

          <div>
            <span className="dashboard-stat-label">
              Resolved
            </span>
            <strong>{stats.resolved}</strong>
          </div>
        </div>
      </div>

      <section className="dashboard-section">
        <div className="dashboard-section-header">
          <div>
            <h2>Active Incidents</h2>
            <p>Incidents currently requiring attention.</p>
          </div>

          <button
            type="button"
            className="dashboard-section-link"
            onClick={() => navigate('/incidents')}
          >
            Manage incidents
            <ArrowRight size={14} />
          </button>
        </div>

        <div className="dashboard-table-card">
          {activeIncidents.length === 0 ? (
            <div className="dashboard-empty">
              <CheckCircle2 size={22} />
              <h3>No active incidents</h3>
              <p>
                There are currently no incidents requiring attention.
              </p>
            </div>
          ) : (
            <div className="dashboard-table-wrapper">
              <table className="dashboard-table">
                <thead>
                  <tr>
                    <th>Incident</th>
                    <th>Service</th>
                    <th>Severity</th>
                    <th>Status</th>
                    <th>Updated</th>
                    <th />
                  </tr>
                </thead>

                <tbody>
                  {activeIncidents.map((incident) => (
                    <tr
                      key={incident.id}
                      onClick={() =>
                        navigate(`/incidents/${incident.id}`)
                      }
                    >
                      <td>
                        <div className="dashboard-incident-cell">
                          <strong>{incident.id}</strong>
                          <span>{incident.title}</span>
                        </div>
                      </td>

                      <td>{incident.service}</td>

                      <td>
                        <span
                          className={`dashboard-severity ${getSeverityClass(
                            incident.severity,
                          )}`}
                        >
                          {incident.severity}
                        </span>
                      </td>

                      <td>
                        <span className="dashboard-status">
                          {getStatusLabel(incident.status)}
                        </span>
                      </td>

                      <td>{formatTime(incident.updatedAt)}</td>

                      <td>
                        <button
                          type="button"
                          className="dashboard-row-action"
                          aria-label={`Open ${incident.id}`}
                          onClick={(event) => {
                            event.stopPropagation()
                            navigate(`/incidents/${incident.id}`)
                          }}
                        >
                          <ArrowRight size={15} />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </section>

      <section className="dashboard-section">
        <div className="dashboard-section-header">
          <div>
            <h2>Response Workflow</h2>
            <p>Current incident response lifecycle.</p>
          </div>
        </div>

        <div className="dashboard-workflow-grid">
          <div className="dashboard-workflow-card">
            <span className="dashboard-workflow-number">01</span>
            <div>
              <h3>Detect</h3>
              <p>
                Production alerts create and register incidents.
              </p>
            </div>
          </div>

          <div className="dashboard-workflow-card">
            <span className="dashboard-workflow-number">02</span>
            <div>
              <h3>Investigate</h3>
              <p>
                Specialized agents collect evidence and diagnostics.
              </p>
            </div>
          </div>

          <div className="dashboard-workflow-card">
            <span className="dashboard-workflow-number">03</span>
            <div>
              <h3>Resolve</h3>
              <p>
                RCA and remediation are reviewed before execution.
              </p>
            </div>
          </div>

          <div className="dashboard-workflow-card">
            <span className="dashboard-workflow-number">04</span>
            <div>
              <h3>Verify</h3>
              <p>
                Recovery is verified and the incident is closed.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}

export default Dashboard