from fastapi import APIRouter

from app.apis.v1.auth_routers import auth_router
from app.apis.v1.challenge_routers import challenge_router, user_challenge_router
from app.apis.v1.dashboard_routers import dashboard_router
from app.apis.v1.health_check_routers import health_check_router
from app.apis.v1.lifestyle_survey_routers import lifestyle_survey_router
from app.apis.v1.user_routers import user_router

v1_routers = APIRouter(prefix="/api/v1")
v1_routers.include_router(auth_router)
v1_routers.include_router(user_router)
v1_routers.include_router(health_check_router)
v1_routers.include_router(lifestyle_survey_router)
v1_routers.include_router(dashboard_router)
v1_routers.include_router(challenge_router)
v1_routers.include_router(user_challenge_router)
