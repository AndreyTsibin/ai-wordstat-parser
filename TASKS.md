# TASKS.md

## 📋 Атомарные задачи для Claude Code

> **Инструкция:** Выполняй задачи последовательно. Каждая задача = один коммит. Не переходи к следующей, пока текущая не выполнена и не протестирована.

---

## ✅ TASK-01: Создать структуру проекта и базовые файлы

**Цель:** Подготовить инфраструктуру проекта для разработки.

**Что нужно сделать:**

1. Создать корневую папку проекта `wordstat-parser/`

2. Создать следующие файлы:
   - `.env.example`
   - `.gitignore`
   - `config.json`
   - `queries.txt` (пустой)
   - `parser.py` (пустой, только shebang)
   - `README.md`

3. **Содержимое `.env.example`:**
```env
# Яндекс Вордстат OAuth токен
# Получить: https://oauth.yandex.ru/
YANDEX_WORDSTAT_TOKEN=your_token_here
```

4. **Содержимое `.gitignore`:**
```
# Секретные данные
.env

# Результаты работы
results.md

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python

# IDE
.vscode/
.idea/
*.swp
*.swo
```

5. **Содержимое `config.json`:**
```json
{
  "business_info": {
    "site": "example.com",
    "niche": "ваша ниша",
    "city": "Москва",
    "region_code": 213,
    "services": [
      "услуга 1",
      "услуга 2",
      "услуга 3"
    ],
    "competitors": [
      "https://competitor1.com",
      "https://competitor2.com"
    ],
    "budget": "10-20 статей/месяц",
    "utp": [
      "ваше преимущество 1",
      "ваше преимущество 2"
    ]
  },
  "parser_settings": {
    "devices": ["desktop", "mobile"],
    "top_results_limit": 50,
    "delay_between_requests": 2
  }
}
```

6. **Содержимое `README.md`:**
```markdown
# Яндекс Вордстат Парсер

Автоматический парсер поисковых запросов через API Яндекс Вордстат для SEO-планирования.

## 🚀 Быстрый старт

### 1. Установка

```bash
git clone https://github.com/your-username/wordstat-parser.git
cd wordstat-parser
```

### 2. Настройка токена

Скопируйте `.env.example` в `.env`:
```bash
cp .env.example .env
```

Получите OAuth-токен:
1. Откройте https://oauth.yandex.ru/
2. Создайте приложение с доступом к API Вордстата
3. Скопируйте ClientID
4. Получите токен по ссылке: 
   ```
   https://oauth.yandex.ru/authorize?response_type=token&client_id=ВАШ_CLIENT_ID
   ```
5. Вставьте токен в файл `.env`

### 3. Настройка бизнес-информации

Отредактируйте `config.json`:
- Укажите вашу нишу, город, услуги
- Добавьте конкурентов и УТП

### 4. Генерация запросов

Используйте Claude Code для генерации `queries.txt`:
```bash
claude-code "Прочитай config.json и сгенерируй queries.txt с поисковыми запросами"
```

### 5. Запуск парсера

```bash
python parser.py
```

Результаты сохранятся в `results.md`.

### 6. Создание контент-плана

```bash
claude-code "Проанализируй results.md и создай контент-план"
```

## 📁 Структура проекта

```
wordstat-parser/
├── .env              # Токен (не коммитится)
├── .env.example      # Шаблон для токена
├── config.json       # Настройки бизнеса
├── queries.txt       # Список запросов
├── parser.py         # Основной скрипт
└── results.md        # Результаты парсинга
```

## 📝 Требования

- Python 3.8+
- Нет внешних зависимостей (только stdlib)

## 📄 Лицензия

MIT
```

