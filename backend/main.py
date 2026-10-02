from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes.incidents import router as incidents_router

app = FastAPI(
    title="PIRA Backend",
    version="1.0.0",
    description="Production Incident Response Agent API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(incidents_router)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "PIRA Backend",
    }


@app.get("/")
def root():
    return {
        "message": "PIRA Backend is running",
    }
