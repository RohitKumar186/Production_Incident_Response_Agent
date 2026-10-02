import type { IncidentStatus } from '../types/incident'

export type WorkflowPhase =
  | 'investigation'
  | 'rca'
  | 'remediation'
  | 'approval'
  | 'verification'
  | 'resolved'

export type WorkflowItemStatus =
  | 'completed'
  | 'active'
  | 'pending'

export interface InvestigationAgent {
  name: string
  detail: string
  status: 'completed' | 'running' | 'pending'
}

export interface InvestigationTimelineItem {
  time: string
  title: string
  description: string
  state: 'completed' | 'active' | 'pending'
}

export interface InvestigationWorkflow {
  status: 'completed' | 'in_progress' | 'pending'
  progress: number
  completedAgents: number
  totalAgents: number
  agents: InvestigationAgent[]
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
  timeline: InvestigationTimelineItem[]
}

export interface IncidentWorkflow {
  currentPhase: WorkflowPhase

  investigation: InvestigationWorkflow

  rca: {
    status: WorkflowItemStatus
    rootCause: string
    confidence: string
    evidence: string
    historicalContext: string
    recommendedAction: string
  }

  remediation: {
    status: WorkflowItemStatus
    action: string
    risk: string
    executionState: string
    result: string
  }

  approval: {
    status: WorkflowItemStatus
    message: string
    approvedBy: string
    timestamp: string
  }

  verification: {
    status: WorkflowItemStatus
    recoveryStatus: string
    recoveryMetrics: string
    result: string
    nextStep: string
  }
}

const defaultAgents: InvestigationAgent[] = [
  {
    name: 'Log Analysis Agent',
    detail: 'Application and gateway logs analyzed',
    status: 'completed',
  },
  {
    name: 'Metrics Agent',
    detail: 'Latency and error-rate metrics analyzed',
    status: 'completed',
  },
  {
    name: 'Database Agent',
    detail: 'Database health and connection state checked',
    status: 'completed',
  },
  {
    name: 'Network Agent',
    detail: 'Network dependency analysis in progress',
    status: 'running',
  },
]

export const incidentWorkflows: Record<
  string,
  IncidentWorkflow
