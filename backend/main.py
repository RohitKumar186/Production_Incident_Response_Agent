from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from backend.api.incidents import router as incidents_router
from backend.api.investigations import router as investigations_router
from backend.api.rca import router as rca_router
from backend.api.remediation import router as remediation_router
from backend.api.approval import router as approval_router
from backend.api.execution import router as execution_router
from backend.api.verification import router as verification_router


app = FastAPI(
    title="Production Incident Response Agent",
    description="PIRA Backend API",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# API ROUTERS
# =========================================================

app.include_router(incidents_router)
app.include_router(investigations_router)
app.include_router(rca_router)
app.include_router(remediation_router)
app.include_router(approval_router)
app.include_router(execution_router)
app.include_router(verification_router)


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():
    return {
        "service": "Production Incident Response Agent",
        "status": "running",
        "version": "1.0.0",
    }