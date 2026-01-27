"""Маршрутизация HTTP запросов."""

from aiohttp.web import Application

from .handlers import health_handler


def setup_routes(app: Application) -> None:
    """Регистрирует все маршруты приложения."""
    app.router.add_get('/health', health_handler)
