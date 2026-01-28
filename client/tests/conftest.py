"""Конфигурация pytest и фикстуры для тестов клиента."""

import asyncio
import sys
import tempfile
from pathlib import Path

import pytest
from aiohttp.test_utils import TestServer

# Добавляем пути для импортов (нужно сделать до импорта app.*)
project_root = Path(__file__).parent.parent.parent
generated_path = project_root / "client" / "generated"
server_path = project_root / "server"

sys.path.insert(0, str(generated_path))
sys.path.insert(0, str(server_path))

from app.database import Database  # noqa: E402
from app.main import create_app  # noqa: E402


@pytest.fixture
def event_loop():
    """Создает event loop для тестов."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def test_db():
    """Создает тестовую БД во временном файле."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name

    db = Database(db_path=db_path)
    await db.connect()

    yield db

    await db.close()
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
async def test_server(test_db):
    """Создает тестовый сервер с тестовой БД."""
    import app.handlers as handlers_module

    original_db = handlers_module.db

    handlers_module.db = test_db

    app_instance = create_app()

    async def init_test_db(app):
        pass

    async def close_test_db(app):
        pass

    app_instance.on_startup.clear()
    app_instance.on_cleanup.clear()
    app_instance.on_startup.append(init_test_db)
    app_instance.on_cleanup.append(close_test_db)

    server = TestServer(app_instance)
    await server.start_server()

    yield server

    await server.close()
    handlers_module.db = original_db


@pytest.fixture
def base_url(test_server):
    """Возвращает базовый URL тестового сервера."""
    return f"http://{test_server.host}:{test_server.port}"
