# aiohttp OpenAPI Client Server

Тестовое задание: реализация сервера и клиента на aiohttp с генерацией OpenAPI контрактов.

## Описание проекта

Этот проект демонстрирует:
- Создание асинхронного REST API сервера на aiohttp
- Генерацию OpenAPI спецификации из кода
- Автоматическую генерацию клиента из OpenAPI контракта
- Написание тестов для сервера и клиента

## Технологический стек

- **Python**: 3.11.9
- **Async сервер**: aiohttp - асинхронный HTTP фреймворк
- **OpenAPI**: aiohttp-apispec + marshmallow - генерация документации
- **База данных**: SQLite (aiosqlite) - легковесная БД
- **Генерация клиента**: openapi-generator - инструмент для генерации клиентов
- **Тесты**: pytest, pytest-asyncio, pytest-aiohttp - фреймворк для тестирования

## Структура проекта

```
aiohttp-openapi-client-server/
├── server/                 # Серверное приложение
│   ├── app/               # Основной код приложения
│   │   ├── __init__.py    # Инициализация пакета
│   │   ├── main.py        # Точка входа, запуск сервера
│   │   ├── routes.py      # Регистрация маршрутов API
│   │   ├── handlers.py    # Обработчики HTTP запросов
│   │   ├── schemas.py     # Marshmallow схемы для валидации
│   │   ├── database.py    # Работа с SQLite базой данных
│   │   └── openapi.py     # Конфигурация OpenAPI документации
│   └── tests/             # Тесты сервера
│       ├── conftest.py    # Фикстуры для тестов
│       └── test_api.py    # Тесты API endpoints
├── client/                # Клиентское приложение
│   ├── generated/         # Сгенерированный клиент (не коммитится в git)
│   ├── app/               # Примеры использования клиента
│   │   └── main.py        # Демонстрация работы с клиентом
│   └── tests/             # Тесты клиента
│       ├── conftest.py    # Фикстуры для тестов
│       └── test_client.py # Интеграционные тесты клиента
├── openapi/               # OpenAPI спецификации
│   └── openapi.yaml       # Экспортированная спецификация API
├── requirements.txt       # Python зависимости проекта
├── generate_client.py     # Скрипт для генерации клиента
├── export_openapi.py      # Скрипт для экспорта OpenAPI спецификации
└── README.md              # Этот файл
```

## Установка и настройка

### Требования

- Python 3.11.9
- Java 11+ (для генерации клиента через openapi-generator)
- Git

### Шаг 1: Клонирование репозитория

```bash
git clone <repository-url>
cd aiohttp_openapi_client_server
```

### Шаг 2: Создание виртуального окружения

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python -m venv venv
source venv/bin/activate
```

### Шаг 3: Установка зависимостей

```bash
pip install -r requirements.txt
```

### Шаг 4: Установка openapi-generator (опционально, для генерации клиента)

**Вариант 1: Через npm (рекомендуется)**
```bash
npm install -g @openapitools/openapi-generator-cli
```

**Вариант 2: Через pip**
```bash
pip install openapi-generator-cli
```

**Важно:** openapi-generator требует Java 11 или выше. Проверьте установку:
```bash
java -version
```

**Как установить Java 11 через Chocolatey :**
1. Откройте PowerShell от имени администратора
2. Выполните команду:
   ```powershell
   Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
   ```
3. После установки Chocolatey перезапустите терминал
4. Установите Java: `choco install openjdk11`

## Запуск сервера

```bash
cd server
python -m app.main
```

Сервер запустится на `http://127.0.0.1:8080`

### Документация по ендпоинтам

**[Swagger UI](http://127.0.0.1:8080/swagger)**

## Генерация клиента

### Шаг 1: Экспорт OpenAPI спецификации

Убедитесь, что сервер запущен, затем выполните в другом терминале:

```bash
python export_openapi.py
```

Это создаст файл `openapi/openapi.yaml` со спецификацией API.

### Шаг 2: Генерация клиента

```bash
python generate_client.py
```

Клиент будет сгенерирован в `client/generated/`.

**Примечание:** Если генератор не найден, убедитесь, что:
- Установлен openapi-generator-cli
- Установлена Java 11+
- Перезапущен терминал после установки

### Шаг 3: Использование клиента

```bash
# Убедитесь, что сервер запущен
cd server && python -m app.main

# В другом терминале запустите пример
python client/app/main.py
```

## Тестирование

### Запуск тестов сервера

```bash
pytest server/tests/ -v
```

### Запуск тестов клиента

```bash
pytest client/tests/ -v
```

## Архитектура проекта

### Серверная часть

**main.py** - Точка входа приложения:
- Создает и настраивает aiohttp Application
- Регистрирует lifecycle hooks для БД
- Запускает сервер

**routes.py** - Регистрация маршрутов:
- Определяет все URL endpoints
- Связывает URL с обработчиками

**handlers.py** - Бизнес-логика:
- Обрабатывает HTTP запросы
- Валидирует данные через Marshmallow схемы
- Работает с БД через объект `db`
- Генерирует HTTP ответы

**schemas.py** - Валидация данных:
- `TaskSchema` - схема для ответа
- `TaskCreateSchema` - схема для создания задачи
- `TaskUpdateSchema` - схема для обновления задачи

**database.py** - Работа с БД:
- Класс `Database` для работы с SQLite
- CRUD операции для задач
- Автоматическое создание таблиц

**openapi.py** - OpenAPI документация:
- Настройка aiohttp-apispec
- Генерация спецификации из декораторов
- Endpoint для получения спецификации в YAML

### Клиентская часть

**generated/** - Сгенерированный клиент:
- Автоматически генерируется из OpenAPI спецификации
- Содержит типизированные модели данных
- Предоставляет API классы для работы с endpoints

**app/main.py** - Пример использования:
- Демонстрирует работу с клиентом
- Показывает все CRUD операции

## Принципы работы

### Асинхронность

Проект использует асинхронное программирование:
- **aiohttp** - асинхронный HTTP сервер
- **aiosqlite** - асинхронная работа с SQLite
- **async/await** - для всех операций I/O

**Преимущества:**
- Высокая производительность
- Эффективное использование ресурсов
- Поддержка множества одновременных соединений

### Валидация данных

Используется **Marshmallow** для валидации:
- Автоматическая проверка типов
- Проверка обязательных полей
- Проверка ограничений (длина, допустимые значения)
- Понятные сообщения об ошибках

### OpenAPI спецификация

Спецификация генерируется автоматически из кода:
- Декораторы `@docs`, `@marshal_with`, `@use_kwargs` описывают API
- Доступна через `/swagger.json` и `/swagger.yaml`
- Используется для генерации клиента

### Генерация клиента

Клиент генерируется из OpenAPI спецификации:
- Один раз описали API - получили клиент для любого языка
- Типобезопасность и автодополнение
- Автоматическая синхронизация с API


## Лицензия

Этот проект создан в рамках тестового задания.


## Автор

**[Ndk985](https://github.com/Ndk985)**