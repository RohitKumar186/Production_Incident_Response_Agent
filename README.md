# Production Incident Response Agent (PIRA)
A multi-agent incident-response platform for investigating simulated production incidents, producing evidence-backed root-cause analysis, managing human-approved remediation, and verifying recovery.

PIRA brings together the incident-processing pipeline in TASK1–TASK6, a FastAPI + PostgreSQL backend, and a React + TypeScript frontend. The goal is to make an incident's journey visible and auditable—from creation and investigation through diagnosis, remediation approval, execution, and verification.
Table of Contents
1. Project at a Glance
2. Problem Statement
3. Objectives
4. System Architecture
5. End-to-End Workflow
6. Task-wise Module Details
7. Backend Architecture
8. Frontend Architecture
9. Data and Persistence
10. Technology Stack
11. Prerequisites
12. Environment Configuration
13. Database Setup
14. Installation and Local Setup
15. Running the Application
16. Using the Frontend
17. API Documentation and Main Endpoints
18. Testing and Validation
19. Troubleshooting
20. Security and Operational Safety
21. Known Development Notes
22. Future Improvements
23. Contributing
24. License
    
### 1. Project at a Glance
Item	Description
Project name	Production Incident Response Agent (PIRA)
Application type	Multi-agent incident response and recovery workflow
Backend	Python, FastAPI, Pydantic
Database	PostgreSQL
Frontend	React, TypeScript, Vite
Agent pipeline	TASK1 through TASK6
API documentation	FastAPI Swagger UI / OpenAPI
Main workflow	Incident → Investigation → RCA → Remediation Proposal → Human Approval → Execution → Verification
Intended environment	Local development, demonstration, and simulated incidents


What PIRA does
PIRA structures incident response into explicit stages. Investigation agents collect findings from logs, metrics, database diagnostics, and network checks. The investigation output is passed to the root-cause analysis stage, which can retrieve relevant historical incidents and runbook knowledge. A remediation proposal is then presented for human review. After approval, the system records or performs the configured remediation workflow and evaluates the result through verification.

The frontend displays incident details and stage statuses so an operator can see what has completed and what remains pending.
Important distinction: Approval, execution, and verification are different states. An approved proposal does not, by itself, prove that remediation was executed or that the service recovered.

### 2. Problem Statement
Production incidents can involve multiple interacting symptoms: increased API latency, database timeouts, network degradation, application errors, or infrastructure failures. Investigating these symptoms manually can be slow, fragmented, and difficult to audit.

PIRA addresses this by organizing investigation work across specialized agents, consolidating findings and evidence, retrieving relevant knowledge, and carrying the incident through a structured response workflow. Human approval is kept as an explicit gate before a proposed remediation is accepted.

This repository demonstrates that workflow in a controlled development environment. It should not be treated as a fully autonomous production operator without additional deployment hardening, permissions, safeguards, and validation.


### 3. Objectives
- Create and track incidents with a consistent identifier and severity.
- Simulate or represent production-style faults.
- Delegate investigation to focused agents for logs, metrics, database, and network evidence.
- Aggregate investigation results into a structured handoff.
- Use retrieval-augmented knowledge to support root-cause analysis.
- Produce a root cause, confidence value, contributing factors, and a recommended action.
- Record remediation proposals and their approval status.
- Keep human approval separate from execution.
- Record execution and verification outcomes.
- Persist incident workflow records in PostgreSQL.
- Provide a dashboard for reviewing incidents and their response progress.
- Make the API inspectable through Swagger UI.

  
### 4. System Architecture
                         OPERATOR
                            |
                            v
                React + TypeScript Frontend
                   Dashboard / Incident Detail
                            |
                     HTTP / JSON API
                            |
                            v
                    FastAPI Application
                      backend/main.py
                            |
           +----------------+----------------+
           |                |                |
           v                v                v
     Incident API     Investigation API    RCA API
           |                |                |
           |                v                |
           |          PIRA Service            |
           |                |                 |
           |                v                 |
           |       TASK1 / TASK2 / TASK3       |
           |                |                 |
           |                v                 |
           |       Investigation findings     |
           |                |                 |
           |                +-------> TASK4   |
           |                           RAG + RCA
           |                              |
           +------------------------------+
                                          |
                                          v
                                Remediation Proposal
                                          |
                                          v
                                    Approval API
                                          |
                                          v
                                    Execution API
                                          |
                                          v
                                  Verification API
                                          |
                                          v
                               PostgreSQL + Audit Trail
