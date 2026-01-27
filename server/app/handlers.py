"""Обработчики HTTP запросов."""

from aiohttp.web import Response, json_response, Request


async def health_handler(request: Request) -> Response:
    """Обработчик для проверки работоспособности сервера. Endpoint: GET /health"""
    return json_response({
        'status': 'ok',
        'message': 'Server is running'
    })
