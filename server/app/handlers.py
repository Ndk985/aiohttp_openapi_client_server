"""Обработчики HTTP запросов."""

from aiohttp.web import Request, Response, json_response
from aiohttp_apispec import docs, marshal_with, use_kwargs
from marshmallow import ValidationError

from .database import db
from .schemas import TaskCreateSchema, TaskSchema, TaskUpdateSchema


@docs(
    tags=["health"],
    summary="Health check",
    description="Проверка работоспособности сервера",
)
async def health_handler(request: Request) -> Response:
    """Обработчик для проверки работоспособности сервера. Endpoint: GET /health"""
    return json_response({"status": "ok", "message": "Server is running"})


@docs(
    tags=["tasks"],
    summary="Создать задачу",
    description="Создает новую задачу с указанными параметрами",
)
@use_kwargs(TaskCreateSchema, location="json")
@marshal_with(TaskSchema, code=201, description="Задача успешно создана")
async def create_task_handler(request: Request) -> Response:
    """Создает новую задачу. Endpoint: POST /tasks"""
    try:
        data = await request.json()
        schema = TaskCreateSchema()

        try:
            validated_data = schema.load(data)
        except ValidationError as e:
            return json_response({"error": "Validation failed", "details": e.messages}, status=400)

        task = await db.create_task(
            validated_data["title"],
            validated_data.get("description"),
            validated_data.get("status", "pending"),
        )

        result_schema = TaskSchema()
        return json_response(result_schema.dump(task), status=201)
    except Exception as e:
        return json_response({"error": str(e)}, status=500)


@docs(tags=["tasks"], summary="Получить задачу", description="Получает задачу по её ID")
@marshal_with(TaskSchema, code=200, description="Задача найдена")
async def get_task_handler(request: Request) -> Response:
    """Получает задачу по ID. Endpoint: GET /tasks/{id}"""
    try:
        task_id = int(request.match_info["id"])
        task = await db.get_task(task_id)

        if not task:
            return json_response({"error": "Task not found"}, status=404)

        schema = TaskSchema()
        return json_response(schema.dump(task))
    except ValueError:
        return json_response({"error": "Invalid task ID"}, status=400)
    except Exception as e:
        return json_response({"error": str(e)}, status=500)


@docs(tags=["tasks"], summary="Обновить задачу", description="Обновляет задачу по её ID")
@use_kwargs(TaskUpdateSchema, location="json")
@marshal_with(TaskSchema, code=200, description="Задача успешно обновлена")
async def update_task_handler(request: Request) -> Response:
    """Обновляет задачу по ID. Endpoint: PUT /tasks/{id}"""
    try:
        task_id = int(request.match_info["id"])
        data = await request.json()
        schema = TaskUpdateSchema()

        try:
            validated_data = schema.load(data)
        except ValidationError as e:
            return json_response({"error": "Validation failed", "details": e.messages}, status=400)

        task = await db.update_task(
            task_id,
            title=validated_data.get("title"),
            description=validated_data.get("description"),
            status=validated_data.get("status"),
        )

        if not task:
            return json_response({"error": "Task not found"}, status=404)

        result_schema = TaskSchema()
        return json_response(result_schema.dump(task))
    except ValueError:
        return json_response({"error": "Invalid task ID"}, status=400)
    except Exception as e:
        return json_response({"error": str(e)}, status=500)


@docs(
    tags=["tasks"],
    summary="Удалить задачу",
    description="Удаляет задачу по её ID",
)
async def delete_task_handler(request: Request) -> Response:
    """Удаляет задачу по ID. Endpoint: DELETE /tasks/{id}"""
    try:
        task_id = int(request.match_info["id"])
        deleted = await db.delete_task(task_id)

        if not deleted:
            return json_response({"error": "Task not found"}, status=404)

        return json_response({"message": "Task deleted successfully"}, status=200)
    except ValueError:
        return json_response({"error": "Invalid task ID"}, status=400)
    except Exception as e:
        return json_response({"error": str(e)}, status=500)
