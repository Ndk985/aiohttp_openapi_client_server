"""Пример использования сгенерированного OpenAPI клиента."""

import asyncio
import sys
from pathlib import Path

# Добавляем путь к сгенерированному клиенту
project_root = Path(__file__).parent.parent.parent
generated_path = project_root / "client" / "generated"
sys.path.insert(0, str(generated_path))

try:
    from openapi_client import ApiClient, Configuration
    from openapi_client.api.tasks_api import TasksApi
    from openapi_client.models.task_create import TaskCreate
    from openapi_client.models.task_update import TaskUpdate
    from openapi_client.rest import ApiException
except ImportError as e:
    print("[ERROR] Ошибка импорта сгенерированного клиента!")
    print(f"Детали: {e}")
    print("\nУбедитесь, что клиент сгенерирован:")
    print("1. Запустите сервер: cd server && python -m app.main")
    print("2. Экспортируйте спецификацию: python export_openapi.py")
    print("3. Сгенерируйте клиент: python generate_client.py")
    sys.exit(1)


BASE_URL = "http://127.0.0.1:8080"


async def main():
    """Демонстрация работы с API через сгенерированный клиент."""
    print("=" * 60)
    print("ДЕМОНСТРАЦИЯ РАБОТЫ С API ЧЕРЕЗ СГЕНЕРИРОВАННЫЙ КЛИЕНТ")
    print("=" * 60)

    configuration = Configuration(host=BASE_URL)
    async with ApiClient(configuration) as api_client:
        tasks_api = TasksApi(api_client)

        try:
            print("\n1. СОЗДАНИЕ ЗАДАЧИ")
            print("-" * 60)
            task_create = TaskCreate(
                title="Изучить Python",
                description="Изучить основы асинхронного программирования",
                status="pending",
            )
            created_task = await tasks_api.tasks_post(task_create)
            print("[OK] Задача создана:")
            print(f"    ID: {created_task.id}")
            print(f"    Title: {created_task.title}")
            print(f"    Status: {created_task.status}")

            task_id = str(created_task.id)

            print("\n2. ПОЛУЧЕНИЕ ЗАДАЧИ ПО ID")
            print("-" * 60)
            task = await tasks_api.tasks_id_get(task_id)
            print("[OK] Задача получена:")
            print(f"    ID: {task.id}")
            print(f"    Title: {task.title}")
            print(f"    Description: {task.description}")
            print(f"    Status: {task.status}")
            print(f"    Created: {task.created_at}")

            print("\n3. ОБНОВЛЕНИЕ ЗАДАЧИ (частичное)")
            print("-" * 60)
            task_update = TaskUpdate(status="in_progress")
            updated_task = await tasks_api.tasks_id_put(task_id, task_update)
            print("[OK] Задача обновлена:")
            print(f"    Status изменен на: {updated_task.status}")

            print("\n4. ОБНОВЛЕНИЕ ЗАДАЧИ (полное)")
            print("-" * 60)
            task_update_full = TaskUpdate(
                title="Изучить Python и aiohttp",
                description="Изучить основы асинхронного программирования и работу с aiohttp",
                status="completed",
            )
            updated_task_full = await tasks_api.tasks_id_put(task_id, task_update_full)
            print("[OK] Задача обновлена:")
            print(f"    Title: {updated_task_full.title}")
            print(f"    Description: {updated_task_full.description}")
            print(f"    Status: {updated_task_full.status}")

            print("\n5. УДАЛЕНИЕ ЗАДАЧИ")
            print("-" * 60)
            await tasks_api.tasks_id_delete(task_id)
            print(f"[OK] Задача {task_id} удалена")

            print("\n6. ПОПЫТКА ПОЛУЧИТЬ УДАЛЕННУЮ ЗАДАЧУ")
            print("-" * 60)
            try:
                await tasks_api.tasks_id_get(task_id)
                print("[ERROR] Задача не должна была быть найдена!")
            except ApiException as e:
                print("[OK] Ожидаемая ошибка (задача не найдена):")
                print(f"    HTTP {e.status}: {e.reason}")

        except ApiException as e:
            print("\n[ERROR] Ошибка API:")
            print(f"    HTTP {e.status}: {e.reason}")
            print(f"    Тело ответа: {e.body}")
        except Exception as e:
            print(f"\n[ERROR] Неожиданная ошибка: {e}")
            print(f"    Тип ошибки: {type(e).__name__}")
            import traceback

            traceback.print_exc()

    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
