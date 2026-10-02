import {
  useEffect,
  useMemo,
  useState,
} from 'react'
import {
  ArrowRight,
  Plus,
  RefreshCw,
  Search,
} from 'lucide-react'
import { useNavigate } from 'react-router-dom'

import {
  createIncident,
  getIncidents,
} from '../api/incidents'

import {
  incidents as mockIncidents,
} from '../mock/incidents'

import type {
  Incident,
  IncidentSeverity,
  IncidentStatus,
} from '../types/incident'

import './Incidents.css'

type SortOption =
  | 'newest'
  | 'oldest'
  | 'severity-high'
  | 'severity-low'

const severityRank: Record<
  IncidentSeverity,
  number
> = {
  critical: 4,
  high: 3,
  medium: 2,
  low: 1,
  unknown: 0,
}

const statusLabels: Record<
  IncidentStatus,
  string
> = {
  active: 'Active',
  investigating: 'Investigating',
  awaiting_approval:
    'Awaiting Approval',
  remediating: 'Remediating',
  verifying: 'Verifying',
  resolved: 'Resolved',
  failed: 'Failed',
}

function formatDate(
  value: string,
) {
  const date = new Date(value)

  if (
    Number.isNaN(
      date.getTime(),
    )
  ) {
    return '—'
  }

  return date.toLocaleString([], {
    month: 'short',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function Incidents() {
  const navigate = useNavigate()

  const [incidentData, setIncidentData] =
    useState<Incident[]>(
      mockIncidents,
    )

  const [searchQuery, setSearchQuery] =
    useState('')

  const [severityFilter, setSeverityFilter] =
    useState<
      'all' | IncidentSeverity
    >('all')

  const [statusFilter, setStatusFilter] =
    useState<
      'all' | IncidentStatus
    >('all')

  const [sortOption, setSortOption] =
    useState<SortOption>(
      'newest',
    )

  const [loading, setLoading] =
    useState(true)

  const [apiError, setApiError] =
    useState(false)

  const [refreshing, setRefreshing] =
    useState(false)

  const [generating, setGenerating] =
    useState(false)

  const [generateError, setGenerateError] =
    useState(false)

  async function loadIncidents(
    showRefreshState = false,
  ) {
    if (showRefreshState) {
      setRefreshing(true)
    } else {
      setLoading(true)
    }

    try {
      const data =
        await getIncidents()

      setIncidentData(data)
      setApiError(false)
    } catch {
      setIncidentData(
        mockIncidents,
      )
      setApiError(true)
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  useEffect(() => {
    void loadIncidents()
  }, [])

  async function handleGenerateIncident() {
    if (generating) {
      return
    }

    setGenerating(true)
    setGenerateError(false)

    try {
      const incident =
        await createIncident()

      setIncidentData(
        (current) => [
          incident,
          ...current.filter(
            (item) =>
              item.id !==
              incident.id,
          ),
        ],
      )

      navigate(
        `/incidents/${incident.id}`,
      )
    } catch (error) {
      console.error(
        'Failed to generate incident:',
        error,
      )

      setGenerateError(true)
    } finally {
      setGenerating(false)
    }
  }

  const filteredIncidents =
    useMemo(() => {
      const query =
        searchQuery
          .trim()
          .toLowerCase()

      const result =
        incidentData.filter(
          (incident) => {
            const matchesSearch =
              !query ||
              incident.id
                .toLowerCase()
                .includes(query) ||
              incident.title
                .toLowerCase()
                .includes(query) ||
              incident.service
                .toLowerCase()
                .includes(query) ||
              incident.type
                .toLowerCase()
                .includes(query)

            const matchesSeverity =
              severityFilter ===
                'all' ||
              incident.severity ===
                severityFilter

            const matchesStatus =
              statusFilter ===
                'all' ||
              incident.status ===
                statusFilter

            return (
              matchesSearch &&
              matchesSeverity &&
              matchesStatus
            )
          },
        )

      return [...result].sort(
        (a, b) => {
          if (
            sortOption ===
            'newest'
          ) {
            return (
              new Date(
                b.createdAt,
              ).getTime() -
              new Date(
                a.createdAt,
              ).getTime()
            )
          }

          if (
            sortOption ===
            'oldest'
          ) {
            return (
              new Date(
                a.createdAt,
              ).getTime() -
              new Date(
                b.createdAt,
              ).getTime()
            )
          }

          if (
            sortOption ===
            'severity-high'
          ) {
            return (
              severityRank[
                b.severity
              ] -
              severityRank[
                a.severity
              ]
            )
          }

          return (
            severityRank[
              a.severity
            ] -
            severityRank[
              b.severity
            ]
          )
        },
      )
    }, [
      incidentData,
      searchQuery,
      severityFilter,
      statusFilter,
      sortOption,
    ])

  function openIncident(
    incidentId: string,
  ) {
    navigate(
      `/incidents/${incidentId}`,
    )
  }

  return (
    <div className="page incidents-page">
      <div className="page-heading">
        <div>
          <h1>
            Incident Management
          </h1>

          <p>
            Monitor, investigate,
            and manage production
            incidents.
          </p>
        </div>

        <div
          style={{
            display: 'flex',
            gap: '10px',
            alignItems: 'center',
            flexWrap: 'wrap',
          }}
        >
          <button
            type="button"
            className="incidents-refresh-button"
            onClick={() =>
              void handleGenerateIncident()
            }
            disabled={generating}
          >
            {generating ? (
              <RefreshCw
                size={15}
                className="refresh-spinning"
              />
            ) : (
              <Plus size={15} />
            )}

            <span>
              {generating
                ? 'Generating...'
                : 'Generate Incident'}
            </span>
          </button>

          <button
            type="button"
            className="incidents-refresh-button"
            onClick={() =>
              void loadIncidents(
                true,
              )
            }
            disabled={
              refreshing
            }
          >
            <RefreshCw
              size={15}
              className={
                refreshing
                  ? 'refresh-spinning'
                  : undefined
              }
            />

            <span>
              Refresh
            </span>
          </button>
        </div>
      </div>

      {apiError && (
        <div className="incidents-api-notice">
          <span>
            Backend API is currently
            unavailable. Showing local
            incident data.
          </span>
        </div>
      )}

      {generateError && (
        <div className="incidents-api-notice">
          <span>
            Unable to generate an
            incident. Please check
            that the PIRA backend is
            running and try again.
          </span>
        </div>
      )}

      <div className="incidents-toolbar">
        <div className="incidents-search">
          <Search size={16} />

          <input
            type="text"
            placeholder="Search incidents..."
            value={searchQuery}
            onChange={(event) =>
              setSearchQuery(
                event.target.value,
              )
            }
          />
        </div>

        <select
          value={severityFilter}
          onChange={(event) =>
            setSeverityFilter(
              event.target.value as
                | 'all'
                | IncidentSeverity,
            )
          }
        >
          <option value="all">
            All Severities
          </option>

          <option value="critical">
            Critical
          </option>

          <option value="high">
            High
          </option>

          <option value="medium">
            Medium
          </option>

          <option value="low">
            Low
          </option>

          <option value="unknown">
            Unknown
          </option>
        </select>

        <select
          value={statusFilter}
          onChange={(event) =>
            setStatusFilter(
              event.target.value as
                | 'all'
                | IncidentStatus,
            )
          }
        >
          <option value="all">
            All Statuses
          </option>

          <option value="active">
            Active
          </option>

          <option value="investigating">
            Investigating
          </option>

          <option value="awaiting_approval">
            Awaiting Approval
          </option>

          <option value="remediating">
            Remediating
          </option>

          <option value="verifying">
            Verifying
          </option>

          <option value="resolved">
            Resolved
          </option>

          <option value="failed">
            Failed
          </option>
        </select>

        <select
          value={sortOption}
          onChange={(event) =>
            setSortOption(
              event.target.value as SortOption,
            )
          }
        >
          <option value="newest">
            Newest First
          </option>

          <option value="oldest">
            Oldest First
          </option>

          <option value="severity-high">
            Severity: High to Low
          </option>

          <option value="severity-low">
            Severity: Low to High
          </option>
        </select>
      </div>

      <div className="incidents-results">
        <span>
          Showing{' '}
          {
            filteredIncidents.length
          }{' '}
          of{' '}
          {incidentData.length}{' '}
          incidents
        </span>
      </div>

      <div className="incidents-table-card">
        {loading ? (
          <div className="incidents-loading">
            <RefreshCw
              size={20}
              className="refresh-spinning"
            />

            <h2>
              Loading incidents...
            </h2>

            <p>
              Fetching current
              incident data.
            </p>
          </div>
        ) : filteredIncidents.length ===
          0 ? (
          <div className="incidents-empty">
            <Search size={22} />

            <h3>
              No incidents found
            </h3>

            <p>
              Try changing your
              search or filter
              criteria.
            </p>
          </div>
        ) : (
          <div className="incidents-table-wrapper">
            <table className="incidents-table">
              <thead>
                <tr>
                  <th>
                    Incident
                  </th>

                  <th>
                    Type
                  </th>

                  <th>
                    Service
                  </th>

                  <th>
                    Severity
                  </th>

                  <th>
                    Status
                  </th>

                  <th>
                    Created
                  </th>

                  <th>
                    Updated
                  </th>

                  <th />
                </tr>
              </thead>

              <tbody>
                {filteredIncidents.map(
                  (incident) => (
                    <tr
                      key={
                        incident.id
                      }
                      onClick={() =>
                        openIncident(
                          incident.id,
                        )
                      }
                    >
                      <td>
                        <div className="incident-id-cell">
                          <strong>
                            {
                              incident.id
                            }
                          </strong>

                          <span>
                            {
                              incident.title
                            }
                          </span>
                        </div>
                      </td>

                      <td>
                        <span className="incident-type">
                          {
                            incident.type
                          }
                        </span>
                      </td>

                      <td>
                        {
                          incident.service
                        }
                      </td>

                      <td>
                        <span
                          className={`severity-badge severity-${incident.severity}`}
                        >
                          {
                            incident.severity
                          }
                        </span>
                      </td>

                      <td>
                        <span
                          className={`status-badge status-${incident.status}`}
                        >
                          {
                            statusLabels[
                              incident.status
                            ]
                          }
                        </span>
                      </td>

                      <td>
                        {formatDate(
                          incident.createdAt,
                        )}
                      </td>

                      <td>
                        {formatDate(
                          incident.updatedAt,
                        )}
                      </td>

                      <td>
                        <button
                          type="button"
                          className="incident-row-action"
                          aria-label={`Open ${incident.id}`}
                          title={`Open ${incident.id}`}
                          onClick={(
                            event,
                          ) => {
                            event.stopPropagation()

                            openIncident(
                              incident.id,
                            )
                          }}
                        >
                          <ArrowRight
                            size={16}
                          />
                        </button>
                      </td>
                    </tr>
                  ),
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}

export default Incidents