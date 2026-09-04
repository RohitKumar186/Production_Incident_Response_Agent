It is written for the current state of our project, where the e-commerce application is included inside the repository and the real integration is already working.

# Production Incident Response Agent

A multi-agent AI system for detecting, investigating, diagnosing, and recovering from production incidents.

## Architecture

```text
Production Application
        ↓
Incident / Alert
        ↓
Incident Response Agent
        ↓
┌──────────┬──────────┬──────────┬──────────┐
↓          ↓          ↓          ↓
Logs     Metrics    Database   Network
Agent     Agent      Agent      Agent
└──────────┴──────────┴──────────┴──────────┘
        ↓
Investigation Knowledge Card
        ↓
RCA + RAG
        ↓
Recommended Fix
        ↓
Human Approval
        ↓
Execute
        ↓
Verify
        ↓
Resolved / Re-investigate
Project Overview

The Production Incident Response Agent is designed to automatically investigate production incidents using multiple specialized investigation agents.

The current system supports both:

A simulated production environment for development and testing
A real integration with the included e-commerce application

The investigation system collects evidence from application logs, metrics, database diagnostics, and network connectivity, then produces a structured Investigation Knowledge Card for the next stage of the incident-response pipeline.

Project Structure
production-incident-response/
│
├── agents/
│   ├── logs_agent.py
│   ├── metrics_agent.py
│   ├── database_agent.py
│   └── network_agent.py
│
├── contracts/
│   └── knowledge_card.json
│
├── data/
│   ├── logs.json
│   ├── metrics.json
│   ├── database.json
│   ├── network.json
│   ├── deployments.json
│   └── knowledge_card.json
│
├── models/
│   └── schemas.py
│
├── orchestration/
│   └── investigation.py
│
├── simulation/
│   ├── environment.py
│   └── incident_generator.py
│
├── tools/
│   ├── log_tool.py
│   ├── metrics_tool.py
│   ├── database_tool.py
│   ├── network_tool.py
│   ├── git_tool.py
│   ├── kubernetes_tool.py
│   ├── ecommerce_monitor.py
│   ├── ecommerce_metrics_tool.py
│   ├── ecommerce_log_tool.py
│   └── ecommerce_network_tool.py
│
├── tests/
│
├── ecommerce-application/
│   └── Target e-commerce production application
│
├── requirements.txt
├── .gitignore
└── README.md
Investigation Agents
Logs Agent

Investigates application logs for relevant errors and request activity.

For the real e-commerce application, it reads the application's runtime log file and identifies Order API activity.

Metrics Agent

Investigates service performance metrics such as:

API latency
Baseline latency
Error rate
CPU metrics when available
HTTP status

For the real e-commerce application, the agent measures actual Order API response latency.

Database Agent

Investigates database health and query performance.

The real e-commerce application currently uses an H2 database during local execution. A diagnostic endpoint exposes database health, query latency, and order information to the Incident Response Agent.

Network Agent

Checks whether the target application is reachable and measures application connectivity latency and packet loss.

Investigation Knowledge Card

The Investigation Knowledge Card is the main output of the investigation stage and acts as the handoff between the investigation agents and the RCA/recovery pipeline.

It contains:

Incident information
Investigation findings
Evidence
Agent confidence
Overall investigation confidence
Investigation status

The schema is defined in:

contracts/knowledge_card.json

A generated Knowledge Card is stored at:

data/knowledge_card.json
Incident Simulation

The project includes a simulation environment that can generate production-style incidents without requiring the real e-commerce application.

The simulation can generate:

Incident information
Application logs
Metrics
Database information
Network information
Deployment information
Kubernetes information

Example simulated incident:

Normal API
    ↓
Latency Spike
    ↓
Incident Generated
    ↓
Investigation Agents
    ↓
Structured Findings
    ↓
Knowledge Card
Target E-commerce Application

This repository contains a modified copy of the open-source e-commerce application:

https://github.com/ttulka/ddd-example-ecommerce-microservices

The application is located at:

ecommerce-application/

It is used as the target production application for testing and demonstrating the Incident Response Agent.

The original project's license is preserved at:

ecommerce-application/LICENSE

The original project is distributed under the MIT License.

Real E-commerce Integration

The Incident Response Agent can communicate with the included e-commerce application through its HTTP API.

The current integration supports:

Real Order API latency measurement
Real application log investigation
Real database diagnostics
Real application connectivity checks
Latency fault injection
Automatic incident creation
Multi-agent investigation
Investigation Knowledge Card generation

The e-commerce application runs locally on:

http://localhost:8080
Incident Fault Injection

The e-commerce application contains a controlled fault-injection mechanism for reproducing an API latency incident.

Enable the latency incident:

POST /order/incident/latency/on

Disable the latency incident:

POST /order/incident/latency/off

When enabled, requests to:

POST /order

experience an artificial delay.

This allows the Incident Response Agent to reproduce and investigate a production-style API latency incident in a controlled development environment.

End-to-End Incident Flow

When the latency fault is enabled, the complete system works as follows:

E-commerce Order API
        ↓
Latency increases
        ↓
Real E-commerce Monitor
        ↓
Incident Detected
        ↓
INC-001 Created
        ↓
┌─────────────── Investigation ───────────────┐
│                                             │
│   Logs Agent                                │
│   Metrics Agent                             │
│   Database Agent                            │
│   Network Agent                             │
│                                             │
└─────────────────────────────────────────────┘
        ↓
Structured Findings
        ↓
Overall Confidence
        ↓
Knowledge Card
        ↓
RCA / Recovery Pipeline
Python Setup

The Incident Response Agent requires Python.

From the project root, create a virtual environment:

python -m venv .venv

Activate the environment:

.\.venv\Scripts\Activate.ps1

Install the required dependencies:

pip install -r requirements.txt
Running the E-commerce Application

The included e-commerce application uses Gradle and Java 21.

Go to:

ecommerce-application/

Then run:

.\gradlew :application:bootRun

The application will start on:

http://localhost:8080
Running the Incident Response Agent

From the root of the Production Incident Response project:

$env:PYTHONPATH="D:\Projects\production-incident-response"

Then run:

.\.venv\Scripts\python.exe orchestration\investigation.py

The agent will:

Monitor the e-commerce Order API.
Measure the current latency.
Compare it with the baseline.
Detect an incident if the latency crosses the threshold.
Create an incident object.
Run the investigation agents.
Collect structured evidence.
Calculate investigation confidence.
Generate the Investigation Knowledge Card.
Example Incident Detection

A successful real integration run can produce output similar to:

PRODUCTION INCIDENT RESPONSE
==================================================
Monitoring real e-commerce application...

E-COMMERCE MONITOR RESULT
==================================================
Status            : 201
Baseline          : 320.0 ms
Current Latency   : 2230.97 ms
Increase          : 597.18%
Incident Detected : True
Successful        : True

🚨 INCIDENT DETECTED
==================================================
Incident ID       : INC-001
Service           : order-api
Severity          : HIGH

Starting investigation agents...

INVESTIGATION COMPLETE
==================================================
Status            : SUCCESS
Findings          : 5
Overall Confidence: 0.96

The exact latency and number of findings can vary between runs.

Knowledge Card Output

After an investigation, the generated Knowledge Card is written to:

data/knowledge_card.json

The Knowledge Card contains the incident, findings, evidence, and confidence information required by the next stage of the system.

Example structure:

{
  "schema_version": "1.0",
  "incident_id": "INC-001",
  "correlation_id": "INC-001",
  "producer": "investigation",
  "consumer": "rca",
  "status": "SUCCESS",
  "payload": {
    "incident": {},
    "findings": [],
    "overall_confidence": 0.96
  }
}
Testing

Run the Python test suite from the project root:

.\.venv\Scripts\python.exe -m pytest

The test suite covers:

Data models
Knowledge Card schema
Simulation
Investigation tools
Investigation agents
Orchestration
Development Modes
Simulation Mode

Simulation mode allows the investigation system to be tested without running the e-commerce application.

It generates controlled incident data and investigation evidence.

Real Application Mode

Real application mode connects the Incident Response Agent to the included e-commerce application.

The current real integration uses:

E-commerce Application
        ↓
HTTP API
        ↓
Incident Response Tools
        ↓
Investigation Agents
        ↓
Knowledge Card
Future Extensions

The architecture is designed to support real production infrastructure in future versions.

Potential integrations include:

Production application logs
Monitoring platforms
Real databases
Network telemetry
Git repositories
Kubernetes clusters
RAG-based incident history
Root Cause Analysis
Automated remediation
Human approval workflows
Post-remediation verification
License

This repository contains an open-source e-commerce application from:

https://github.com/ttulka/ddd-example-ecommerce-microservices

The original MIT License and copyright notice are preserved in:

ecommerce-application/LICENSE

Third-party dependencies used by the e-commerce application may have their own licenses.


**One correction from my earlier version:** I intentionally removed the old “Recommended Directory Structure” and “clone the e-commerce application separately” instructions, because those are now obsolete.

After you paste this into `README.md` and save it, **🟠 Terminal 3**:

```powershell
git add README.md

Then we can move on to the final staged-file verification.