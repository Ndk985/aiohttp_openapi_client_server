"""Обработчики HTTP запросов."""

from aiohttp.web import Request, Response, json_response

from .database import db


async def health_handler(request: Request) -> Response:
    """Обработчик для проверки работоспособности сервера. Endpoint: GET /health"""
    return json_response({"status": "ok", "message": "Server is running"})


async def create_task_handler(request: Request) -> Response:
    """Создает новую задачу. Endpoint: POST /tasks"""
    try:
        data = await request.json()
        title = data.get("title")
        description = data.get("description")
        status = data.get("status", "pending")

        if not title:
            return json_response({"error": "Title is required"}, status=400)

        task = await db.create_task(title, description, status)
        return json_response(task, status=201)
    except Exception as e:
        return json_response({"error": str(e)}, status=500)


async def get_task_handler(request: Request) -> Response:
    """Получает задачу по ID. Endpoint: GET /tasks/{id}"""
    try:
        task_id = int(request.match_info["id"])
        task = await db.get_task(task_id)

        if not task:
            return json_response({"error": "Task not found"}, status=404)

        return json_response(task)
    except ValueError:
        return json_response({"error": "Invalid task ID"}, status=400)
    except Exception as e:
        return json_response({"error": str(e)}, status=500)


async def update_task_handler(request: Request) -> Response:
    """Обновляет задачу по ID. Endpoint: PUT /tasks/{id}"""
    try:
        task_id = int(request.match_info["id"])
        data = await request.json()

        task = await db.update_task(
            task_id,
            title=data.get("title"),
            description=data.get("description"),
            status=data.get("status"),
        )

        if not task:
            return json_response({"error": "Task not found"}, status=404)

        return json_response(task)
    except ValueError:
        return json_response({"error": "Invalid task ID"}, status=400)
    except Exception as e:
        return json_response({"error": str(e)}, status=500)


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
