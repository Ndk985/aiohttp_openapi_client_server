"""Конфигурация OpenAPI документации."""

from collections import OrderedDict

import yaml
from aiohttp import web
from aiohttp.web import Application
from aiohttp_apispec import setup_aiohttp_apispec


def _convert_ordered_dict_to_dict(obj):
    """Рекурсивно преобразует OrderedDict в обычный dict для сериализации в YAML."""
    if isinstance(obj, OrderedDict):
        return {key: _convert_ordered_dict_to_dict(value) for key, value in obj.items()}
    elif isinstance(obj, dict):
        return {key: _convert_ordered_dict_to_dict(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [_convert_ordered_dict_to_dict(item) for item in obj]
    else:
        return obj


async def swagger_yaml_handler(request: web.Request) -> web.Response:
    """Отдает OpenAPI спецификацию в формате YAML."""
    spec = request.app.get("swagger_dict")
    if not spec:
        return web.Response(text="OpenAPI спецификация недоступна", status=500)

    spec_dict = _convert_ordered_dict_to_dict(spec)
    yaml_body = yaml.safe_dump(spec_dict, sort_keys=False, allow_unicode=True)
    return web.Response(text=yaml_body, content_type="application/x-yaml")


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

    # Endpoint для YAML-версии спецификации
    app.router.add_get("/swagger.yaml", swagger_yaml_handler)
