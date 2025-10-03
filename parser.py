#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import sys


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


def main():
    """Главная функция парсера"""
    print("🚀 Запуск парсера Яндекс Вордстат\n")

    # Загрузка конфигурации
    token = load_env()
    config = load_config()
    queries = load_queries()

    # Вывод информации
    business = config['business_info']
    settings = config['parser_settings']

    print(f"📂 Регион: {business['city']} ({business['region_code']})")
    print(f"📱 Устройства: {', '.join(settings['devices'])}")
    print(f"📋 Загружено запросов: {len(queries)}")
    print(f"🔑 Токен: {'✅ Загружен' if token else '❌ Отсутствует'}\n")

    # Список запросов
    print("Список запросов:")
    for i, query in enumerate(queries, 1):
        print(f"  {i}. {query}")


if __name__ == "__main__":
    main()