Main architectural layers
1. User interface

The React application allows the operator to browse incidents, open incident details, inspect investigation/RCA data, review remediation, approve or reject proposals, and view verification/recovery status.

2. API layer

FastAPI exposes HTTP endpoints and validates request and response bodies with Pydantic schemas. The application registers route modules from backend/api/.

3. Orchestration and service layer

backend/services/pira_service.py coordinates the investigation and RCA work called from the incident flow. backend/orchestrator/pira_orchestrator.py contains backend orchestration logic.

4. Agent and knowledge pipeline

The TASK1–TASK6 packages separate simulation, investigation tools, agents, knowledge retrieval, RCA, remediation, and verification.

5. Persistence layer

The backend's PostgreSQL connection module is backend/database/connection.py. API modules read and write incident and workflow data to database tables.
5. End-to-End Workflow


### The normal operator journey is:
Stage 1 — Incident creation
An incident is created with an identifier, service, incident type, severity, title, description, timestamp, and optional metadata. The backend stores the incident and begins the investigation workflow.
Stage 2 — Investigation
The investigation pipeline gathers evidence from specialized agents:
- Logs Agent: searches logs for relevant errors and request activity.
- Metrics Agent: examines latency, error rates, and service performance measurements.
- Database Agent: checks database-related symptoms such as query performance or timeout evidence.
- Network Agent: checks connectivity and network-latency evidence.
The results are aggregated into findings and evidence, including confidence values where supplied by the underlying tool or agent.
Stage 3 — Root Cause Analysis (RCA)
The RCA stage consumes the investigation output. The TASK4 RAG components retrieve potentially relevant historical incidents, runbooks, and knowledge records. The analyzer uses the available evidence and retrieved context to produce a root-cause result and a recommended action.

RAG context is supporting information, not proof by itself; RCA quality depends on the input evidence and the relevance of retrieved records.
Stage 4 — Remediation proposal
The system stores a proposal with an action, rationale, risk level, proposer, approval status, and execution status. A newly created proposal normally begins in a pending approval state and has not yet been executed.
Stage 5 — Human approval
An operator reviews the proposal and approves or rejects it. The approval record should identify the proposal and the decision. Do not approve a proposal merely because the incident page is showing an approval button; first review the action and rationale.
Stage 6 — Execution
After approval, the execution stage records the outcome of the configured remediation. In this repository, the task pipeline includes simulated execution components. A successful approval response is not equivalent to successful execution.
Stage 7 — Verification and recovery
Verification checks the post-remediation state and records the verification/recovery result. The incident should only be treated as recovered when the verification result supports that conclusion.
Workflow state summary
Stage	Main output	What to verify
Incident	Incident record and ID	Correct incident is visible
Investigation	Findings and evidence	Agents completed; evidence is available
RCA	Root cause and recommended action	RCA response is valid and relevant
Remediation	Proposal record	Proposal ID belongs to the same incident
Approval	Approval decision	Status changed to approved or rejected
Execution	Execution record/result	Execution actually ran and returned a result
Verification	Verification/recovery result	Recovery is supported by the verification outcome





### 6. Task-wise Module Details
The project separates pipeline responsibilities across TASK1–TASK6. The descriptions below reflect the modules present in the repository snapshot.
TASK1 — Incident Simulation and Models
Purpose: represent incidents and generate controlled incident/simulation inputs.

Notable areas:
- TASK1/generator/incident_generator.py — incident generation.
- TASK1/generator/runner.py — generator execution support.
- TASK1/generator/scheduler.py — scheduling-related logic.
- TASK1/models/ — incident, alert, fault, and schema models.
- TASK1/simulator/infrastructure.py — simulated infrastructure.
- TASK1/simulator/state.py — simulation state.
- TASK1/data/ — sample logs, metrics, database, and network data.
- TASK1/tests/ — tests for incident types, scheduling, and integration.
Role in the pipeline: provide a consistent incident and environment context for later investigation stages.

### TASK2 — Investigation Agents
Purpose: investigate the incident from multiple diagnostic perspectives.

