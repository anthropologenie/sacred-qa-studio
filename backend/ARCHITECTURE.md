# Sacred QA Studio - Backend Architecture

## Request Flow
POST /sankalpa → sacred_contacts → lineage tree → validation → database

## Agent Pattern
Each agent:
1. Receives request + parent_lineage_id
2. Performs operation (validate/score/search)
3. Logs to qa_logs
4. Creates lineage entry linking to parent
5. Returns result

## Current Agents
- api-gateway: Entry point, creates root lineage
- jnana-validator-v1: Request validation
- db-writer: Database operations

## Tables
- app.sacred_contacts: API request/response log
- app.request_lineage: Agent execution tree
- app.qa_logs: Detailed agent logs
- app.sankalpa: Core data
