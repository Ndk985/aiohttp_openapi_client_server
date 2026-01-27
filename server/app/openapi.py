"""Конфигурация OpenAPI документации."""

from aiohttp_apispec import setup_aiohttp_apispec
from aiohttp.web import Application


def setup_openapi(app: Application) -> None:
    """Настраивает OpenAPI документацию для приложения."""
    setup_aiohttp_apispec(
        app=app,
        title="Tasks API",
        version="1.0.0",
        url="/swagger.json",
        swagger_path="/swagger",
        info={
            "description": "REST API для управления задачами (tasks)",
        },
    )