Notable areas:
- TASK2/agents/logs_agent.py
- TASK2/agents/metrics_agent.py
- TASK2/agents/database_agent.py
- TASK2/agents/network_agent.py
- TASK2/aggregator/evidence_aggregator.py
- TASK2/investigator/investigator.py
- TASK2/orchestrator/investigation.py
- TASK2/models/ — investigation and adapter schemas.
- TASK2/tests/ — tests for individual agents and investigation orchestration.
Role in the pipeline: gather findings from the available tools and combine them into an investigation result.


### TASK3 — Tools and Data Layer
Purpose: provide the diagnostic tools called by the agents and their local data sources.

Notable areas:
- TASK3/tools/log_search.py and TASK3/tools/logs.py
- TASK3/tools/metrics_reader.py and TASK3/tools/metrics.py
- TASK3/tools/database_reader.py and TASK3/tools/database.py
- TASK3/tools/network_checker.py and TASK3/tools/network.py
- TASK3/tools/infrastructure.py
- TASK3/tools/registry.py
- TASK3/models/tool_schemas.py
- TASK3/data/ — sample diagnostic data.
- TASK3/tests/test_tools.py
Role in the pipeline: give investigation agents a consistent way to read or query evidence. The JSON data in this layer is local diagnostic data for the configured pipeline; it should not be described as live production telemetry unless connected to a real source.


### TASK4 — Retrieval-Augmented Generation and RCA
Purpose: enrich the investigation with relevant knowledge and produce root-cause analysis.

Notable areas:
- TASK4/rag/knowledge_base.py — knowledge-base support.
- TASK4/rag/retriever.py — retrieval logic.
- TASK4/rca/analyzer.py — RCA analysis.
- TASK4/orchestrator/investigation.py — investigation/RCA orchestration.
- TASK4/models/schemas.py — data schemas.
- TASK4/data/knowledge.json — knowledge records.
- TASK4/tests/test_task4.py — tests for the RCA stage.
Role in the pipeline: use investigation findings together with relevant stored knowledge to produce a structured root-cause result. Retrieved context may include previous incidents and runbook material.


### TASK5 — Remediation Planning, Approval, and Execution
Purpose: turn a recommended action into a reviewable proposal and controlled execution flow.

Notable areas:
- TASK5/planner/planner.py — remediation planning.
- TASK5/orchestrator/remediation.py — remediation orchestration.
- TASK5/orchestrator/task4_adapter.py — adapter from the RCA/investigation output.
- TASK5/approval/approval.py — approval logic.
- TASK5/approval/cli.py — command-line approval support.
- TASK5/execution/simulator.py — simulated execution.
- TASK5/models/schemas.py — remediation schemas.
- TASK5/tests/ — remediation and adapter tests.
Role in the pipeline: propose an action, require a decision, and then pass approved work through the configured execution path.

### TASK6 — Verification
Purpose: evaluate whether the incident response achieved the expected outcome.

Notable areas:
- TASK6/verification/verifier.py — verification logic.
- TASK6/orchestrator/verification.py — verification orchestration.
- TASK6/models/schemas.py — verification schemas.
- TASK6/tests/test_task6.py — verification tests.
- TASK6/demo.py — demonstration entry point.
Role in the pipeline: create a separate verification outcome so the system can distinguish “approved” or “executed” from “recovered.”
Integration layer
The integration/ directory contains adapters that connect the task packages:
- integration/task1_to_task2.py
- integration/task4_to_task5.py
- integration/task4_to_task6.py
- integration/task5_to_task6.py
- integration/runtime_data/ — runtime diagnostic JSON.
These adapters are intended to keep data handoffs between task modules explicit rather than making every task depend directly on every other task.

