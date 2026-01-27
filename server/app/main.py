"""Точка входа в серверное приложение."""

from aiohttp import web
from aiohttp.web import Application

from .routes import setup_routes


def create_app() -> Application:
    """Создает и настраивает aiohttp приложение."""
    app = web.Application()
    setup_routes(app)
    return app


def main():
    """Запускает сервер."""
    app = create_app()
    web.run_app(app, host='127.0.0.1', port=8080)


if __name__ == '__main__':
    main()
