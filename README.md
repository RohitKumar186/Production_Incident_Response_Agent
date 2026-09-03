# Production Incident Response Agent

A multi-agent AI system for investigating and responding to production incidents.

The system detects an incident, investigates multiple production signals, collects evidence, generates a standardized Knowledge Card, and passes the investigation results to the RCA and remediation pipeline.

## Current Architecture

```text
Incident
   ↓
Incident Simulation
   ↓
Investigation Orchestrator
   ↓
┌─────────┬──────────┬──────────┬─────────┐
│  Logs   │ Metrics  │ Database │ Network │
│  Agent  │  Agent   │  Agent   │  Agent  │
└─────────┴──────────┴──────────┴─────────┘
   ↓
Investigation Findings
   ↓
Knowledge Card
   ↓
RCA / Remediation Pipeline