### 7. Backend Architecture
The FastAPI application entry point is backend/main.py. It creates the application and registers route modules for incidents, investigations, RCA, remediation, approval, execution, and verification.
Backend directory
backend/
├── api/
│   ├── incidents.py
│   ├── investigations.py
│   ├── rca.py
│   ├── remediation.py
│   ├── approval.py
│   ├── execution.py
│   └── verification.py
├── database/
│   └── connection.py
├── orchestrator/
│   └── pira_orchestrator.py
├── schemas/
│   ├── incident.py
│   ├── investigation.py
│   ├── rca.py
│   ├── remediation.py
│   ├── approval.py
│   ├── execution.py
│   └── verification.py
├── services/
│   └── pira_service.py
└── main.py
Responsibilities
- API routes: receive HTTP requests, validate payloads, call services or persistence logic, and return structured responses.
- Schemas: define accepted request fields and expected response shapes.
- Service/orchestration modules: coordinate the task pipeline and business workflow.
- Database connection: creates PostgreSQL connections for the API modules.
- Audit records: the incident API writes audit events for important lifecycle actions; related workflow tables hold the stage-specific records.
API error handling
An HTTP 4xx response generally means the request or referenced resource could not be accepted or found. An HTTP 5xx response means the server failed while processing the request. When debugging:
1. Inspect the failing request in browser DevTools → Network.
2. Read the response body.
3. Check the backend terminal traceback.
4. Compare the payload to the schema in Swagger.
5. Verify that the incident ID and proposal ID belong to the same record.
8. Frontend Architecture
The frontend is a React + TypeScript application built with Vite. It communicates with the backend through API client modules.
Main frontend files
frontend/src/
├── api/
│   ├── client.ts
│   ├── incidents.ts
│   ├── investigation.ts
│   ├── rca.ts
│   ├── remediation.ts
│   └── verification.ts
├── components/
│   ├── dashboard/
│   │   ├── IncidentStatusBadge.tsx
│   │   ├── IncidentTable.tsx
│   │   └── StatCard.tsx
│   ├── investigation/
│   │   └── InvestigationPanel.tsx
│   ├── layout/
│   │   ├── AppShell.tsx
│   │   ├── Header.tsx
│   │   └── Sidebar.tsx
│   ├── rca/
│   │   └── RCASection.tsx
│   └── remediation/
│       └── RemediationSection.tsx
├── pages/
│   ├── Dashboard.tsx
│   ├── History.tsx
│   ├── IncidentDetails.tsx
│   └── Incidents.tsx
├── types/
│   └── incident.ts
└── App.tsx
UI responsibilities
- Dashboard / Incidents: browse and select incidents.
- Incident details: show incident metadata and the response workflow stages.
- Investigation panel: display investigation status, findings, and evidence.
- RCA section: show root cause and supporting analysis.
- Remediation section: show proposal details and approval controls.
- Verification section: display verification and recovery information.
- API clients: centralize HTTP calls so the UI does not need to duplicate endpoint details.
API base URL
The frontend API client uses the environment variable VITE_API_BASE_URL when configured and otherwise defaults to http://localhost:8000 in the current source snapshot.

If the backend runs on a different host or port, set a local environment file at frontend/.env:
VITE_API_BASE_URL=http://localhost:8000
Restart Vite after changing the environment.

### 9. Data and Persistence
PostgreSQL
The backend uses PostgreSQL via backend/database/connection.py. The current workflow refers to tables for the following kinds of data:
Data area	Purpose
incidents	Incident identity, metadata, severity, service, and status
investigations	Investigation stage records
evidence	Evidence associated with an investigation
rca_results	Root cause, confidence, contributing factors, and recommended action
remediation_proposals	Proposed action, rationale, risk, approval status, and execution status
approvals	Human approval decision records
remediation_executions	Execution records and results
verification_results	Verification and recovery outcomes
agent_runs	Agent stage inputs, outputs, and status
audit_logs	Lifecycle and workflow audit events
historical_incidents	Historical incident knowledge used by retrieval workflows


The exact table names and required columns must match the database schema used by your local instance. This README does not replace the schema or migration SQL.
Local JSON data
TASK1/data/, TASK2/data/, TASK3/data/, TASK4/data/, and integration/runtime_data/ contain JSON data used by different task components. These files provide local/simulated incident evidence and knowledge. If a tool is configured to read these files, it is not automatically querying a live production service.
Data consistency
- Use the same incident ID across the stages of a workflow.
- Use the remediation proposal ID returned by the API; do not guess it or reuse another incident's ID.
- Keep contributing_factors and other structured JSON fields consistent with the Pydantic response schema.
- Inspect the API response after every state-changing action.


### 10. Technology Stack
Technology	Use
Python	Agent logic, orchestration, and backend
FastAPI	REST API and Swagger/OpenAPI
Pydantic	Request and response validation
PostgreSQL	Persistent workflow records
Psycopg2	PostgreSQL driver
React	Frontend UI
TypeScript	Frontend type safety
Vite	Frontend development server and build tooling
Axios	HTTP API calls
Pytest	Python test runner
JSON	Local simulated evidence and knowledge data


Versions should be taken from the project’s maintained dependency files and package lock. Avoid mixing globally installed packages with the project's virtual environment.

