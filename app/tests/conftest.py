import asyncio
from collections.abc import Generator

import pytest
import pytest_asyncio
from _pytest.fixtures import FixtureRequest
from tortoise.contrib.test import finalizer, initializer

from app.core import config
from app.core.db.databases import TORTOISE_APP_MODELS

TEST_BASE_URL = "http://test"

# PostgreSQL에서 DB를 생성/삭제하려면 다른 DB(maintenance DB)에 먼저 접속해야 한다.
# asyncpg는 DB 미지정 시 username(ckduser)을 DB명으로 사용하므로,
# CI의 postgres 서비스에 ckduser DB가 존재해야 한다. (checks.yml 참고)
TEST_DB_URL = f"postgres://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}"


@pytest.fixture(scope="session", autouse=True)
def initialize(request: FixtureRequest) -> Generator[None, None]:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # db_url을 직접 전달하면 _TORTOISE_TEST_DB가 설정되어
    # TestCase도 PostgreSQL을 사용하게 된다.
    initializer(modules=TORTOISE_APP_MODELS, db_url=TEST_DB_URL)
    yield
    finalizer()
    loop.close()


@pytest_asyncio.fixture(autouse=True, scope="session")  # type: ignore[type-var]
def event_loop() -> None:
    pass
