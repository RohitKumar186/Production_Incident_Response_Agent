Production Incident Response Agent (PIRA)
PIRA is a multi-agent incident-response project that simulates and investigates production incidents, gathers evidence from specialized agents, produces a root-cause analysis (RCA), proposes remediation, requires human approval, and verifies whether the simulated service has recovered.

The repository combines the TASK1–TASK6 incident-response pipeline with a FastAPI backend and a React + TypeScript frontend.
Contents
- Project overview
- Architecture and workflow
- Repository structure
- Technology stack
- Prerequisites
- Configuration
- Run the backend
- Run the frontend
- Use the application
- API documentation
- Testing
- Current testing note
- Troubleshooting
- Safety note
Project overview
The goal of PIRA is to provide a structured workflow for handling production-style incidents. Rather than relying on a single diagnostic step, the system separates investigation, diagnosis, remediation planning, approval, execution, and verification.

The repository includes:
- Incident simulation and models in TASK1.
- Specialized investigation agents in TASK2.
- Tooling and local JSON data sources in TASK3.
- Retrieval-augmented context and root-cause analysis in TASK4.
- Remediation planning, approval logic, and simulated execution in TASK5.
- Verification logic in TASK6.
- A FastAPI backend that exposes incident-response operations and persists workflow records in PostgreSQL.
- A React, TypeScript, and Vite frontend for incident management and workflow review.
Architecture and workflow
Incident created in the frontend
              |
              v
       FastAPI backend
              |
              v
    Incident / simulation flow
              |
              v
  Investigation agents (TASK2)
   + tools and data (TASK3)
              |
              v
   Investigation findings/evidence
              |
              v
    RAG + Root Cause Analysis
             (TASK4)
              |
              v
       Remediation proposal
             (TASK5)
              |
              v
       Human approval gate
              |
              v
     Simulated remediation execution
              |
              v
       Verification (TASK6)
              |
       +------+------+
       |             |
   Recovered      Not recovered
       |             |
       v             v
  Mark verified   Follow-up /
  and retain      re-investigation
  history
The exact remediation and verification outcome depends on the incident and the simulated environment. Human approval is a distinct stage; approval alone does not prove that execution or recovery succeeded.
Repository structure
Production_Incident_Response_Agent/
├── TASK1/                     # Incident generator, models, simulator
├── TASK2/                     # Logs, metrics, database and network agents
├── TASK3/                     # Investigation tools and local JSON data
├── TASK4/                     # RAG, knowledge retrieval and RCA
├── TASK5/                     # Remediation planner, approval and execution
├── TASK6/                     # Verification workflow and verifier
├── integration/               # Adapters between pipeline stages
│   └── runtime_data/          # JSON data used by integration components
├── backend/
│   ├── api/                   # FastAPI route modules
│   ├── database/              # PostgreSQL connection
│   ├── orchestrator/           # Backend workflow orchestration
│   ├── schemas/               # API request/response schemas
│   ├── services/              # Investigation and RCA service layer
│   └── main.py                # FastAPI application entry point
├── frontend/
│   ├── src/api/               # Frontend API clients
│   ├── src/components/        # Dashboard and workflow components
│   ├── src/pages/             # Dashboard, incidents and details pages
│   └── package.json
├── pytest.ini
└── README.md
Technology stack
- Python for the agent pipeline, orchestration and backend.
- FastAPI for HTTP API endpoints and interactive API documentation.
- PostgreSQL for incident and workflow persistence.
- Psycopg2 for PostgreSQL connectivity.
- Pydantic for request/response validation and data schemas.
- React + TypeScript + Vite for the frontend.
- Axios for frontend HTTP requests.
- Pytest for automated tests.
Prerequisites
Install the following before running the project:
- Python 3.11 or newer (the project has also been exercised in a Python 3.13 environment).
- Node.js and npm.
- PostgreSQL.
- Git, if cloning the repository.
Configuration
PostgreSQL
The backend reads its connection settings from environment variables:
Variable	Default in code	Purpose
DB_HOST	localhost	PostgreSQL host
DB_PORT	5432	PostgreSQL port
DB_NAME	pira_db	Database name
DB_USER	postgres	Database user
DB_PASSWORD	Postgres@123	Database password


Set DB_PASSWORD to your own local password before running the application. Do not commit real credentials to GitHub.

Create the pira_db database (or configure DB_NAME to an existing database) and ensure the application's tables are initialized. The API uses tables including incidents, investigations, rca_results, remediation_proposals, approvals, remediation_executions, verification_results, agent_runs, audit_logs, evidence, and historical_incidents.

The repository snapshot used to prepare this README did not include a single authoritative root-level SQL migration file. Use the schema/setup SQL maintained by your project team or the database already configured for your working environment; do not assume that creating the database alone creates all required tables.