### 11. Prerequisites
Install:
1. Python — Python 3.11+ recommended; the development environment has also used Python 3.13.
2. Node.js and npm — required for the frontend.
3. PostgreSQL — required by the API database layer.
4. Git — required to clone and manage the repository.
5. VS Code or another editor — recommended for local development.
Verify installations:
python --version
node --version
npm --version
git --version
psql --version
The last command requires PostgreSQL command-line tools to be installed and on PATH.

### 12. Environment Configuration
The backend database connection uses environment variables for host, port, database name, username, and password. Check backend/database/connection.py in your current branch for the exact defaults and connection behavior.

Example PowerShell configuration for the current terminal:
$env:DB_HOST = "localhost"
$env:DB_PORT = "5432"
$env:DB_NAME = "pira_db"
$env:DB_USER = "postgres"
$env:DB_PASSWORD = "YOUR_LOCAL_POSTGRES_PASSWORD"
Replace the placeholder with your own local password. These variables only apply to the current PowerShell session unless you configure them elsewhere.
Secrets policy
- Never commit a real database password, API key, token, or private connection string.
- Use local environment variables or a local .env file if supported by your configuration.
- Keep .env files out of version control.
- If a secret has been committed publicly, rotate it; deleting the text from the latest file alone is not enough to invalidate it.

### 13. Database Setup
1. Start the PostgreSQL service.
2. Create a database, for example pira_db, if one does not already exist.
3. Configure the backend environment variables.
4. Ensure the required schema and tables exist.
5. Start the backend and inspect the API root or Swagger UI.
The repository snapshot used for this README did not provide a single confirmed root-level migration script that can safely create every current backend table. Therefore, do not assume that creating an empty database is sufficient. Use the schema already used by your working environment or the team's authoritative SQL setup. The application may raise database errors if tables or columns are missing.

A successful HTTP server startup only confirms that FastAPI has started; it does not guarantee that every database operation will work. Verify a read/write flow against the configured database.

### 14. Installation and Local Setup
14.1 Clone the repository
git clone https://github.com/RohitKumar186/Production_Incident_Response_Agent.git
cd Production_Incident_Response_Agent
If you are using the main branch:
git switch main
git pull origin main
14.2 Create a Python virtual environment
From the repository root:
python -m venv .venv
.\.venv\Scripts\Activate.ps1
If PowerShell blocks activation, use an allowed local activation policy or run the virtual environment's Python executable directly.
14.3 Install backend dependencies
The uploaded repository snapshot did not contain a single consolidated root-level backend requirements.txt. If your current branch has a maintained backend dependency file, use it. Otherwise, a starting set of core API dependencies is:
python -m pip install --upgrade pip
python -m pip install fastapi "uvicorn[standard]" psycopg2-binary pydantic python-dotenv pytest
The full task pipeline may require additional packages. If an import error identifies a missing dependency, install the package specified by the relevant task's requirements file rather than guessing at a version. Prefer a consolidated, pinned dependency file for repeatable setup.
14.4 Install frontend dependencies
Open a separate terminal:
cd frontend
npm install
npm install uses frontend/package.json and the committed lock file to install the frontend dependencies.

### 15. Running the Application
Run the backend and frontend in separate terminals.
Terminal A — Backend
From the repository root, activate the virtual environment and set database environment variables, then run:
python -m uvicorn backend.main:app --reload
The default local API URL is:
http://127.0.0.1:8000
The application root is:
http://127.0.0.1:8000/
A successful root response should identify the service as Production Incident Response Agent and report its running status and version.
Terminal B — Frontend
From the repository root:
cd frontend
npm run dev
Vite prints the actual local URL in the terminal. It is commonly:
http://localhost:5173
Open the URL printed by Vite in the browser.
Stop the development servers
Press Ctrl+C in each terminal to stop its server.

### 16. Using the Frontend
1. Confirm PostgreSQL is running and the database schema exists.
2. Start the backend.
3. Open the Swagger page once to confirm the API starts.
4. Start the frontend in another terminal.
5. Open the frontend URL printed by Vite.
6. Navigate to the incidents page.
7. Create a new synthetic test incident.
8. Open the generated incident details page.
9. Review investigation progress, agents, findings, and evidence.
10. Review the RCA root cause, confidence, contributing factors, and recommended action.
11. Review the remediation proposal, its rationale, and risk level.
12. Approve or reject the proposal as an authorized human reviewer.
13. Check the execution result separately.
14. Check verification and recovery status separately.
Suggested demo scenario
A useful demonstration scenario is an API latency incident affecting order-api.

