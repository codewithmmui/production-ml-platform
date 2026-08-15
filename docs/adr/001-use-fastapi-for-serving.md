# ADR 001: FastAPI for serving

## Context
Inference needs strict contracts, async-compatible middleware, OpenAPI and probe endpoints.
## Decision
Use FastAPI/Pydantic behind a production ASGI server.
## Alternatives
Flask requires more contract plumbing; dedicated model servers complicate custom feature behavior.
## Consequences
Excellent typed interfaces; CPU inference must remain bounded and scale via workers/pods.