For PowerShell, configure connection values in the current terminal session, for example:
$env:DB_HOST = "localhost"
$env:DB_PORT = "5432"
$env:DB_NAME = "pira_db"
$env:DB_USER = "postgres"
$env:DB_PASSWORD = "YOUR_LOCAL_POSTGRES_PASSWORD"
These values apply to the current PowerShell session. Set them again in a new terminal, or use a local environment-file approach supported by your setup. Keep local secrets out of version control.
Run the backend
From the repository root:
1. Create and activate a virtual environment:
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
2. Install the backend and pipeline dependencies:
   python -m pip install --upgrade pip
   pip install fastapi "uvicorn[standard]" psycopg2-binary "pydantic>=2,<3" python-dotenv faker numpy pytest
   If your team has a maintained dependency/lock file for the complete repository, prefer that file so all contributors use consistent versions. The root-level snapshot used to prepare this README did not contain a consolidated backend requirements.txt.
3. Set the PostgreSQL environment variables described above.
4. Start FastAPI:
   python -m uvicorn backend.main:app --reload
The backend runs at http://127.0.0.1:8000 by default.

The root endpoint GET / returns the service name, running status, and version.
Run the frontend
Open a second terminal and move into the frontend directory:
cd frontend
npm install
npm run dev
Vite prints the local frontend URL in the terminal (commonly http://localhost:5173).

The frontend API client uses VITE_API_BASE_URL when provided, otherwise it defaults to http://localhost:8000. If the backend is running on a different host or port, create a local frontend/.env file containing:
VITE_API_BASE_URL=http://localhost:8000
Restart the Vite development server after changing environment variables.
Use the application
1. Start PostgreSQL and ensure the PIRA database schema is present.
2. Start the backend and confirm it is running.
3. Start the frontend.
4. Open the frontend URL printed by Vite.
5. Create a new test incident from the UI.
6. Review the investigation findings and evidence.
7. Review the root-cause analysis and recommended action.
8. Review the remediation proposal and submit it for human approval.
9. Approve or reject the proposal using the UI.
10. If approved, inspect the execution result and then the verification/recovery status.
For a reliable demo, use a synthetic incident such as an API latency increase on order-api. Verify each stage on the incident details page rather than treating an “approved” state as proof that recovery has completed.
API documentation
With the backend running, open:
- Swagger UI: http://127.0.0.1:8000/docs
- OpenAPI schema: http://127.0.0.1:8000/openapi.json
- Service root: http://127.0.0.1:8000/
The backend route modules cover incident creation and retrieval, investigation, RCA, remediation proposals, approvals, execution records, and verification. The exact request schemas are available in Swagger, which should be treated as the source of truth for the running version.
Testing
Run the test suite from the repository root:
python -m pytest -q
To run a focused test module or folder, pass its path to pytest, for example:
python -m pytest TASK3/tests -q
The project includes tests across TASK1–TASK6. Tests should be run from the repository root so package imports resolve consistently.
Current testing note
In the development session used to prepare this README, python -m pytest -q stopped during test collection with import errors in legacy TASK1–TASK6 tests (including imports for generator, simulator, TASK3, TASK1.simulation, and run_scenario). Running python -m pytest backend -q reported no tests ran, because no backend tests were discovered in that folder. These results do not establish that the full automated suite passes. The frontend-driven end-to-end workflow was manually exercised in the development environment, but the legacy test collection errors remain a separate item to address.
Troubleshooting
Frontend loads but API calls fail
- Confirm FastAPI is running at http://localhost:8000.
- Open http://127.0.0.1:8000/docs to check that the API starts.
- Check VITE_API_BASE_URL and restart Vite after changing it.
- Inspect the browser DevTools Network tab for the failing endpoint and response.
Database connection error
- Confirm PostgreSQL is running.
- Check DB_HOST, DB_PORT, DB_NAME, DB_USER, and DB_PASSWORD.
- Confirm that the database exists and required tables have been created.
- Do not paste database passwords or other secrets into issues or screenshots.
RCA endpoint returns a validation error
Check the response schema and stored JSON shape. In the development session, the RCA API was updated to normalize contributing_factors to a list when stored data contained a dictionary. Keep API serialization consistent with RCAResponse.
Remediation proposal is missing
A GET /api/remediation/{incident_id} response of [] means the endpoint did not find a proposal for that incident. Confirm that a proposal exists for the same incident before attempting approval. Do not reuse a remediation ID from a different incident.
Approval appears successful but verification is pending
Approval, execution, and verification are separate workflow stages. Refresh the incident page and inspect each stage and the backend response. A successful approval response by itself does not establish that remediation execution or service recovery completed.
Safety note
This project is intended for development, demonstration, and simulated incident-response workflows. Review proposed actions and require explicit human approval before any real operational change. Do not connect experimental remediation execution to production infrastructure without security review, authorization controls, auditability, and a tested rollback plan.
License
No root-level license file was confirmed in the repository snapshot used to prepare this README. Add the appropriate license and attribution information if this project will be distributed publicly.
