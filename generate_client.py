"""Скрипт для генерации Python клиента из OpenAPI спецификации."""

import subprocess
import sys
from pathlib import Path

OPENAPI_FILE = Path("openapi/openapi.yaml")
OUTPUT_DIR = Path("client/generated")
OPENAPI_GENERATOR_CMD = None


def check_java():
    """Проверяет наличие Java (JRE 11+ требуется для openapi-generator)."""
    try:
        result = subprocess.run(
            ["java", "-version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        # Java выводит версию в stderr, не в stdout
        if result.stderr:
            version_info = result.stderr.split("\n")[0]
            print(f"[OK] Java найдена: {version_info}")

            # Парсим версию Java
            version_line = result.stderr.split("\n")[0]
            # Ищем паттерн типа "version "1.8.0" или "openjdk version "11.0.2"
            import re

            version_match = re.search(r'version ["\']?(\d+)', version_line)
            if version_match:
                java_major_version = int(version_match.group(1))
                if java_major_version < 11:
                    print(f"[ERROR] Требуется Java 11 или выше, найдена Java {java_major_version}")
                    print("\nopenapi-generator-cli требует Java 11 или выше.")
                    print("\nУстановите Java 11+ одним из способов:")
                    print("1. OpenJDK 11+: https://adoptium.net/")
                    print("2. Oracle Java 11+: https://www.oracle.com/java/technologies/downloads/")
                    print("3. Через Chocolatey: choco install openjdk11")
                    print("\nПосле установки перезапустите терминал и проверьте: java -version")
                    return False
                else:
                    print(f"[OK] Версия Java {java_major_version} подходит")
                    return True
            else:
                print("[WARNING] Не удалось определить версию Java, продолжаю...")
                return True
    except FileNotFoundError:
        print("[ERROR] Java не найдена!")
        print("\nopenapi-generator требует Java Runtime Environment (JRE) 11 или выше.")
        print("\nУстановите Java одним из способов:")
        print("1. OpenJDK 11+: https://adoptium.net/")
        print("2. Oracle Java 11+: https://www.oracle.com/java/technologies/downloads/")
        print("3. Через Chocolatey: choco install openjdk11")
        print("\nПосле установки перезапустите терминал и проверьте: java -version")
        return False
    except Exception as e:
        print(f"[WARNING] Ошибка при проверке Java: {e}")
        return False
    return False


def check_openapi_file():
    """Проверяет наличие OpenAPI спецификации."""
    if not OPENAPI_FILE.exists():
        print(f"Файл {OPENAPI_FILE} не найден!")
        print("\nСначала нужно экспортировать спецификацию:")
        print("1. Запустите сервер: cd server && python -m app.main")
        print("2. В другом терминале: python export_openapi.py")
        return False
    print(f"Файл {OPENAPI_FILE} найден")
    return True


def check_openapi_generator():
    """Проверяет установку openapi-generator/openapi-generator-cli.

    На разных способах установки бинарник может называться по-разному:
    - openapi-generator-cli  (npm/pip)
    - openapi-generator      (brew/scoop)
    - модуль Python: python -m openapi_generator_cli
    """
    global OPENAPI_GENERATOR_CMD

    # Проверяем, установлен ли пакет через pip
    try:
        import openapi_generator_cli  # noqa: F401

        print("[OK] Пакет openapi_generator_cli найден через import")
    except ImportError:
        pass

    # Пробуем найти исполняемый файл в Scripts виртуального окружения
    venv_scripts = Path(sys.prefix) / "Scripts"
    if venv_scripts.exists():
        exe_candidates = [
            venv_scripts / "openapi-generator-cli.exe",
            venv_scripts / "openapi-generator-cli",
            venv_scripts / "openapi-generator.exe",
            venv_scripts / "openapi-generator",
        ]
        for exe_path in exe_candidates:
            if exe_path.exists():
                print(f"[OK] Найден исполняемый файл: {exe_path}")
                OPENAPI_GENERATOR_CMD = [str(exe_path)]
                # Проверяем, что он работает
                try:
                    result = subprocess.run(
                        [str(exe_path), "version"],
                        capture_output=True,
                        text=True,
                        timeout=15,
                        shell=False,
                    )
                    # Проверяем успешный запуск (код 0) или наличие версии в выводе
                    if result.returncode == 0:
                        if result.stdout.strip():
                            print(result.stdout.strip())
                        elif result.stderr.strip():
                            # Иногда версия выводится в stderr
                            version_info = result.stderr.strip().split("\n")[0]
                            if "version" in version_info.lower() or any(
                                x in version_info for x in ["7.", "6.", "5."]
                            ):
                                print(version_info)
                        print(f"[OK] Генератор работает: {exe_path}")
                        return True
                    else:
                        # Проверяем на ошибку версии Java
                        error_output = result.stderr + result.stdout
                        if (
                            "UnsupportedClassVersionError" in error_output
                            or "class file version" in error_output
                        ):
                            print("[ERROR] Проблема с версией Java при запуске генератора:")
                            print(f"   {error_output[:400]}")
                            print("\n   Генератор требует Java 11 или выше.")
                            print("   Обновите Java и попробуйте снова.")
                            return False

                        # Если код возврата не 0, проверяем вывод на наличие версии
                        output = (result.stdout + result.stderr).lower()
                        if "version" in output or any(x in output for x in ["7.", "6.", "5."]):
                            print(f"[OK] Генератор найден (код {result.returncode}): {exe_path}")
                            if result.stderr:
                                print(f"   Вывод: {result.stderr[:100]}")
                            return True
                        else:
                            # Показываем ошибку, если версия не найдена
                            print(f"[WARNING] Ошибка при запуске {exe_path}:")
                            if result.stderr:
                                print(f"   stderr: {result.stderr[:300]}")
                            if result.stdout:
                                print(f"   stdout: {result.stdout[:300]}")
                except Exception as e:
                    print(f"[WARNING] Исключение при проверке {exe_path}: {e}")
                    import traceback

                    print(f"   Детали: {traceback.format_exc()[:200]}")
                    # Продолжаем поиск других вариантов

    # Пробуем различные команды
    candidates = [
        ["openapi-generator-cli", "version"],
        ["openapi-generator", "version"],
        [sys.executable, "-m", "openapi_generator_cli", "version"],
    ]

    for cmd in candidates:
        try:
            print(f"🔍 Пробую: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=15,
                shell=False,
            )
            if result.returncode == 0:
                print(f"[OK] Найден генератор: {' '.join(cmd)}")
                if result.stdout.strip():
                    print(result.stdout.strip())
                OPENAPI_GENERATOR_CMD = cmd[:-1]  # без аргумента version
                return True
            else:
                error_output = result.stderr + result.stdout
                if (
                    "UnsupportedClassVersionError" in error_output
                    or "class file version" in error_output
                ):
                    print("[ERROR] Проблема с версией Java:")
                    print(f"   {error_output[:400]}")
                    print("\n   Генератор требует Java 11 или выше.")
                    return False
                if result.stderr:
                    print(f"[WARNING] stderr: {result.stderr[:200]}")
        except FileNotFoundError:
            continue
        except Exception as e:
            print(f"[WARNING] Ошибка при проверке {' '.join(cmd)}: {e}")

    print("\n[ERROR] openapi-generator-cli не найден ни под одним из ожидаемых имён!")
    print("\nУстановите openapi-generator-cli одним из способов:")
    print("1. Через npm: npm install -g @openapitools/openapi-generator-cli")
    print("2. Через pip: pip install openapi-generator-cli")
    print("3. Через Homebrew (macOS): brew install openapi-generator")
    print("4. Через Scoop (Windows): scoop install openapi-generator-cli")
    print("\nПримечание: openapi-generator требует Java (JRE 8+)")
    print("\nДиагностика:")
    print(f"  - Python: {sys.executable}")
    print(f"  - Prefix: {sys.prefix}")
    print(f"  - Scripts: {venv_scripts if venv_scripts.exists() else 'не найден'}")
    return False


def generate_client():
    """Генерирует Python клиент из OpenAPI спецификации."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"\nГенерация клиента из {OPENAPI_FILE}...")
    print(f"Выходная директория: {OUTPUT_DIR}")

    try:
        # Используем найденную команду или пробуем стандартное имя
        if OPENAPI_GENERATOR_CMD is None:
            base_cmd = ["openapi-generator-cli"]
        else:
            base_cmd = OPENAPI_GENERATOR_CMD

        cmd = [
            *base_cmd,
            "generate",
            "-i",
            str(OPENAPI_FILE),
            "-g",
            "python",
            "-o",
            str(OUTPUT_DIR),
            "--additional-properties=library=asyncio,packageName=openapi_client",
            "--skip-validate-spec",
        ]

        print(f"🚀 Запускаю команду: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        # Проверяем на ошибку версии Java в выводе
        error_output = result.stderr + result.stdout
        if "UnsupportedClassVersionError" in error_output or "class file version" in error_output:
            print("[ERROR] Проблема с версией Java!")
            print("\nГенератор требует Java 11 или выше, но найдена более старая версия.")
            print("\nУстановите Java 11+ одним из способов:")
            print("1. OpenJDK 11+: https://adoptium.net/")
            print("2. Oracle Java 11+: https://www.oracle.com/java/technologies/downloads/")
            print("3. Через Chocolatey: choco install openjdk11")
            print("\nПосле установки:")
            print("- Перезапустите терминал")
            print("- Проверьте версию: java -version")
            print("- Запустите генерацию снова: python generate_client.py")
            if result.stderr:
                print(f"\nДетали ошибки:\n{result.stderr[:500]}")
            return False

        if result.returncode == 0:
            print("[OK] Команда выполнена успешно!")

            # Проверяем, что файлы действительно созданы
            py_files = list(OUTPUT_DIR.rglob("*.py"))
            if py_files:
                print("[OK] Клиент успешно сгенерирован!")
                print(f"Клиент находится в: {OUTPUT_DIR}")
                print(f"Создано Python файлов: {len(py_files)}")
                print("\nПримеры файлов:")
                for py_file in sorted(py_files)[:5]:
                    rel_path = py_file.relative_to(OUTPUT_DIR)
                    print(f"   - {rel_path}")
                if len(py_files) > 5:
                    print(f"   ... и ещё {len(py_files) - 5} файлов")
                return True
            else:
                print("[WARNING] Команда выполнена, но Python файлы не найдены!")
                print(f"Проверьте содержимое: {OUTPUT_DIR}")
                if result.stdout:
                    print(f"\nВывод команды (stdout):\n{result.stdout[:500]}")
                if result.stderr:
                    print(f"\nВывод команды (stderr):\n{result.stderr[:500]}")
                return False
        else:
            print("[ERROR] Ошибка при генерации клиента:")
            print(f"Код возврата: {result.returncode}")
            if result.stderr:
                print(f"\nstderr:\n{result.stderr}")
            if result.stdout:
                print(f"\nstdout:\n{result.stdout}")
            return False

    except subprocess.TimeoutExpired:
        print("Таймаут при генерации клиента")
        return False
    except Exception as e:
        print(f"Ошибка: {e}")
        return False


def main():
    """Основная функция."""
    print("=" * 60)
    print("ГЕНЕРАЦИЯ PYTHON КЛИЕНТА ИЗ OPENAPI СПЕЦИФИКАЦИИ")
    print("=" * 60)

    if not check_openapi_file():
        sys.exit(1)

    if not check_java():
        print("\n[WARNING] ВНИМАНИЕ: Без Java генератор не будет работать!")
        print("Продолжаю проверку генератора, но генерация может не сработать...\n")

    if not check_openapi_generator():
        sys.exit(1)

    if not generate_client():
        sys.exit(1)

    print("\n" + "=" * 60)
    print("ГЕНЕРАЦИЯ ЗАВЕРШЕНА УСПЕШНО")
    print("=" * 60)
    print("\nСледующие шаги:")
    print(f"1. Проверьте сгенерированный клиент в {OUTPUT_DIR}")
    print("2. Пример использования уже создан в client/app/main.py")


if __name__ == "__main__":
    main()
