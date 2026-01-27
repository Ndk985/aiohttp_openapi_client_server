"""Маршрутизация HTTP запросов."""

from aiohttp.web import Application

from .handlers import (
    create_task_handler,
    delete_task_handler,
    get_task_handler,
    health_handler,
    update_task_handler,
)


def setup_routes(app: Application) -> None:
    """Регистрирует все маршруты приложения."""
    app.router.add_get("/health", health_handler)
    app.router.add_post("/tasks", create_task_handler)
    app.router.add_get("/tasks/{id}", get_task_handler)
    app.router.add_put("/tasks/{id}", update_task_handler)
    app.router.add_delete("/tasks/{id}", delete_task_handler)
