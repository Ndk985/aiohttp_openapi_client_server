"""Конфигурация pytest и фикстуры для тестов."""

import asyncio
import tempfile
from pathlib import Path

import pytest
from aiohttp.test_utils import TestClient, TestServer
from app.database import Database
from app.main import create_app


@pytest.fixture
def event_loop():
    """Создает event loop для тестов."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def test_db():
    """Создает тестовую БД во временном файле."""
    # Используем временный файл для тестовой БД
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name

    db = Database(db_path=db_path)
    await db.connect()

    yield db

    await db.close()
    # Удаляем временный файл БД после тестов
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
async def app(test_db):
    """Создает тестовое приложение с тестовой БД."""
    # Переопределяем глобальный db в модуле handlers на тестовую БД
    import app.handlers as handlers_module

    original_db = handlers_module.db

    # Подменяем БД на тестовую
    handlers_module.db = test_db

    # Создаем приложение
    app_instance = create_app()

    # Переопределяем startup/cleanup hooks, чтобы не подключать БД заново
    async def init_test_db(app):
        """Заглушка для инициализации БД - БД уже подключена."""
        pass

    async def close_test_db(app):
        """Заглушка для закрытия БД - закроем в фикстуре."""
        pass

    # Заменяем hooks
    app_instance.on_startup.clear()
    app_instance.on_cleanup.clear()
    app_instance.on_startup.append(init_test_db)
    app_instance.on_cleanup.append(close_test_db)

    yield app_instance

    # Восстанавливаем оригинальную БД
    handlers_module.db = original_db


@pytest.fixture
async def client(app):
    """Создает тестовый HTTP клиент."""
    async with TestClient(TestServer(app)) as test_client:
        yield test_client
