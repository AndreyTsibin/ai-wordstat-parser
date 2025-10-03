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

# Словари для категоризации
CATEGORY_KEYWORDS = {
    'commercial': [
        'купить', 'заказать', 'под ключ', 'недорого', 'дешево',
        'цена', 'стоимость', 'прайс', 'акция', 'скидка',
        'доставка', 'установка', 'монтаж', 'вызвать', 'услуги'
    ],
    'informational': [
        'как', 'что такое', 'почему', 'зачем', 'когда',
        'где', 'какой', 'какая', 'какие', 'способы',
        'методы', 'инструкция', 'руководство', 'советы', 'этапы'
    ],
    'price': [
        'цена', 'стоимость', 'прайс', 'сколько стоит',
        'расценки', 'тариф', 'стоит', 'за квадратный метр'
    ],
    'comparison': [
        'отзывы', 'рейтинг', 'лучшие', 'топ', 'сравнение',
        'vs', 'или', 'какой выбрать', 'что лучше'
    ]
}

# Эмодзи для типов
CATEGORY_EMOJI = {
    'commercial': '🛒',
    'informational': '📚',
    'price': '💰',
    'comparison': '⚖️',
    'local': '📍',
    'other': '🔍'
}


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


def has_minus_words(phrase, minus_words):
    """
    Проверяет, содержит ли фраза минус-слова

    Args:
        phrase: Поисковая фраза
        minus_words: Список минус-слов

    Returns:
        bool: True если фраза содержит минус-слова
    """
    if not minus_words:
        return False

    phrase_lower = phrase.lower()
    for minus_word in minus_words:
        if minus_word.lower() in phrase_lower:
            return True
    return False


def categorize_phrase(phrase, city_name):
    """
    Определяет тип поисковой фразы

    Args:
        phrase: Поисковая фраза
        city_name: Название города для определения локальных запросов

    Returns:
        tuple: (категория, эмодзи)
    """
    phrase_lower = phrase.lower()

    # Проверка на локальность
    is_local = city_name.lower() in phrase_lower

    # Приоритет: price > commercial > informational > comparison
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in phrase_lower:
                emoji = CATEGORY_EMOJI.get(category, '🔍')
                # Добавляем флаг локальности
                if is_local and category != 'informational':
                    emoji = f"{CATEGORY_EMOJI['local']} {emoji}"
                return category.capitalize(), emoji

    # Если не подошла ни одна категория
    emoji = CATEGORY_EMOJI['local'] if is_local else CATEGORY_EMOJI['other']
    return 'Other', emoji


def track_duplicates(all_phrases):
    """
    Отслеживает дубликаты фраз и считает вхождения

    Args:
        all_phrases: Словарь {фраза: [список запросов, где встречается]}

    Returns:
        dict: Словарь с дубликатами
    """
    duplicates = {}

    for phrase, sources in all_phrases.items():
        if len(sources) > 1:
            duplicates[phrase] = len(sources)

    return duplicates


def format_number(num):
    """Форматирует число с разделителями тысяч"""
    return f"{num:,}".replace(',', ' ')


def generate_header(config, total_queries, timestamp):
    """Генерирует шапку Markdown документа"""
    business = config['business_info']
    settings = config['parser_settings']

    header = f"""# 📊 Результаты парсинга Яндекс Вордстат

**Дата:** {timestamp}
**Регион:** {business['city']} ({business['region_code']})
**Устройства:** {', '.join(settings['devices'])}
**Обработано запросов:** {total_queries}

---

"""
    return header


def filter_phrases_by_minus_words(phrases, minus_words):
    """
    Фильтрует фразы по минус-словам

    Args:
        phrases: Список фраз из API
        minus_words: Список минус-слов

    Returns:
        tuple: (отфильтрованные фразы, удаленные фразы)
    """
    if not minus_words:
        return phrases, []

    filtered = []
    removed = []

    for phrase_data in phrases:
        phrase = phrase_data['phrase']
        if has_minus_words(phrase, minus_words):
            removed.append(phrase)
        else:
            filtered.append(phrase_data)

    return filtered, removed


