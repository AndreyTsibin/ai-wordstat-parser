#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import sys
import urllib.request
import urllib.error
import time


# API настройки
API_BASE_URL = "https://api.wordstat.yandex.net"
API_METHOD = "/v1/topRequests"


def load_env():
    """Загружает переменные окружения из файла .env"""
    env_path = '.env'

    if not os.path.exists(env_path):
        print("❌ Ошибка: файл .env не найден!")
        print("📝 Скопируйте .env.example в .env и добавьте токен")
        sys.exit(1)

    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

    token = os.getenv('YANDEX_WORDSTAT_TOKEN')
    if not token or token == 'your_token_here':
        print("❌ Ошибка: токен не настроен в .env")
        sys.exit(1)

    return token


def load_config():
    """Загружает настройки из config.json"""
    config_path = 'config.json'

    if not os.path.exists(config_path):
        print("❌ Ошибка: файл config.json не найден!")
        sys.exit(1)

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка парсинга config.json: {e}")
        sys.exit(1)

    # Валидация обязательных полей
    required_fields = ['business_info', 'parser_settings']
    for field in required_fields:
        if field not in config:
            print(f"❌ Ошибка: поле '{field}' отсутствует в config.json")
            sys.exit(1)

    return config


def load_queries():
    """Загружает список запросов из queries.txt"""
    queries_path = 'queries.txt'

    if not os.path.exists(queries_path):
        print("❌ Ошибка: файл queries.txt не найден!")
        print("📝 Используйте Claude Code для генерации запросов")
        sys.exit(1)

    with open(queries_path, 'r', encoding='utf-8') as f:
        queries = [line.strip() for line in f if line.strip()]

    if not queries:
        print("❌ Ошибка: queries.txt пустой!")
        sys.exit(1)

    return queries


def fetch_top_requests(token, phrase, region, devices, max_retries=3):
    """
    Получает топ популярных запросов для фразы из API Вордстата

    Args:
        token: OAuth токен
        phrase: Поисковая фраза
        region: Код региона (например, 213 для Москвы)
        devices: Список устройств ['desktop', 'mobile']
        max_retries: Количество попыток при ошибке

    Returns:
        dict: JSON с результатами или None при ошибке
    """
    url = API_BASE_URL + API_METHOD

    # Формируем тело запроса
    data = {
        "phrase": phrase,
        "regions": [region],
        "devices": devices
    }

    json_data = json.dumps(data).encode('utf-8')

    # Заголовки
    headers = {
        'Content-Type': 'application/json;charset=utf-8',
        'Authorization': f'Bearer {token}'
    }

    # Попытки запроса с ретраями
    for attempt in range(1, max_retries + 1):
        try:
            request = urllib.request.Request(
                url,
                data=json_data,
                headers=headers,
                method='POST'
            )

            with urllib.request.urlopen(request, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result

        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8') if e.fp else 'No details'
            print(f"   ⚠️ HTTP ошибка {e.code}: {error_body}")

            if attempt < max_retries:
                wait_time = 5 * attempt
                print(f"   🔄 Повтор через {wait_time} сек... (попытка {attempt}/{max_retries})")
                time.sleep(wait_time)
            else:
                print(f"   ❌ Не удалось получить данные после {max_retries} попыток")
                return None

        except urllib.error.URLError as e:
            print(f"   ⚠️ Ошибка соединения: {e.reason}")

            if attempt < max_retries:
                wait_time = 5 * attempt
                print(f"   🔄 Повтор через {wait_time} сек...")
                time.sleep(wait_time)
            else:
                return None

        except Exception as e:
            print(f"   ❌ Неожиданная ошибка: {e}")
            return None

    return None


def main():
    """Главная функция парсера"""
    print("🚀 Запуск парсера Яндекс Вордстат\n")

    # Загрузка конфигурации
    token = load_env()
    config = load_config()
    queries = load_queries()

    business = config['business_info']
    settings = config['parser_settings']

    print(f"📂 Регион: {business['city']} ({business['region_code']})")
    print(f"📱 Устройства: {', '.join(settings['devices'])}")
    print(f"📋 Загружено запросов: {len(queries)}\n")

    # ТЕСТ: запрос первой фразы
    print("🧪 Тестирование API...\n")
    test_phrase = queries[0]
    print(f"Тестовый запрос: {test_phrase}")

    result = fetch_top_requests(
        token=token,
        phrase=test_phrase,
        region=business['region_code'],
        devices=settings['devices']
    )

    if result:
        print(f"✅ API работает!")
        print(f"📊 Общая частотность: {result.get('totalCount', 0)}")
        print(f"📝 Получено фраз: {len(result.get('topRequests', []))}")

        # Показываем топ-5
        if result.get('topRequests'):
            print("\nТоп-5 фраз:")
            for i, item in enumerate(result['topRequests'][:5], 1):
                print(f"  {i}. {item['phrase']} — {item['count']}")
    else:
        print("❌ API не отвечает")


if __name__ == "__main__":
    main()
