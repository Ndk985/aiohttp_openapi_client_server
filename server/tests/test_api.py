"""Тесты для API endpoints."""

import pytest


@pytest.mark.asyncio
class TestHealthEndpoint:
    """Тесты для health check endpoint."""

    async def test_health_get(self, client):
        """Тест GET /health."""
        async with client.get("/health") as resp:
            assert resp.status == 200
            data = await resp.json()
            assert data["status"] == "ok"
            assert "message" in data

    async def test_health_head(self, client):
        """Тест HEAD /health."""
        async with client.head("/health") as resp:
            assert resp.status == 200


@pytest.mark.asyncio
class TestTasksEndpoint:
    """Тесты для tasks endpoints."""

    async def test_create_task_success(self, client):
        """Тест успешного создания задачи."""
        task_data = {
            "title": "Тестовая задача",
            "description": "Описание тестовой задачи",
            "status": "pending",
        }

        async with client.post("/tasks", json=task_data) as resp:
            assert resp.status == 201
            data = await resp.json()
            assert "id" in data
            assert data["title"] == task_data["title"]
            assert data["description"] == task_data["description"]
            assert data["status"] == task_data["status"]
            assert "created_at" in data

    async def test_create_task_minimal(self, client):
        """Тест создания задачи с минимальными данными (только title)."""
        task_data = {"title": "Минимальная задача"}

        async with client.post("/tasks", json=task_data) as resp:
            assert resp.status == 201
            data = await resp.json()
            assert data["title"] == task_data["title"]
            assert data["status"] == "pending"  # Значение по умолчанию

    async def test_create_task_validation_error_empty_title(self, client):
        """Тест валидации: пустой title."""
        task_data = {"title": ""}

        async with client.post("/tasks", json=task_data) as resp:
            assert resp.status == 400
            data = await resp.json()
            assert "error" in data

    async def test_create_task_validation_error_missing_title(self, client):
        """Тест валидации: отсутствует title."""
        task_data = {"description": "Задача без названия"}

        async with client.post("/tasks", json=task_data) as resp:
            assert resp.status == 400
            data = await resp.json()
            assert "error" in data

    async def test_create_task_validation_error_invalid_status(self, client):
        """Тест валидации: невалидный status."""
        task_data = {"title": "Задача", "status": "invalid_status"}

        async with client.post("/tasks", json=task_data) as resp:
            assert resp.status == 400
            data = await resp.json()
            assert "error" in data

    async def test_get_task_success(self, client):
        """Тест успешного получения задачи."""
        # Сначала создаем задачу
        task_data = {"title": "Задача для получения"}
        async with client.post("/tasks", json=task_data) as create_resp:
            assert create_resp.status == 201
            created_task = await create_resp.json()
            task_id = created_task["id"]

        # Затем получаем её
        async with client.get(f"/tasks/{task_id}") as resp:
            assert resp.status == 200
            data = await resp.json()
            assert data["id"] == task_id
            assert data["title"] == task_data["title"]

    async def test_get_task_not_found(self, client):
        """Тест получения несуществующей задачи."""
        async with client.get("/tasks/99999") as resp:
            assert resp.status == 404
            data = await resp.json()
            assert "error" in data

    async def test_get_task_invalid_id(self, client):
        """Тест получения задачи с невалидным ID."""
        async with client.get("/tasks/abc") as resp:
            assert resp.status == 400
            data = await resp.json()
            assert "error" in data

    async def test_update_task_partial(self, client):
        """Тест частичного обновления задачи (только status)."""
        # Создаем задачу
        task_data = {"title": "Задача для обновления", "status": "pending"}
        async with client.post("/tasks", json=task_data) as create_resp:
            created_task = await create_resp.json()
            task_id = created_task["id"]

        # Обновляем только status
        update_data = {"status": "in_progress"}
        async with client.put(f"/tasks/{task_id}", json=update_data) as resp:
            assert resp.status == 200
            data = await resp.json()
            assert data["status"] == "in_progress"
            assert data["title"] == task_data["title"]  # Title не изменился

    async def test_update_task_full(self, client):
        """Тест полного обновления задачи."""
        # Создаем задачу
        task_data = {"title": "Исходная задача", "status": "pending"}
        async with client.post("/tasks", json=task_data) as create_resp:
            created_task = await create_resp.json()
            task_id = created_task["id"]

        # Обновляем все поля
        update_data = {
            "title": "Обновленная задача",
            "description": "Новое описание",
            "status": "completed",
        }
        async with client.put(f"/tasks/{task_id}", json=update_data) as resp:
            assert resp.status == 200
            data = await resp.json()
            assert data["title"] == update_data["title"]
            assert data["description"] == update_data["description"]
            assert data["status"] == update_data["status"]

    async def test_update_task_not_found(self, client):
        """Тест обновления несуществующей задачи."""
        update_data = {"status": "completed"}
        async with client.put("/tasks/99999", json=update_data) as resp:
            assert resp.status == 404
            data = await resp.json()
            assert "error" in data

    async def test_update_task_invalid_id(self, client):
        """Тест обновления задачи с невалидным ID."""
        update_data = {"status": "completed"}
        async with client.put("/tasks/abc", json=update_data) as resp:
            assert resp.status == 400
            data = await resp.json()
            assert "error" in data

    async def test_delete_task_success(self, client):
        """Тест успешного удаления задачи."""
        # Создаем задачу
        task_data = {"title": "Задача для удаления"}
        async with client.post("/tasks", json=task_data) as create_resp:
            created_task = await create_resp.json()
            task_id = created_task["id"]

        # Удаляем задачу
        async with client.delete(f"/tasks/{task_id}") as resp:
            assert resp.status == 200
            data = await resp.json()
            assert "message" in data

        # Проверяем, что задача удалена
        async with client.get(f"/tasks/{task_id}") as get_resp:
            assert get_resp.status == 404

    async def test_delete_task_not_found(self, client):
        """Тест удаления несуществующей задачи."""
        async with client.delete("/tasks/99999") as resp:
            assert resp.status == 404
            data = await resp.json()
            assert "error" in data

    async def test_delete_task_invalid_id(self, client):
        """Тест удаления задачи с невалидным ID."""
        async with client.delete("/tasks/abc") as resp:
            assert resp.status == 400
            data = await resp.json()
            assert "error" in data
