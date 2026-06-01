from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse
from slowapi.errors import RateLimitExceeded
from tortoise import Tortoise

from app.apis.v1 import v1_routers
from app.core.db.databases import TORTOISE_APP_MODELS, TORTOISE_ORM, run_migrations
from app.core.error_handlers import register_error_handlers
from app.core.rate_limit import limiter
from app.core.seed import seed_challenges


@asynccontextmanager
async def lifespan(app: FastAPI):
    await run_migrations()
    await Tortoise.init(config=TORTOISE_ORM)
    await seed_challenges()
    yield
    await Tortoise.close_connections()


Tortoise.init_models(TORTOISE_APP_MODELS, "models")

app = FastAPI(
    lifespan=lifespan,
    default_response_class=ORJSONResponse,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# REQ-NF-008 / REQ-SEC-004: Rate Limiting
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def _rate_limit_handler(request: Request, exc: RateLimitExceeded) -> ORJSONResponse:
    return ORJSONResponse(
        status_code=429,
        content={"detail": f"요청이 너무 많습니다. 잠시 후 다시 시도해주세요. (제한: {exc.detail})"},
    )


register_error_handlers(app)
app.include_router(v1_routers)
