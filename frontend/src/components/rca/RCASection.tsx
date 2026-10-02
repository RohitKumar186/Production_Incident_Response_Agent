import { CheckCircle2, FileSearch, ShieldCheck } from 'lucide-react'

interface RCAWorkflow {
  status: string
  rootCause?: string
  confidence?: number
  contributingFactors?: string[]
  evidenceCount?: number
  generatedAt?: string
}

interface RCASectionProps {
  workflow: RCAWorkflow
}

function RCASection({ workflow }: RCASectionProps) {
  const isCompleted = workflow.status === 'completed'

  const confidence = Math.min(
    Math.max(workflow.confidence ?? 0, 0),
    100,
  )

  return (
    <section className="workflow-section">
      <div className="workflow-section-header">
        <div className="workflow-section-title">
          <div className="workflow-section-icon">
            <ShieldCheck size={17} />
          </div>

          <div>
            <h2>Root Cause Analysis</h2>
            <p>
              Determine the underlying cause of the incident.
            </p>
          </div>
        </div>

        <span
          className={`workflow-status workflow-status-${
            isCompleted ? 'completed' : 'pending'
          }`}
        >
          {isCompleted ? 'RCA Complete' : 'RCA Pending'}
        </span>
      </div>

      <div className="workflow-detail-grid">
        <div className="workflow-detail-item workflow-detail-wide">
          <span>Root Cause</span>

          <strong>
            {workflow.rootCause || 'Root cause analysis is pending.'}
          </strong>
        </div>

        <div className="workflow-detail-item">
          <span>Confidence</span>

          <strong>{confidence}%</strong>
        </div>

        <div className="workflow-detail-item">
          <span>Evidence Reviewed</span>

          <strong>
            {workflow.evidenceCount ?? 0} items
          </strong>
        </div>
      </div>

      {confidence > 0 && (
        <div className="rca-confidence">
          <div className="rca-confidence-header">
            <span>RCA Confidence</span>
            <strong>{confidence}%</strong>
          </div>

          <div className="rca-confidence-track">
            <div
              className="rca-confidence-fill"
              style={{ width: `${confidence}%` }}
            />
          </div>
        </div>
      )}

      {workflow.contributingFactors &&
        workflow.contributingFactors.length > 0 && (
          <div className="rca-factors">
            <span className="workflow-detail-label">
              Contributing Factors
            </span>

            <div className="rca-factor-list">
              {workflow.contributingFactors.map(
                (factor, index) => (
                  <div
                    className="rca-factor"
                    key={`${factor}-${index}`}
                  >
                    <CheckCircle2 size={14} />
                    <span>{factor}</span>
                  </div>
                ),
              )}
            </div>
          </div>
        )}

      <div className="rca-evidence-note">
        <FileSearch size={15} />

        <span>
          RCA findings are generated from the evidence collected
          during the investigation phase.
        </span>
      </div>
    </section>
  )
}

export default RCASection