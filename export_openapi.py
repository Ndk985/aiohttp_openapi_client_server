"""Скрипт для экспорта OpenAPI спецификации в файл."""

import sys
from pathlib import Path

import requests
import yaml

BASE_URL = "http://127.0.0.1:8080"
OUTPUT_DIR = Path("openapi")
OUTPUT_FILE = OUTPUT_DIR / "openapi.yaml"


def export_openapi_spec():
    """Экспортирует OpenAPI спецификацию в YAML файл."""
    try:
        response = requests.get(f"{BASE_URL}/swagger.json", timeout=5)
        response.raise_for_status()

        spec = response.json()

        OUTPUT_DIR.mkdir(exist_ok=True)

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            yaml.safe_dump(spec, f, sort_keys=False, allow_unicode=True, default_flow_style=False)

        print(f"✅ OpenAPI спецификация экспортирована в {OUTPUT_FILE}")
        return True
    except requests.exceptions.ConnectionError:
        print(f"❌ Не удалось подключиться к серверу на {BASE_URL}")
        print("Убедитесь, что сервер запущен: cd server && python -m app.main")
        return False
    except Exception as e:
        print(f"❌ Ошибка при экспорте: {e}")
        return False


if __name__ == "__main__":
    success = export_openapi_spec()
    sys.exit(0 if success else 1)