Example display values (adjust to the fields shown by the form):
Field	Example
Service	order-api
Incident type	LATENCY
Severity	High
Title	E2E Test - API latency increased
Description	Synthetic test incident for validating the PIRA workflow.


These values are a demo example, not evidence of a live outage.
Evidence to capture for a project demo
- Incident details page after creation.
- Investigation stage showing completion and findings.
- RCA section with root cause and recommended action.
- Remediation proposal and pending approval.
- Approval outcome.
- Execution result.
- Verification/recovery result.
Keep the incident ID visible in screenshots so the stages can be shown to refer to the same incident.

 
### 17. API Documentation and Main Endpoints
FastAPI automatically provides interactive API documentation when the backend is running:
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- OpenAPI JSON: http://127.0.0.1:8000/openapi.json
- Root endpoint: http://127.0.0.1:8000/
The registered backend route groups are:
Route group	Purpose
/api/incidents	Create and retrieve incidents
/api/investigations	Access investigation results
/api/rca	Create or retrieve root-cause analysis results
/api/remediation	Create and retrieve remediation proposals
/api/approval	Handle remediation approval decisions
/api/execution	Access remediation execution operations/results
/api/verification	Access verification results


Use Swagger as the source of truth for exact HTTP methods, path parameters, request payloads, and response schemas. The specific endpoints and schemas can evolve with the code. Do not guess an approval or execution request body.
Example: inspect an existing proposal
The current remediation API includes a GET route that takes an incident ID:
GET /api/remediation/{incident_id}
For example, in Swagger, use INC-API-TEST-003 only if you want to inspect that existing development incident. Replace it with the incident ID you are actually testing.

A response of [] means no remediation proposal was returned for that incident. Before trying approval, create or locate the correct proposal and use the id returned by the API.
Example: API debugging checklist
1. Open browser DevTools → Network.
2. Trigger the UI action once.
3. Select the relevant Fetch/XHR request.
4. Inspect Request URL, Request Method, Status, Payload, and Response.
5. If the response is 4xx or 5xx, inspect the backend terminal output.
6. Confirm the incident ID and proposal ID match.
7. Refresh the incident page after successful state changes.


### 18. Testing and Validation
Run all discovered tests
From the repository root:
python -m pytest -q
Run with verbose test names:
python -m pytest -v
Run a focused test file or folder:
python -m pytest TASK3/tests -q
python -m pytest TASK2/tests -q
Run a single test file:
python -m pytest TASK3/tests/test_tools.py -q
Run tests from the repository root so Python package imports are resolved consistently.
Manual end-to-end validation
The UI workflow can also be tested manually:
- Create a new incident.
- Confirm investigation and RCA data are returned.
- Confirm a remediation proposal exists for the same incident.
- Approve the proposal through the frontend.
- Confirm the execution status changes as expected.
- Confirm verification and recovery results.
- Check the backend/database records if a UI status appears inconsistent.
Manual testing and automated unit/integration testing are different forms of evidence. Record their results separately.


### 19. Troubleshooting
ModuleNotFoundError while collecting tests
Run tests from the repository root and check the import paths used by the tests. This repository contains legacy test imports that expect different package layouts, such as direct generator/simulator imports or a TASK1.simulation package. Do not rename modules or change Task 1–3 logic blindly to make collection pass; first determine the intended package structure and the test's expected entry point.
python -m pytest backend -q says no tests ran
That output means pytest did not discover tests in the backend directory. It is not a pass result and does not indicate that backend endpoints are broken. Use the repository's actual test modules and manual API checks until backend tests are added.
Backend starts but an API returns HTTP 500
- Read the traceback in the terminal running Uvicorn.
- Check the response schema and the actual returned JSON type.
- Check that the database contains the required table and columns.
- Check for a missing import or helper function.
- Re-test the exact endpoint in Swagger after making a focused change.
RCA response validation error for contributing_factors
The API response schema expects contributing_factors to be a list. If legacy database rows contain a dictionary instead, normalize the value during serialization before returning it. Preserve the actual data and shape expected by the API; avoid silently changing unrelated RCA fields.
Remediation GET returns an empty array
A response such as:
[]
means the endpoint found no proposal for that incident ID. Create or locate a proposal for the same incident and verify its returned ID before approval. A proposal for another incident must not be reused.
Frontend says approval failed but Network response is empty
Inspect the request's status, method, URL, payload, and backend terminal output. An empty response body alone is not enough to determine the cause. Confirm whether the request reached the backend and whether the UI is interpreting the result correctly.
Frontend and backend use different ports
Set VITE_API_BASE_URL in frontend/.env, restart Vite, and verify the request URL in DevTools.
Database connection or missing-table errors
Check PostgreSQL service status and the configured database credentials. Confirm that the database schema is initialized. Do not assume that creating an empty database creates all PIRA tables.


