import { AlertTriangle, CheckCircle2, Clock3, ShieldAlert } from 'lucide-react'

interface RemediationWorkflow {
  status: string
  action?: string
  description?: string
  risk?: string
  proposedBy?: string
  createdAt?: string
}

interface RemediationSectionProps {
  workflow: RemediationWorkflow
}

function RemediationSection({
  workflow,
}: RemediationSectionProps) {
  const statusLabel =
    workflow.status === 'completed'
      ? 'Remediation Complete'
      : workflow.status === 'executing'
        ? 'Remediation Executing'
        : workflow.status === 'approved'
          ? 'Remediation Approved'
          : workflow.status === 'pending'
            ? 'Awaiting Approval'
            : workflow.status

  const isCompleted = workflow.status === 'completed'
  const isExecuting = workflow.status === 'executing'
  const isApproved = workflow.status === 'approved'

  return (
    <section className="workflow-section">
      <div className="workflow-section-header">
        <div className="workflow-section-title">
          <div className="workflow-section-icon">
            <ShieldAlert size={17} />
          </div>

          <div>
            <h2>Remediation</h2>
            <p>
              Proposed corrective action for the incident.
            </p>
          </div>
        </div>

        <span
          className={`workflow-status ${
            isCompleted
              ? 'workflow-status-completed'
              : isExecuting || isApproved
                ? 'workflow-status-running'
                : 'workflow-status-pending'
          }`}
        >
          {statusLabel}
        </span>
      </div>

      <div className="workflow-detail-grid remediation-detail-grid">
        <div className="workflow-detail-item workflow-detail-wide">
          <span>Proposed Action</span>

          <strong>
            {workflow.action ||
              'Remediation proposal is pending.'}
          </strong>
        </div>

        <div className="workflow-detail-item">
          <span>Risk</span>

          <strong>
            {workflow.risk || 'Not specified'}
          </strong>
        </div>

        <div className="workflow-detail-item">
          <span>Proposed By</span>

          <strong>
            {workflow.proposedBy || 'PIRA Orchestrator'}
          </strong>
        </div>
      </div>

      {workflow.description && (
        <div className="remediation-description">
          <span className="workflow-detail-label">
            Description
          </span>

          <p>{workflow.description}</p>
        </div>
      )}

      {workflow.risk && (
        <div className="remediation-risk">
          <AlertTriangle size={15} />

          <div>
            <strong>Risk Assessment</strong>
            <p>{workflow.risk}</p>
          </div>
        </div>
      )}

      {isApproved && (
        <div className="remediation-state remediation-state-approved">
          <CheckCircle2 size={16} />

          <div>
            <strong>Remediation approved</strong>
            <p>
              The approved remediation can now proceed through
              the execution stage.
            </p>
          </div>
        </div>
      )}

      {isExecuting && (
        <div className="remediation-state remediation-state-executing">
          <Clock3 size={16} />

          <div>
            <strong>Remediation executing</strong>
            <p>
              The corrective action is currently being executed.
            </p>
          </div>
        </div>
      )}

      {isCompleted && (
        <div className="remediation-state remediation-state-completed">
          <CheckCircle2 size={16} />

          <div>
            <strong>Remediation completed</strong>
            <p>
              The corrective action has completed successfully.
            </p>
          </div>
        </div>
      )}
    </section>
  )
}

export default RemediationSection