> = {
  'INC-001': {
    currentPhase: 'investigation',

    investigation: {
      status: 'in_progress',
      progress: 75,
      completedAgents: 3,
      totalAgents: 4,

      agents: defaultAgents,

      evidence: {
        logs: '1,284',
        metrics: '+400%',
        database: 'Healthy',
        network: 'Investigating',
      },

      findings: {
        logs: 'Elevated gateway response times',
        metrics: 'API latency increased by 400%',
        database: 'Primary database responding normally',
        network:
          'Downstream dependency analysis running',
      },

      timeline: [
        {
          time: '20:10',
          title: 'Incident detected',
          description:
            'API latency threshold exceeded.',
          state: 'completed',
        },
        {
          time: '20:12',
          title: 'Investigation started',
          description:
            'PIRA orchestrator dispatched diagnostic agents.',
          state: 'completed',
        },
        {
          time: '20:16',
          title: 'Evidence collected',
          description:
            'Logs, metrics and database evidence gathered.',
          state: 'completed',
        },
        {
          time: '20:22',
          title: 'Network analysis',
          description:
            'Network dependency analysis currently running.',
          state: 'active',
        },
      ],
    },

    rca: {
      status: 'pending',
      rootCause: 'Pending investigation',
      confidence: 'Not available',
      evidence: 'Investigation still in progress.',
      historicalContext: 'Not yet evaluated.',
      recommendedAction: 'Pending RCA.',
    },

    remediation: {
      status: 'pending',
      action: 'Pending root cause analysis.',
      risk: 'Not assessed',
      executionState: 'Not started',
      result: 'No remediation executed.',
    },

    approval: {
      status: 'pending',
      message: 'Approval will be requested after remediation proposal.',
      approvedBy: '—',
      timestamp: '—',
    },

    verification: {
      status: 'pending',
      recoveryStatus: 'Not started',
      recoveryMetrics: 'Not available',
      result: 'Verification pending remediation.',
      nextStep: 'Complete investigation.',
    },
  },

  'INC-002': {
    currentPhase: 'approval',

    investigation: {
      status: 'completed',
      progress: 100,
      completedAgents: 4,
      totalAgents: 4,

      agents: [
        {
          name: 'Log Analysis Agent',
          detail: 'Database connection errors analyzed',
          status: 'completed',
        },
        {
          name: 'Metrics Agent',
          detail: 'Connection pool utilization analyzed',
          status: 'completed',
        },
        {
          name: 'Database Agent',
          detail: 'Connection pool exhaustion confirmed',
          status: 'completed',
        },
        {
          name: 'Network Agent',
          detail: 'Database network path verified',
          status: 'completed',
        },
      ],

      evidence: {
        logs: '842',
        metrics: '96%',
        database: 'Exhausted',
        network: 'Healthy',
      },

      findings: {
        logs: 'Repeated database connection acquisition failures',
        metrics: 'Connection pool utilization reached 96%',
        database: 'Connection pool exhaustion confirmed',
        network: 'Database network path operating normally',
      },

      timeline: [
        {
          time: '19:45',
          title: 'Incident detected',
          description:
            'Database connection pool threshold exceeded.',
          state: 'completed',
        },
        {
          time: '19:48',
          title: 'Investigation started',
          description:
            'Diagnostic agents began database analysis.',
          state: 'completed',
        },
        {
          time: '19:55',
          title: 'Root cause identified',
          description:
            'Connection pool exhaustion confirmed.',
          state: 'completed',
        },
        {
          time: '20:05',
          title: 'Awaiting approval',
          description:
            'Remediation proposal requires operator approval.',
          state: 'active',
        },
      ],
    },

    rca: {
      status: 'completed',
      rootCause: 'Database connection pool exhaustion',
      confidence: '94%',
      evidence:
        'Connection utilization and repeated acquisition failures correlate with the incident.',
      historicalContext:
        'Similar pool exhaustion was observed during high request concurrency.',
      recommendedAction:
        'Increase pool capacity and recycle affected application connections.',
    },

    remediation: {
      status: 'completed',
      action:
        'Increase database connection pool capacity and recycle stale connections.',
      risk: 'Medium',
      executionState: 'Proposal prepared',
      result:
        'Remediation plan prepared for human approval.',
    },

    approval: {
      status: 'active',
      message:
        'Human approval is required before remediation execution.',
      approvedBy: 'Awaiting operator',
      timestamp: '20:05',
    },

    verification: {
      status: 'pending',
      recoveryStatus: 'Not started',
      recoveryMetrics: 'Not available',
      result: 'Verification will begin after remediation.',
      nextStep: 'Approve remediation.',
    },
  },

  'INC-003': {
    currentPhase: 'investigation',

    investigation: {
      status: 'in_progress',
      progress: 50,
      completedAgents: 2,
      totalAgents: 4,

      agents: [
        {
          name: 'Log Analysis Agent',
          detail: 'Service communication logs analyzed',
          status: 'completed',
        },
        {
          name: 'Metrics Agent',
          detail: 'Packet-loss metrics analyzed',
          status: 'completed',
        },
        {
          name: 'Database Agent',
          detail: 'Database dependency check pending',
          status: 'pending',
        },
        {
          name: 'Network Agent',
          detail: 'Network path analysis in progress',
          status: 'running',
        },
      ],

      evidence: {
        logs: '634',
        metrics: '12.4%',
        database: 'Pending',
        network: 'Investigating',
      },

      findings: {
        logs: 'Inter-service request failures detected',
        metrics: 'Packet loss reached 12.4%',
        database: 'Dependency check pending',
        network: 'Network path investigation in progress',
      },

      timeline: [
        {
          time: '18:40',
          title: 'Incident detected',
          description:
            'Packet-loss threshold exceeded.',
          state: 'completed',
        },
        {
          time: '18:43',
          title: 'Investigation started',
          description:
            'Network and metrics agents dispatched.',
          state: 'completed',
        },
        {
          time: '18:52',
          title: 'Initial evidence collected',
          description:
            'Service communication failures identified.',
          state: 'completed',
        },
        {
          time: '19:02',
          title: 'Network path analysis',
          description:
            'Network dependency investigation continues.',
          state: 'active',
        },
      ],
    },

    rca: {
      status: 'pending',
      rootCause: 'Pending network investigation',
      confidence: 'Not available',
      evidence: 'Additional network evidence required.',
      historicalContext: 'Not yet evaluated.',
      recommendedAction: 'Pending RCA.',
    },

    remediation: {
      status: 'pending',
      action: 'Pending root cause analysis.',
      risk: 'Not assessed',
      executionState: 'Not started',
      result: 'No remediation executed.',
    },

    approval: {
      status: 'pending',
      message: 'Approval will follow remediation proposal.',
      approvedBy: '—',
      timestamp: '—',
    },

    verification: {
      status: 'pending',
      recoveryStatus: 'Not started',
      recoveryMetrics: 'Not available',
      result: 'Verification pending remediation.',
      nextStep: 'Complete investigation.',
    },
  },

  'INC-004': {
    currentPhase: 'remediation',

    investigation: {
      status: 'completed',
      progress: 100,
      completedAgents: 4,
      totalAgents: 4,

      agents: [
        {
          name: 'Log Analysis Agent',
          detail: 'Workflow error logs analyzed',
          status: 'completed',
        },
        {
          name: 'Metrics Agent',
          detail: 'Error-rate metrics analyzed',
          status: 'completed',
        },
        {
          name: 'Database Agent',
          detail: 'Database dependency verified',
          status: 'completed',
        },
        {
          name: 'Network Agent',
          detail: 'Service network path verified',
          status: 'completed',
        },
      ],

      evidence: {
        logs: '2,417',
        metrics: '+68%',
        database: 'Healthy',
        network: 'Healthy',
      },

      findings: {
        logs: 'Workflow worker exceptions increased',
        metrics: 'Workflow error rate increased by 68%',
        database: 'Database dependency healthy',
        network: 'Service network path healthy',
      },

      timeline: [
        {
          time: '17:30',
          title: 'Incident detected',
          description:
            'Workflow error rate exceeded threshold.',
          state: 'completed',
        },
        {
          time: '17:35',
          title: 'Investigation started',
          description:
            'Diagnostic agents analyzed workflow dependencies.',
          state: 'completed',
        },
        {
          time: '17:55',
          title: 'Root cause identified',
          description:
            'Worker processing failure identified.',
          state: 'completed',
        },
        {
          time: '18:10',
          title: 'Remediation started',
          description:
            'Worker recovery procedure is executing.',
          state: 'active',
        },
      ],
    },

    rca: {
      status: 'completed',
      rootCause: 'Workflow worker processing failure',
      confidence: '91%',
      evidence:
        'Worker exceptions correlate directly with the increased workflow error rate.',
      historicalContext:
        'Previous incidents showed similar worker instability after deployment changes.',
      recommendedAction:
        'Restart affected workers and restore healthy worker capacity.',
    },

    remediation: {
      status: 'active',
      action:
        'Restart affected workflow workers and restore capacity.',
      risk: 'Low',
      executionState: 'Executing',
      result: 'Worker recovery currently in progress.',
    },

    approval: {
      status: 'completed',
      message: 'Remediation approved by incident operator.',
      approvedBy: 'Incident Operator',
      timestamp: '18:03',
    },

    verification: {
      status: 'pending',
      recoveryStatus: 'Waiting for remediation',
      recoveryMetrics: 'Not available',
      result: 'Verification begins after worker recovery.',
      nextStep: 'Complete remediation.',
    },
  },

  'INC-005': {
    currentPhase: 'resolved',

    investigation: {
      status: 'completed',
      progress: 100,
      completedAgents: 4,
      totalAgents: 4,

      agents: [
        {
          name: 'Log Analysis Agent',
          detail: 'Worker resource logs analyzed',
          status: 'completed',
        },
        {
          name: 'Metrics Agent',
          detail: 'CPU and memory metrics analyzed',
          status: 'completed',
        },
        {
          name: 'Database Agent',
          detail: 'Database dependency verified',
          status: 'completed',
        },
        {
          name: 'Network Agent',
          detail: 'Cluster network path verified',
          status: 'completed',
        },
      ],

      evidence: {
        logs: '1,923',
        metrics: '91%',
        database: 'Healthy',
        network: 'Healthy',
      },

      findings: {
        logs: 'Worker resource exhaustion confirmed',
        metrics: 'Node memory utilization reached 91%',
        database: 'Database dependency healthy',
        network: 'Cluster network healthy',
      },

      timeline: [
        {
          time: '15:20',
          title: 'Incident detected',
          description:
            'Worker node resource threshold exceeded.',
          state: 'completed',
        },
        {
          time: '15:25',
          title: 'Investigation completed',
          description:
            'Resource exhaustion confirmed.',
          state: 'completed',
        },
        {
          time: '15:40',
          title: 'Remediation completed',
          description:
            'Worker capacity restored.',
          state: 'completed',
        },
        {
          time: '16:05',
          title: 'Incident verified',
          description:
            'Cluster resource metrics returned to healthy levels.',
          state: 'completed',
        },
      ],
    },

    rca: {
      status: 'completed',
      rootCause: 'Worker node resource exhaustion',
      confidence: '97%',
      evidence:
        'Node resource metrics and worker failures confirm resource exhaustion.',
      historicalContext:
        'The cluster previously experienced elevated worker resource usage.',
      recommendedAction:
        'Restore worker capacity and rebalance workload.',
    },

    remediation: {
      status: 'completed',
      action:
        'Restore worker capacity and rebalance cluster workload.',
      risk: 'Low',
      executionState: 'Completed',
      result:
        'Worker capacity restored successfully.',
    },

    approval: {
      status: 'completed',
      message:
        'Remediation approved and executed successfully.',
      approvedBy: 'Incident Operator',
      timestamp: '15:42',
    },

    verification: {
      status: 'completed',
      recoveryStatus: 'Recovered',
      recoveryMetrics:
        'CPU and memory utilization returned to normal range.',
      result: 'Incident successfully verified as resolved.',
      nextStep: 'No further action required.',
    },
  },
}