### 20. Security and Operational Safety
PIRA should be treated as a development/demo project unless and until production deployment controls are added and reviewed.
- Keep human approval as a real gate for remediation.
- Never point simulated execution at production systems without a security review.
- Use least-privilege credentials for database and infrastructure access.
- Keep secrets out of source control.
- Validate and audit state-changing API requests.
- Log decisions and execution outcomes without exposing passwords or tokens.
- Add authorization to sensitive operations before deploying beyond a trusted local environment.
- Design rollback and failure handling before allowing operational changes.
- Verify recovery from independent signals where possible; do not mark an incident recovered merely because execution returned successfully.

### 21. Known Development Notes
The following notes are based on the development session associated with this project README:
- The frontend was manually exercised with a fresh incident through investigation, RCA, remediation approval, execution, and verification. This was a manual end-to-end check in the development environment, not a claim that every automated test passes.
- An RCA API response validation issue was encountered because a stored contributing_factors value was a dictionary while the response schema expected a list. The serialization function was adjusted to normalize the value.
- A remediation approval issue was investigated by checking the proposal ID and the approval API flow.
- python -m pytest -q reported nine collection errors in legacy TASK1–TASK6 tests, including import errors for generator, simulator, TASK3, TASK1.simulation, and run_scenario.
- python -m pytest backend -q reported no tests ran; there were no discoverable backend tests in that folder in the tested checkout.
- The current project state should therefore be described as manually end-to-end tested in the development UI, with legacy automated test collection errors still requiring cleanup.
These are development-session observations. Re-run the commands on the current branch to confirm whether they still apply.

### 22. Future Improvements
Potential next steps for hardening the project:
1. Add a single authoritative backend dependency file with pinned versions.
2. Add database migrations/schema initialization scripts and document them.
3. Add backend tests for incident creation, RCA serialization, remediation, approval, execution, and verification.
4. Repair legacy TASK1–TASK6 test import paths without altering the task contracts.
5. Add an integration test for the full API lifecycle using a disposable test database.
6. Add authentication and role-based authorization for approval and execution endpoints.
7. Add stronger audit coverage for every state transition.
8. Add structured logging and request correlation IDs across the pipeline.
9. Add consistent error response schemas.
10. Add frontend build/type-check instructions and CI checks.
11. Document environment variables in a .env.example file with placeholders only.
12. Add health/readiness checks for API and database connectivity.
13. Add a controlled rollback/compensation path for failed remediation.
14. Add a clear separation between simulated tools and any real infrastructure connectors.

### 23. Contributing
For a local change:
1. Create a feature branch.
2. Keep changes scoped to one concern.
3. Run relevant tests and manually verify the affected workflow.
4. Check git diff and git status.
5. Commit with a descriptive message.
6. Push the branch and open a pull request for review.
Suggested branch names:
feature/<short-description>
fix/<short-description>
docs/<short-description>
Do not commit local .env files, passwords, tokens, virtual environments, node_modules, build outputs, or generated cache files.

### 24. License
No authoritative root-level license file was confirmed in the repository snapshot used to prepare this README. Check the repository's current license and third-party component requirements before redistributing the project. Do not claim a license that has not been selected by the project owners.
Maintainer Checklist
Before presenting or merging a release, verify:
- [ ] The intended branch contains the latest backend and frontend changes.
- [ ] PostgreSQL setup is documented and the schema is available.
- [ ] Backend starts with the documented command.
- [ ] Frontend starts and calls the expected API URL.
- [ ] A fresh test incident can be created.
- [ ] Investigation and RCA return valid data.
- [ ] A remediation proposal exists for the same incident.
- [ ] Human approval works and is recorded.
- [ ] Execution result is checked separately.
- [ ] Verification/recovery result is checked separately.
- [ ] Automated test results are recorded accurately.
- [ ] No credentials or local secrets are committed.
