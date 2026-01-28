"""Интеграционные тесты для сгенерированного клиента."""

import pytest

try:
    from openapi_client import ApiClient, Configuration
    from openapi_client.api.tasks_api import TasksApi
    from openapi_client.models.task_create import TaskCreate
    from openapi_client.models.task_update import TaskUpdate
    from openapi_client.rest import ApiException
except ImportError:
    pytest.skip("Сгенерированный клиент не найден", allow_module_level=True)


@pytest.mark.asyncio
class TestClientIntegration:
    """Интеграционные тесты для сгенерированного клиента."""

    async def test_create_task(self, base_url):
        """Тест создания задачи через клиент."""
        config = Configuration(host=base_url)
        async with ApiClient(config) as api_client:
            tasks_api = TasksApi(api_client)

            task_create = TaskCreate(
                title="Тестовая задача",
                description="Описание тестовой задачи",
                status="pending",
            )

            created_task = await tasks_api.tasks_post(task_create)

            assert created_task.id is not None
            assert created_task.title == task_create.title
            assert created_task.description == task_create.description
            assert created_task.status == task_create.status
            assert created_task.created_at is not None

    async def test_get_task(self, base_url):
        """Тест получения задачи через клиент."""
        config = Configuration(host=base_url)
        async with ApiClient(config) as api_client:
            tasks_api = TasksApi(api_client)

            # Создаем задачу
            task_create = TaskCreate(title="Задача для получения")
            created_task = await tasks_api.tasks_post(task_create)

            # Получаем задачу
            task = await tasks_api.tasks_id_get(str(created_task.id))

            assert task.id == created_task.id
            assert task.title == created_task.title
            assert task.status == created_task.status

    async def test_get_task_not_found(self, base_url):
        """Тест получения несуществующей задачи через клиент."""
        config = Configuration(host=base_url)
        async with ApiClient(config) as api_client:
            tasks_api = TasksApi(api_client)

            with pytest.raises(ApiException) as exc_info:
                await tasks_api.tasks_id_get("99999")

            assert exc_info.value.status == 404

    async def test_update_task_partial(self, base_url):
        """Тест частичного обновления задачи через клиент."""
        config = Configuration(host=base_url)
        async with ApiClient(config) as api_client:
            tasks_api = TasksApi(api_client)

            # Создаем задачу
            task_create = TaskCreate(title="Задача для обновления", status="pending")
            created_task = await tasks_api.tasks_post(task_create)

            # Обновляем только status
            task_update = TaskUpdate(status="in_progress")
            updated_task = await tasks_api.tasks_id_put(str(created_task.id), task_update)

            assert updated_task.id == created_task.id
            assert updated_task.status == "in_progress"
            assert updated_task.title == created_task.title

    async def test_update_task_full(self, base_url):
        """Тест полного обновления задачи через клиент."""
        config = Configuration(host=base_url)
        async with ApiClient(config) as api_client:
            tasks_api = TasksApi(api_client)

            # Создаем задачу
            task_create = TaskCreate(title="Исходная задача", status="pending")
            created_task = await tasks_api.tasks_post(task_create)

            # Обновляем все поля
            task_update = TaskUpdate(
                title="Обновленная задача",
                description="Новое описание",
                status="completed",
            )
            updated_task = await tasks_api.tasks_id_put(str(created_task.id), task_update)

            assert updated_task.title == task_update.title
            assert updated_task.description == task_update.description
            assert updated_task.status == task_update.status

    async def test_update_task_not_found(self, base_url):
        """Тест обновления несуществующей задачи через клиент."""
        config = Configuration(host=base_url)
        async with ApiClient(config) as api_client:
            tasks_api = TasksApi(api_client)

            task_update = TaskUpdate(status="completed")

            with pytest.raises(ApiException) as exc_info:
                await tasks_api.tasks_id_put("99999", task_update)

            assert exc_info.value.status == 404

    async def test_delete_task(self, base_url):
        """Тест удаления задачи через клиент."""
        config = Configuration(host=base_url)
        async with ApiClient(config) as api_client:
            tasks_api = TasksApi(api_client)

            # Создаем задачу
            task_create = TaskCreate(title="Задача для удаления")
            created_task = await tasks_api.tasks_post(task_create)

            # Удаляем задачу
            await tasks_api.tasks_id_delete(str(created_task.id))

            # Проверяем, что задача удалена
            with pytest.raises(ApiException) as exc_info:
                await tasks_api.tasks_id_get(str(created_task.id))

            assert exc_info.value.status == 404

    async def test_delete_task_not_found(self, base_url):
        """Тест удаления несуществующей задачи через клиент."""
        config = Configuration(host=base_url)
        async with ApiClient(config) as api_client:
            tasks_api = TasksApi(api_client)

            with pytest.raises(ApiException) as exc_info:
                await tasks_api.tasks_id_delete("99999")

            assert exc_info.value.status == 404

    async def test_full_workflow(self, base_url):
        """Тест полного workflow: создание -> получение -> обновление -> удаление."""
        config = Configuration(host=base_url)
        async with ApiClient(config) as api_client:
            tasks_api = TasksApi(api_client)

            # 1. Создаем задачу
            task_create = TaskCreate(
                title="Workflow задача",
                description="Тест полного цикла",
                status="pending",
            )
            created_task = await tasks_api.tasks_post(task_create)
            assert created_task.status == "pending"

            # 2. Получаем задачу
            task = await tasks_api.tasks_id_get(str(created_task.id))
            assert task.title == "Workflow задача"

            # 3. Обновляем задачу
            task_update = TaskUpdate(status="in_progress")
            updated_task = await tasks_api.tasks_id_put(str(created_task.id), task_update)
            assert updated_task.status == "in_progress"

            # 4. Обновляем еще раз
            task_update2 = TaskUpdate(status="completed")
            completed_task = await tasks_api.tasks_id_put(str(created_task.id), task_update2)
            assert completed_task.status == "completed"

            # 5. Удаляем задачу
            await tasks_api.tasks_id_delete(str(created_task.id))

            # 6. Проверяем, что задача удалена
            with pytest.raises(ApiException) as exc_info:
                await tasks_api.tasks_id_get(str(created_task.id))
            assert exc_info.value.status == 404
