"""Работа с базой данных SQLite."""

from datetime import datetime
from typing import Any, Dict, List, Optional

import aiosqlite


class Database:
    """Менеджер базы данных SQLite."""

    def __init__(self, db_path: str = "tasks.db"):
        """Инициализация подключения к БД."""
        self.db_path = db_path
        self._connection: Optional[aiosqlite.Connection] = None

    async def connect(self) -> None:
        """Создает подключение к БД и инициализирует схему."""
        self._connection = await aiosqlite.connect(self.db_path)
        self._connection.row_factory = aiosqlite.Row
        await self._init_schema()

    async def close(self) -> None:
        """Закрывает подключение к БД."""
        if self._connection:
            await self._connection.close()

    async def _init_schema(self) -> None:
        """Создает таблицу tasks если она не существует."""
        await self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL
            )
        """
        )
        await self._connection.commit()

    async def create_task(
        self, title: str, description: Optional[str] = None, status: str = "pending"
    ) -> Dict[str, Any]:
        """Создает новую задачу."""
        created_at = datetime.utcnow().isoformat()
        cursor = await self._connection.execute(
            "INSERT INTO tasks (title, description, status, created_at) VALUES (?, ?, ?, ?)",
            (title, description, status, created_at),
        )
        await self._connection.commit()
        task_id = cursor.lastrowid
        return await self.get_task(task_id)

    async def get_task(self, task_id: int) -> Optional[Dict[str, Any]]:
        """Получает задачу по ID."""
        async with self._connection.execute(
            "SELECT * FROM tasks WHERE id = ?", (task_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return dict(row)
            return None

    async def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Получает все задачи."""
        async with self._connection.execute("SELECT * FROM tasks ORDER BY id") as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def update_task(
        self,
        task_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Обновляет задачу по ID."""
        updates = []
        params = []

        if title is not None:
            updates.append("title = ?")
            params.append(title)
        if description is not None:
            updates.append("description = ?")
            params.append(description)
        if status is not None:
            updates.append("status = ?")
            params.append(status)

        if not updates:
            return await self.get_task(task_id)

        params.append(task_id)
        query = f'UPDATE tasks SET {", ".join(updates)} WHERE id = ?'

        await self._connection.execute(query, params)
        await self._connection.commit()

        return await self.get_task(task_id)

    async def delete_task(self, task_id: int) -> bool:
        """Удаляет задачу по ID."""
        cursor = await self._connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        await self._connection.commit()
        return cursor.rowcount > 0


# Глобальный экземпляр БД
db = Database()
