"""Точка входа в серверное приложение."""

from aiohttp import web
from aiohttp.web import Application

from .database import db
from .openapi import setup_openapi
from .routes import setup_routes


async def init_db(app: Application) -> None:
    """Инициализирует БД при старте приложения."""
    await db.connect()


async def close_db(app: Application) -> None:
    """Закрывает БД при остановке приложения."""
    await db.close()


def create_app() -> Application:
    """Создает и настраивает aiohttp приложение."""
    app = web.Application()
    setup_routes(app)
    setup_openapi(app)
    app.on_startup.append(init_db)
    app.on_cleanup.append(close_db)
    return app


def main():
    """Запускает сервер."""
    app = create_app()
    web.run_app(app, host="127.0.0.1", port=8080)


if __name__ == "__main__":
    main()