7. **Содержимое `parser.py` (только shebang):**
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
```

**Критерии приёмки:**
- ✅ Все файлы созданы с правильным содержимым
- ✅ `.gitignore` исключает `.env` и `results.md`
- ✅ `config.json` содержит валидный JSON
- ✅ `README.md` содержит инструкции

**Коммит:** `feat: initialize project structure with base files`

---

## ✅ TASK-02: Реализовать загрузку конфигурации

**Цель:** Создать функции для чтения `.env`, `config.json` и `queries.txt`.

**Что нужно сделать:**

1. Открыть `parser.py`

2. Добавить импорты:
```python
import os
import json
import sys
```

3. Создать функцию `load_env()`:
```python
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
```

4. Создать функцию `load_config()`:
```python
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
```

5. Создать функцию `load_queries()`:
```python
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
```

6. Добавить главную функцию для тестирования:
```python
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
```

**Критерии приёмки:**
- ✅ Функции корректно читают файлы
- ✅ Валидация отсутствующих файлов работает
- ✅ Валидация пустого токена работает
- ✅ Запуск `python parser.py` показывает загруженные данные
- ✅ Если нет `.env` — выводится понятная ошибка

**Тестирование:**
1. Создайте `.env` с токеном
2. Заполните `queries.txt` (3-5 тестовых запросов)
3. Запустите `python parser.py`
4. Проверьте, что все данные загружены

**Коммит:** `feat: add config loading functions (env, json, queries)`

---

## ✅ TASK-03: Реализовать API клиент для Яндекс Вордстат

**Цель:** Создать функцию для запросов к API `/v1/topRequests`.

**Что нужно сделать:**

1. Добавить импорты в начало `parser.py`:
```python
import urllib.request
import urllib.error
import time
```

2. Добавить константы API:
```python
# API настройки
API_BASE_URL = "https://api.wordstat.yandex.net"
API_METHOD = "/v1/topRequests"
```

3. Создать функцию `fetch_top_requests()`:
```python
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
```

4. Обновить функцию `main()` для тестирования API:
```python
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
```

**Критерии приёмки:**
- ✅ Функция отправляет корректный POST-запрос
- ✅ Retry-логика работает (3 попытки с задержкой)
- ✅ Обрабатываются HTTP и сетевые ошибки
- ✅ Запуск `python parser.py` показывает результат тестового запроса
- ✅ При ошибке токена — понятное сообщение

**Тестирование:**
1. Запустите `python parser.py`
2. Проверьте, что получен ответ от API
3. Намеренно укажите неверный токен — проверьте обработку ошибки

**Коммит:** `feat: add Wordstat API client with retry logic`

---

## ✅ TASK-04: Реализовать категоризацию ключевых слов

**Цель:** Создать функцию для определения типа фразы (коммерческая, информационная, ценовая, локальная).

**Что нужно сделать:**

1. Добавить словари с ключевыми словами после констант API:
```python
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
```

2. Создать функцию `categorize_phrase()`:
```python
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
```

3. Создать функцию для отслеживания дубликатов:
```python
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
```

4. Обновить `main()` для тестирования категоризации:
```python
def main():
    """Главная функция парсера"""
    print("🚀 Запуск парсера Яндекс Вордстат\n")
    
    # Загрузка конфигурации
    token = load_env()
    config = load_config()
    queries = load_queries()
    
    business = config['business_info']
    settings = config['parser_settings']
    city = business['city']
    
    print(f"📂 Регион: {city} ({business['region_code']})")
    print(f"📋 Загружено запросов: {len(queries)}\n")
    
    # ТЕСТ: категоризация
    print("🧪 Тестирование категоризации...\n")
    
    test_phrases = [
        "купить ноутбук москва",
        "как выбрать ноутбук",
        "стоимость ноутбука",
        "ноутбук отзывы",
        "ноутбук купить"
    ]
    
    for phrase in test_phrases:
        category, emoji = categorize_phrase(phrase, city)
        print(f"{emoji} {phrase} → {category}")

if __name__ == "__main__":
    main()
```

**Критерии приёмки:**
- ✅ Функция корректно определяет коммерческие фразы
- ✅ Функция корректно определяет информационные фразы
- ✅ Функция корректно определяет ценовые фразы
- ✅ Локальные фразы помечаются флагом 📍
- ✅ Запуск `python parser.py` показывает примеры категоризации

**Тестирование:**
Запустите `python parser.py` и проверьте, что тестовые фразы категоризируются правильно.

**Коммит:** `feat: add keyword categorization with emoji markers`

---

## ✅ TASK-05: Реализовать генерацию Markdown отчёта

**Цель:** Создать функции для форматирования результатов в `results.md`.

**Что нужно сделать:**

1. Создать функцию для форматирования чисел:
```python
def format_number(num):
    """Форматирует число с разделителями тысяч"""
    return f"{num:,}".replace(',', ' ')