export function getIncidentWorkflow(
  incidentId: string,
  incidentStatus: IncidentStatus,
): IncidentWorkflow {
  const workflow = incidentWorkflows[incidentId]

  if (workflow) {
    return workflow
  }

  return {
    currentPhase:
      incidentStatus === 'resolved'
        ? 'resolved'
        : 'investigation',

    investigation: {
      status: 'pending',
      progress: 0,
      completedAgents: 0,
      totalAgents: 4,
      agents: [],
      evidence: {
        logs: 'Pending',
        metrics: 'Pending',
        database: 'Pending',
        network: 'Pending',
      },
      findings: {
        logs: 'Pending',
        metrics: 'Pending',
        database: 'Pending',
        network: 'Pending',
      },
      timeline: [],
    },

    rca: {
      status: 'pending',
      rootCause: 'Pending',
      confidence: 'Not available',
      evidence: 'Pending',
      historicalContext: 'Pending',
      recommendedAction: 'Pending',
    },

    remediation: {
      status: 'pending',
      action: 'Pending',
      risk: 'Not assessed',
      executionState: 'Not started',
      result: 'Pending',
    },

    approval: {
      status: 'pending',
      message: 'Pending',
      approvedBy: '—',
      timestamp: '—',
    },

    verification: {
      status: 'pending',
      recoveryStatus: 'Pending',
      recoveryMetrics: 'Pending',
      result: 'Pending',
      nextStep: 'Pending',
    },
  }
}