def generate_query_section(query_num, query, result, city, limit, seen_phrases, minus_words=None):
    """
    Генерирует секцию Markdown для одного запроса

    Args:
        query_num: Номер запроса
        query: Текст запроса
        result: Результат от API
        city: Название города
        limit: Лимит фраз для вывода
        seen_phrases: Словарь отслеживания дубликатов
        minus_words: Список минус-слов для фильтрации

    Returns:
        str: Markdown секция
    """
    if not result or 'topRequests' not in result:
        return f"## 🔍 Запрос {query_num}: {query}\n\n❌ Не удалось получить данные\n\n---\n\n"

    total_count = result.get('totalCount', 0)
    phrases = result.get('topRequests', [])

    # Фильтруем по минус-словам
    filtered_phrases, removed_phrases = filter_phrases_by_minus_words(phrases, minus_words or [])

    # Сортируем по частотности
    phrases_sorted = sorted(filtered_phrases, key=lambda x: x['count'], reverse=True)
    top_phrases = phrases_sorted[:limit]

    removed_note = f"\n**Отфильтровано по минус-словам:** {len(removed_phrases)}" if removed_phrases else ""

    section = f"""## 🔍 Запрос {query_num}: {query}

**Общая частотность:** {format_number(total_count)} показов/мес
**Найдено фраз:** {len(phrases)}{removed_note}
**Топ-{limit} по частотности:**

| № | Фраза | Частотность | Тип |
|---|-------|-------------|-----|
"""

    for i, item in enumerate(top_phrases, 1):
        phrase_text = item['phrase']
        count = format_number(item['count'])
        category, emoji = categorize_phrase(phrase_text, city)

        # Отслеживание дубликатов
        if phrase_text in seen_phrases:
            seen_phrases[phrase_text].append(query)
            duplicate_mark = f" *(встречается в {len(seen_phrases[phrase_text])} запросах)*"
        else:
            seen_phrases[phrase_text] = [query]
            duplicate_mark = ""

        section += f"| {i} | {phrase_text}{duplicate_mark} | {count} | {emoji} {category} |\n"

    section += "\n---\n\n"
    return section


def generate_summary(all_results, seen_phrases):
    """Генерирует сводную статистику"""
    # Собираем все фразы
    all_phrases_list = []
    for result in all_results:
        if result and 'topRequests' in result:
            all_phrases_list.extend(result['topRequests'])

    # Сортируем по частотности
    all_phrases_sorted = sorted(all_phrases_list, key=lambda x: x['count'], reverse=True)
    top_10 = all_phrases_sorted[:10]

    summary = """## 📈 Сводная статистика

**Топ-10 самых частотных фраз по всем запросам:**

| № | Фраза | Частотность |
|---|-------|-------------|
"""

    for i, item in enumerate(top_10, 1):
        phrase = item['phrase']
        count = format_number(item['count'])
        summary += f"| {i} | {phrase} | {count} |\n"

    # Статистика дубликатов
    duplicates = {k: v for k, v in seen_phrases.items() if len(v) > 1}

    if duplicates:
        summary += f"\n**Фразы, встречающиеся в нескольких запросах:** {len(duplicates)}\n"

    return summary


def save_results(config, queries, all_results, seen_phrases):
    """Сохраняет результаты в results.md"""
    from datetime import datetime

    timestamp = datetime.now().strftime("%d.%m.%Y %H:%M")

    # Генерируем документ
    content = generate_header(config, len(queries), timestamp)

    # Добавляем секции для каждого запроса
    limit = config['parser_settings']['top_results_limit']
    city = config['business_info']['city']
    minus_words = config['parser_settings'].get('minus_words', [])

    for i, (query, result) in enumerate(zip(queries, all_results), 1):
        section = generate_query_section(i, query, result, city, limit, seen_phrases, minus_words)
        content += section

    # Добавляем сводную статистику
    content += generate_summary([r for r in all_results if r], seen_phrases)

    # Сохраняем
    with open('results.md', 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"\n✅ Результаты сохранены в results.md")


def collect_top_phrases_for_recursion(all_results, minus_words, top_n=10):
    """
    Собирает топ N фраз для рекурсивного парсинга

    Args:
        all_results: Результаты парсинга
        minus_words: Список минус-слов
        top_n: Количество топ фраз

    Returns:
        list: Список фраз для рекурсивного парсинга
    """
    all_phrases = []

    for result in all_results:
        if result and 'topRequests' in result:
            phrases = result['topRequests']
            # Фильтруем по минус-словам
            filtered, _ = filter_phrases_by_minus_words(phrases, minus_words)
            all_phrases.extend(filtered)

    # Сортируем по частотности и берем топ N
    sorted_phrases = sorted(all_phrases, key=lambda x: x['count'], reverse=True)
    top_phrases = sorted_phrases[:top_n]

    return [p['phrase'] for p in top_phrases]


