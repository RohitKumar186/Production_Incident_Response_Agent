import './InvestigationPanel.css'
import {
  Activity,
  CheckCircle2,
  Clock3,
  FileSearch,
  Server,
} from 'lucide-react'

interface InvestigationWorkflow {
  status: 'completed' | 'in_progress' | 'pending' | 'running'
  progress: number
  completedAgents: number
  totalAgents: number
  agents: {
    name: string
    detail: string
    status: 'completed' | 'running' | 'pending'
  }[]
  evidence: {
    logs: string
    metrics: string
    database: string
    network: string
  }
  findings: {
    logs: string
    metrics: string
    database: string
    network: string
  }
  timeline: {
    time: string
    title: string
    description: string
    state: 'completed' | 'active' | 'pending'
  }[]
  summary?: string
  evidenceCount?: number
}

interface InvestigationPanelProps {
  workflow: InvestigationWorkflow
}

function InvestigationPanel({
  workflow,
}: InvestigationPanelProps) {
  const isCompleted =
    workflow.status === 'completed'

  const isRunning =
    workflow.status === 'in_progress' ||
    workflow.status === 'running'

  const statusText = isCompleted
    ? 'Investigation Complete'
    : isRunning
      ? 'Investigation Running'
      : 'Investigation Pending'

  const evidenceCount =
    workflow.evidenceCount ??
    Object.values(workflow.evidence).filter(
      (value) =>
        value &&
        value !== 'Pending' &&
        value !== 'Investigating',
    ).length

  return (
    <section className="coming-workflow-section investigation-section">
      <div className="coming-workflow-header">
        <div className="coming-workflow-title">
          <div className="workflow-section-icon">
            <FileSearch size={17} />
          </div>

          <div>
            <span>PHASE 01</span>
            <h2>Investigation</h2>
          </div>
        </div>

        <span
          className={`workflow-pending-badge ${
            isCompleted
              ? 'workflow-badge-completed'
              : isRunning
                ? 'workflow-badge-active'
                : 'workflow-badge-pending'
          }`}
        >
          {statusText}
        </span>
      </div>

      <div className="workflow-section-content">
        <div className="investigation-progress">
          <div className="investigation-progress-header">
            <span>Investigation Progress</span>

            <strong>{workflow.progress}%</strong>
          </div>

          <div className="investigation-progress-track">
            <div
              className="investigation-progress-fill"
              style={{
                width: `${Math.min(
                  Math.max(workflow.progress, 0),
                  100,
                )}%`,
              }}
            />
          </div>
        </div>

        {workflow.summary && (
          <div className="investigation-summary">
            <span>Investigation Summary</span>

            <p>{workflow.summary}</p>
          </div>
        )}

        <div className="investigation-overview-grid">
          <div className="investigation-overview-card">
            <Activity size={16} />

            <div>
              <span>Agents Completed</span>

              <strong>
                {workflow.completedAgents}/
                {workflow.totalAgents}
              </strong>
            </div>
          </div>

          <div className="investigation-overview-card">
            <FileSearch size={16} />

            <div>
              <span>Evidence</span>

              <strong>
                {evidenceCount} items
              </strong>
            </div>
          </div>

          <div className="investigation-overview-card">
            {isCompleted ? (
              <CheckCircle2 size={16} />
            ) : (
              <Clock3 size={16} />
            )}

            <div>
              <span>Status</span>

              <strong>{statusText}</strong>
            </div>
          </div>
        </div>

        <div className="investigation-subsection">
          <div className="investigation-subsection-heading">
            <Server size={15} />

            <span>Specialized Agents</span>
          </div>

          <div className="investigation-agent-list">
            {workflow.agents.map((agent) => (
              <div
                className="investigation-agent"
                key={agent.name}
              >
                <div
                  className={`investigation-agent-status investigation-agent-${agent.status}`}
                >
                  {agent.status === 'completed' ? (
                    <CheckCircle2 size={13} />
                  ) : agent.status === 'running' ? (
                    <Clock3 size={13} />
                  ) : (
                    <Clock3 size={13} />
                  )}
                </div>

                <div>
                  <strong>{agent.name}</strong>

                  <span>{agent.detail}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="investigation-subsection">
          <div className="investigation-subsection-heading">
            <FileSearch size={15} />

            <span>Evidence Collected</span>
          </div>

          <div className="investigation-evidence-grid">
            <EvidenceItem
              label="Logs"
              value={workflow.evidence.logs}
            />

            <EvidenceItem
              label="Metrics"
              value={workflow.evidence.metrics}
            />

            <EvidenceItem
              label="Database"
              value={workflow.evidence.database}
            />

            <EvidenceItem
              label="Network"
              value={workflow.evidence.network}
            />
          </div>
        </div>

        <div className="investigation-subsection">
          <div className="investigation-subsection-heading">
            <Activity size={15} />

            <span>Key Findings</span>
          </div>

          <div className="investigation-findings-grid">
            <FindingItem
              label="Logs"
              value={workflow.findings.logs}
            />

            <FindingItem
              label="Metrics"
              value={workflow.findings.metrics}
            />

            <FindingItem
              label="Database"
              value={workflow.findings.database}
            />

            <FindingItem
              label="Network"
              value={workflow.findings.network}
            />
          </div>
        </div>

        {workflow.timeline.length > 0 && (
          <div className="investigation-subsection">
            <div className="investigation-subsection-heading">
              <Clock3 size={15} />

              <span>Investigation Timeline</span>
            </div>

            <div className="investigation-timeline">
              {workflow.timeline.map((item, index) => (
                <div
                  className="investigation-timeline-item"
                  key={`${item.time}-${item.title}-${index}`}
                >
                  <div
                    className={`investigation-timeline-marker timeline-${item.state}`}
                  >
                    {item.state === 'completed' ? (
                      <CheckCircle2 size={12} />
                    ) : (
                      <Clock3 size={12} />
                    )}
                  </div>

                  <div className="investigation-timeline-content">
                    <div>
                      <strong>{item.title}</strong>
                      <span>{item.time}</span>
                    </div>

                    <p>{item.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </section>
  )
}

function EvidenceItem({
  label,
  value,
}: {
  label: string
  value: string
}) {
  return (
    <div className="investigation-evidence-item">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  )
}

function FindingItem({
  label,
  value,
}: {
  label: string
  value: string
}) {
  return (
    <div className="investigation-finding-item">
      <span>{label}</span>
      <p>{value}</p>
    </div>
  )
}

export default InvestigationPanel