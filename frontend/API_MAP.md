# Conduit Frontend API Map

The frontend only calls routes present in the backend. The small additions below expose persisted records that already exist in the database models/repositories and provide the missing HTTP entrypoint for the existing LangGraph execution.

| Feature | Method | Route | Purpose |
|---|---|---|---|
| Health | GET | `/health` | Backend health indicator |
| Launch workflow | POST | `/executions` | Create an execution and invoke the existing LangGraph in a background task |
| Executions | GET | `/executions` | List persisted workflow executions with steps |
| Execution detail | GET | `/executions/{execution_id}` | Load one execution and its step history |
| Approvals | GET | `/approvals?status=pending` | Read approval queue |
| Approve | POST | `/approvals/{approval_request_id}/approve` | Existing approval decision route |
| Reject | POST | `/approvals/{approval_request_id}/reject` | Existing rejection/regeneration route |
| Marketing | GET | `/marketing/content` | List persisted marketing content |
| Marketing detail | GET | `/marketing/content/{content_id}` | Existing content detail route |
| Marketing schedule | POST | `/marketing/content/{content_id}/schedule` | Existing schedule route |
| Sales leads | GET | `/sales/leads` | List persisted leads |
| Sales lead detail | GET | `/sales/leads/{lead_id}` | Read one lead |
| Sales follow-ups | GET | `/sales/follow-ups` | List persisted follow-ups |
| Sales follow-up detail | GET | `/sales/follow-ups/{follow_up_id}` | Read one follow-up |
| Sales schedule | POST | `/sales/leads/follow-up/{follow_up_id}/schedule` | Existing schedule route |
| Tech tickets | GET | `/tech/tickets` | List persisted tickets |
| Tech ticket detail | GET | `/tech/tickets/{ticket_id}` | Read one ticket |
| Tech fixes | GET | `/tech/fixes` | List persisted fixes |
| Tech fix detail | GET | `/tech/fixes/{fix_id}` | Read one generated fix |

## Minimal backend additions

- `api/routers/executions.py`: HTTP launch/list/detail surface for the existing `WorkflowExecution` and LangGraph.
- `api/routers/insights.py`: read-only list endpoints for persisted approvals and business objects.
- `api/routers/resources.py`: detail endpoints for Sales records.
- `api/schemas/execution.py` and `api/schemas/resources.py`: response/request contracts for those thin API surfaces.
- `api/routers/marketing.py`: restores the legacy `reject_content` helper used by an existing repository test and exposes a compatibility endpoint. The main UI uses the canonical `/approvals/{approval_request_id}/reject` route.
- `main.py`: serves `frontend/index.html` and `/assets/*`, with SPA fallback for frontend routes.

No workflow node, service, repository, MCP tool, database model, or LangGraph business rule was replaced by the frontend.