def save_to_csv(seen_phrases, minus_words):
    """Сохраняет результаты в CSV для удобства работы"""
    import csv

    # Собираем все фразы с их данными
    phrases_data = []
    for phrase, sources in seen_phrases.items():
        if not has_minus_words(phrase, minus_words):
            # Получаем частотность из первого источника (она одинакова)
            phrases_data.append({
                'phrase': phrase,
                'sources_count': len(sources)
            })

    # Сохраняем CSV
    with open('results.csv', 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Фраза', 'Встречается в запросах'])

        for data in phrases_data:
            writer.writerow([data['phrase'], data['sources_count']])

    print(f"📊 Экспорт в CSV: results.csv")


def main():
    """Главная функция парсера"""
    from datetime import datetime

    start_time = datetime.now()

    print("🚀 Запуск парсера Яндекс Вордстат\n")

    # Загрузка конфигурации
    token = load_env()
    config = load_config()
    queries = load_queries()

    business = config['business_info']
    settings = config['parser_settings']

    recursive_enabled = settings.get('recursive_parsing', False)
    recursion_depth = settings.get('recursion_depth', 2)
    recursive_top_n = settings.get('recursive_top_queries', 10)
    minus_words = settings.get('minus_words', [])

    print(f"📂 Регион: {business['city']} ({business['region_code']})")
    print(f"📱 Устройства: {', '.join(settings['devices'])}")
    print(f"📋 Загружено запросов: {len(queries)}")
    if recursive_enabled:
        print(f"🔄 Рекурсивный парсинг: ВКЛ (глубина: {recursion_depth}, топ: {recursive_top_n})")
    if minus_words:
        print(f"🚫 Минус-слова: {len(minus_words)} шт.")
    print()

    # Хранилище результатов
    all_results = []
    seen_phrases = {}
    all_queries = list(queries)  # Копия для рекурсии

    # УРОВЕНЬ 1: Обработка базовых запросов
    print(f"{'='*50}")
    print("📍 УРОВЕНЬ 1: Базовые запросы")
    print(f"{'='*50}\n")

    for i, query in enumerate(queries, 1):
        print(f"[{i}/{len(queries)}] Парсинг: \"{query}\"")

        result = fetch_top_requests(
            token=token,
            phrase=query,
            region=business['region_code'],
            devices=settings['devices']
        )

        if result and 'topRequests' in result:
            total_count = result.get('totalCount', 0)
            phrases_count = len(result.get('topRequests', []))
            print(f"   ✅ Получено {phrases_count} фраз ({format_number(total_count)} показов/мес)")
        else:
            print(f"   ❌ Не удалось получить данные")

        all_results.append(result)

        # Задержка между запросами (кроме последнего)
        if i < len(queries):
            delay = settings['delay_between_requests']
            print(f"   ⏳ Ожидание {delay} сек...\n")
            time.sleep(delay)
        else:
            print()

    # УРОВЕНЬ 2: Рекурсивный парсинг
    if recursive_enabled and recursion_depth >= 2:
        print(f"\n{'='*50}")
        print("📍 УРОВЕНЬ 2: Рекурсивный парсинг топ фраз")
        print(f"{'='*50}\n")

        # Собираем топ фразы для рекурсии
        recursive_queries = collect_top_phrases_for_recursion(all_results, minus_words, recursive_top_n)
        print(f"🎯 Отобрано {len(recursive_queries)} фраз для рекурсивного парсинга\n")

        for i, query in enumerate(recursive_queries, 1):
            # Пропускаем уже запрошенные фразы
            if query in all_queries:
                continue

            all_queries.append(query)
            print(f"[{i}/{len(recursive_queries)}] Парсинг (L2): \"{query}\"")

            result = fetch_top_requests(
                token=token,
                phrase=query,
                region=business['region_code'],
                devices=settings['devices']
            )

            if result and 'topRequests' in result:
                total_count = result.get('totalCount', 0)
                phrases_count = len(result.get('topRequests', []))
                print(f"   ✅ Получено {phrases_count} фраз ({format_number(total_count)} показов/мес)")
            else:
                print(f"   ❌ Не удалось получить данные")

            all_results.append(result)

            # Задержка между запросами
            if i < len(recursive_queries):
                delay = settings['delay_between_requests']
                print(f"   ⏳ Ожидание {delay} сек...\n")
                time.sleep(delay)
            else:
                print()

    # Подсчёт успешных запросов
    successful = sum(1 for r in all_results if r)
    failed = len(all_queries) - successful

    print(f"{'='*50}")
    print(f"📊 Обработано: {successful}/{len(all_queries)} запросов")
    if failed > 0:
        print(f"⚠️  Неудачных: {failed}")

    # Сохранение результатов
    if successful > 0:
        save_results(config, all_queries, all_results, seen_phrases)

        # Подсчёт всех уникальных фраз
        unique_phrases = len(seen_phrases)
        print(f"📝 Найдено уникальных фраз: {unique_phrases}")

        # Экспорт в CSV
        save_to_csv(seen_phrases, minus_words)
    else:
        print("❌ Нет данных для сохранения")

    # Время выполнения
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    print(f"⏱️  Время выполнения: {duration:.1f} сек")
    print(f"\n{'='*50}")
    print("🎉 Парсинг завершён!")


if __name__ == "__main__":
    main()