```

2. Создать функцию генерации заголовка документа:
```python
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
```

3. Создать функцию генерации таблицы для запроса:
```python
def generate_query_section(query_num, query, result, city, limit, seen_phrases):
    """
    Генерирует секцию Markdown для одного запроса
    
    Args:
        query_num: Номер запроса
        query: Текст запроса
        result: Результат от API
        city: Название города
        limit: Лимит фраз для вывода
        seen_phrases: Словарь отслеживания дубликатов
    
    Returns:
        str: Markdown секция
    """
    if not result or 'topRequests' not in result:
        return f"## 🔍 Запрос {query_num}: {query}\n\n❌ Не удалось получить данные\n\n---\n\n"
    
    total_count = result.get('totalCount', 0)
    phrases = result.get('topRequests', [])
    
    # Сортируем по частотности
    phrases_sorted = sorted(phrases, key=lambda x: x['count'], reverse=True)
    top_phrases = phrases_sorted[:limit]
    
    section = f"""## 🔍 Запрос {query_num}: {query}

**Общая частотность:** {format_number(total_count)} показов/мес  
**Найдено фраз:** {len(phrases)}  
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
```

4. Создать функцию генерации сводной статистики:
```python
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
```

5. Создать главную функцию сохранения:
```python
def save_results(config, queries, all_results, seen_phrases):
    """Сохраняет результаты в results.md"""
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%d.%m.%Y %H:%M")
    
    # Генерируем документ
    content = generate_header(config, len(queries), timestamp)
    
    # Добавляем секции для каждого запроса
    limit = config['parser_settings']['top_results_limit']
    city = config['business_info']['city']
    
    for i, (query, result) in enumerate(zip(queries, all_results), 1):
        section = generate_query_section(i, query, result, city, limit, seen_phrases)
        content += section
    
    # Добавляем сводную статистику
    content += generate_summary([r for r in all_results if r], seen_phrases)
    
    # Сохраняем
    with open('results.md', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n✅ Результаты сохранены в results.md")
```

**Критерии приёмки:**
- ✅ Функции генерируют корректный Markdown
- ✅ Таблицы правильно отформатированы
- ✅ Числа форматируются с пробелами (1 520 вместо 1520)
- ✅ Дубликаты помечаются
- ✅ Сводная статистика содержит топ-10

**Тестирование:**
Пока только проверка синтаксиса — полное тестирование в следующей задаче.

**Коммит:** `feat: add Markdown report generation functions`

---

## ✅ TASK-06: Интегрировать все компоненты и добавить логирование

**Цель:** Собрать финальный парсер с прогресс-баром и обработкой всех запросов.

**Что нужно сделать:**

1. Переписать функцию `main()`:
```python
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
    
    print(f"📂 Регион: {business['city']} ({business['region_code']})")
    print(f"📱 Устройства: {', '.join(settings['devices'])}")
    print(f"📋 Загружено запросов: {len(queries)}\n")
    
    # Хранилище результатов
    all_results = []
    seen_phrases = {}
    
    # Обработка каждого запроса
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
    
    # Подсчёт успешных запросов
    successful = sum(1 for r in all_results if r)
    failed = len(queries) - successful
    
    print(f"{'='*50}")
    print(f"📊 Обработано: {successful}/{len(queries)} запросов")
    if failed > 0:
        print(f"⚠️  Неудачных: {failed}")
    
    # Сохранение результатов
    if successful > 0:
        save_results(config, queries, all_results, seen_phrases)
        
        # Подсчёт всех уникальных фраз
        unique_phrases = len(seen_phrases)
        print(f"📝 Найдено уникальных фраз: {unique_phrases}")
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
```

**Критерии приёмки:**
- ✅ Парсер обрабатывает все запросы из `queries.txt`
- ✅ Показывается прогресс `[1/15]`
- ✅ Логируется результат каждого запроса
- ✅ Работает задержка между запросами
- ✅ Подсчитывается время выполнения
- ✅ Генерируется `results.md` с полными данными

**Тестирование:**
1. Заполните `queries.txt` 5-7 реальными запросами
2. Запустите `python parser.py`
3. Проверьте консольный вывод
4. Откройте `results.md` и проверьте таблицы

**Коммит:** `feat: integrate all components with progress logging`

---

## ✅ TASK-07: Финальное тестирование и документация

**Цель:** Протестировать парсер с реальными данными и обновить документацию.

**Что нужно сделать:**

1. **Создать файл `config.json.example`** с примером настроек:
```json
{
  "business_info": {
    "site": "example.com",
    "niche": "ремонт квартир",
    "city": "Москва",
    "region_code": 213,
    "services": [
      "косметический ремонт",
      "капитальный ремонт",
      "дизайнерский ремонт"
    ],
    "competitors": [
      "https://competitor1.com",
      "https://competitor2.com"
    ],
    "budget": "10-20 статей/месяц",
    "utp": [
      "гарантия 5 лет",
      "ремонт за 30 дней",
      "фиксированная цена"
    ]
  },
  "parser_settings": {
    "devices": ["desktop", "mobile"],
    "top_results_limit": 50,
    "delay_between_requests": 2
  }
}
```

2. **Создать тестовый `queries.txt`** с реальными запросами для проверки:
```
ремонт квартир москва
ремонт квартир москва под ключ
стоимость ремонта квартир москва
капитальный ремонт квартир москва
косметический ремонт квартир москва
```

3. **Обновить README.md** — добавить секцию "Примеры результатов":
```markdown
## 📊 Примеры результатов

После запуска парсера вы получите `results.md` со следующей структурой:

### Результат для одного запроса:

| № | Фраза | Частотность | Тип |
|---|-------|-------------|-----|
| 1 | ремонт квартир москва под ключ | 1 520 | 📍 🛒 Commercial |
| 2 | ремонт квартир москва недорого | 890 | 📍 🛒 Commercial |
| 3 | как выбрать ремонтную компанию москва | 340 | 📍 📚 Informational |

### Сводная статистика:

- Топ-10 самых частотных фраз
- Список дубликатов
- Общее количество уникальных ключей
```

4. **Протестировать edge cases:**
   - Запуск без `.env` → проверить ошибку
   - Запуск с пустым `queries.txt` → проверить ошибку
   - Запуск с неверным токеном → проверить обработку HTTP 401
   - Запуск с 1 запросом → проверить корректность
   - Запуск с 10+ запросами → проверить время и результаты

5. **Добавить секцию FAQ в README:**
```markdown
## ❓ FAQ

**Q: Как получить токен API?**  
A: Следуйте инструкции в разделе "Настройка токена"

**Q: Какой лимит запросов в API?**  
A: API имеет дневную квоту. Для бета-версии проверьте лимиты в документации Яндекса.

**Q: Можно ли парсить несколько регионов?**  
A: В текущей версии — один регион. Для нескольких создайте отдельные `config.json`.

**Q: Как изменить количество выводимых фраз?**  
A: Измените `top_results_limit` в `config.json`.

**Q: Парсер падает с ошибкой, что делать?**  
A: Проверьте наличие `.env`, валидность токена, корректность `queries.txt`.
```

**Критерии приёмки:**
- ✅ Парсер успешно обрабатывает 10+ запросов
- ✅ `results.md` корректно форматирован и читается
- ✅ Все edge cases обработаны
- ✅ README содержит полную документацию
- ✅ Примеры файлов созданы

**Финальное тестирование:**
1. Удалите все сгенерированные файлы (`.env`, `results.md`)
2. Следуйте инструкциям в README от начала до конца
3. Убедитесь, что парсер работает у "нового пользователя"

**Коммит:** `docs: add examples and FAQ, complete testing`

---

## 🎯 Порядок выполнения задач

Выполняй строго последовательно:
1. TASK-01 → коммит → проверка
2. TASK-02 → коммит → проверка
3. TASK-03 → коммит → проверка
4. TASK-04 → коммит → проверка
5. TASK-05 → коммит → проверка
6. TASK-06 → коммит → проверка
7. TASK-07 → коммит → завершение

После каждой задачи делай коммит с указанным сообщением.

---

## ✅ Финальный чеклист

После выполнения всех задач проверь:

- [ ] Все файлы созданы согласно структуре
- [ ] `.gitignore` исключает `.env` и `results.md`
- [ ] Парсер запускается без ошибок
- [ ] Генерируется корректный `results.md`
- [ ] README содержит полную инструкцию
- [ ] Обработаны все edge cases
- [ ] Код следует PEP 8
- [ ] Все функции имеют docstrings

**После проверки:** Готово к пушу в GitHub! 🚀