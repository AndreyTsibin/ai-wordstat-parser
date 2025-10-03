#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Content Planner для генерации плана статей на основе результатов парсинга Яндекс Вордстат
"""

import json
import sys
from datetime import datetime
from collections import defaultdict


def load_config():
    """Загрузка конфигурации из config.json"""
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Ошибка: файл config.json не найден")
        sys.exit(1)
    except json.JSONDecodeError:
        print("❌ Ошибка: некорректный формат config.json")
        sys.exit(1)


def parse_results_md():
    """Парсинг results.md для извлечения данных о ключевых фразах"""
    try:
        with open('results.md', 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ Ошибка: файл results.md не найден. Запустите сначала parser.py")
        sys.exit(1)

    phrases = []
    lines = content.split('\n')

    # Парсим таблицы с фразами
    in_table = False
    for line in lines:
        # Определяем начало таблицы
        if line.startswith('| № | Фраза | Частотность | Тип |'):
            in_table = True
            continue

        # Пропускаем разделитель таблицы
        if in_table and line.startswith('|---|'):
            continue

        # Парсим строки таблицы
        if in_table and line.startswith('|'):
            parts = [p.strip() for p in line.split('|')[1:-1]]
            if len(parts) >= 4 and parts[0].isdigit():
                phrase_text = parts[1]
                # Убираем пометку о дубликате
                if '*(встречается в' in phrase_text:
                    phrase_text = phrase_text.split('*(встречается')[0].strip()

                try:
                    frequency = int(parts[2].replace(',', '').replace(' ', ''))
                except ValueError:
                    continue

                category_raw = parts[3]
                category = extract_category(category_raw)

                phrases.append({
                    'phrase': phrase_text,
                    'frequency': frequency,
                    'category': category
                })

        # Конец таблицы
        if in_table and line.strip() == '---':
            in_table = False

    return phrases


def extract_category(category_str):
    """Извлечение категории из строки с эмодзи"""
    category_map = {
        '🛒': 'commercial',
        '💰': 'price',
        '📚': 'informational',
        '⚖️': 'comparison',
        '📍': 'local',
        '🔍': 'other'
    }

    for emoji, cat in category_map.items():
        if emoji in category_str:
            return cat
    return 'other'


def extract_root_words(phrase):
    """
    Извлекает корневые слова из фразы для кластеризации

    Args:
        phrase: Фраза для анализа

    Returns:
        set: Набор значимых слов
    """
    # Стоп-слова (предлоги, союзы и т.д.)
    stop_words = {
        'в', 'на', 'и', 'с', 'под', 'для', 'по', 'от', 'до', 'из', 'к', 'о',
        'спб', 'санкт', 'петербург', 'москва', 'мск'
    }

    words = phrase.lower().split()
    # Убираем стоп-слова и короткие слова
    meaningful = {w for w in words if len(w) > 2 and w not in stop_words}

    return meaningful


def find_semantic_cluster(phrase, phrase_data, existing_clusters, min_common_words=2):
    """
    Находит семантический кластер для фразы на основе общих слов

    Args:
        phrase: Фраза для кластеризации
        phrase_data: Данные фразы (частотность, категория)
        existing_clusters: Существующие кластеры
        min_common_words: Минимальное количество общих слов

    Returns:
        str: Название кластера или None
    """
    phrase_words = extract_root_words(phrase)

    # Специальные паттерны для популярных тем
    special_patterns = {
        'под ключ': {'под', 'ключ'},
        'цена стоимость': {'цена', 'стоимость', 'сколько', 'стоит', 'прайс'},
        'хрущевка': {'хрущевк'},
        'маленькая': {'маленьк', 'небольш'},
        'детская': {'детск'},
        'гостиная': {'гостин'},
        'панельный дом': {'панельн'}
    }

    # Проверяем специальные паттерны
    for cluster_name, pattern_words in special_patterns.items():
        if any(word in phrase.lower() for word in pattern_words):
            return cluster_name

    # Ищем кластер с максимальным совпадением слов
    best_match = None
    max_common = 0

    for cluster_name, cluster_phrases in existing_clusters.items():
        # Берем первую фразу кластера как эталон
        if cluster_phrases:
            reference_phrase = cluster_phrases[0]['phrase']
            reference_words = extract_root_words(reference_phrase)
            common_words = phrase_words & reference_words

            if len(common_words) >= min_common_words and len(common_words) > max_common:
                max_common = len(common_words)
                best_match = cluster_name

    return best_match


def cluster_phrases(phrases, config):
    """Кластеризация фраз по темам статей с улучшенной семантической группировкой"""
    settings = config['content_plan_settings']
    min_freq = settings.get('min_frequency_threshold', 50)

    # Фильтруем фразы по минимальной частотности
    filtered = [p for p in phrases if p['frequency'] >= min_freq]

    # Сортируем по частотности (самые частотные будут создавать кластеры)
    filtered.sort(key=lambda x: x['frequency'], reverse=True)

    # Семантические кластеры
    semantic_clusters = defaultdict(list)

    for phrase_data in filtered:
        phrase = phrase_data['phrase']

        # Пытаемся найти существующий кластер
        cluster_name = find_semantic_cluster(phrase, phrase_data, semantic_clusters)

        if cluster_name:
            # Добавляем в существующий кластер
            semantic_clusters[cluster_name].append(phrase_data)
        else:
            # Создаем новый кластер на основе главных слов фразы
            root_words = extract_root_words(phrase)
            if root_words:
                # Используем 1-2 самых длинных слова как название кластера
                sorted_words = sorted(root_words, key=len, reverse=True)
                cluster_name = ' '.join(sorted_words[:2])
            else:
                cluster_name = phrase[:30]  # Fallback

            semantic_clusters[cluster_name].append(phrase_data)

    # Группируем также по категориям для совместимости
    category_clusters = defaultdict(list)
    for phrase_data in filtered:
        category_clusters[phrase_data['category']].append(phrase_data)

    # Сортируем каждую группу по частотности
    for cluster in semantic_clusters:
        semantic_clusters[cluster].sort(key=lambda x: x['frequency'], reverse=True)

    for category in category_clusters:
        category_clusters[category].sort(key=lambda x: x['frequency'], reverse=True)

    return category_clusters


def calculate_priority(frequency):
    """Расчет приоритета статьи на основе частотности"""
    if frequency >= 500:
        return "★★★★★", "Высокий"
    elif frequency >= 200:
        return "★★★★☆", "Средний"
    elif frequency >= 100:
        return "★★★☆☆", "Средний"
    elif frequency >= 50:
        return "★★☆☆☆", "Низкий"
    else:
        return "★☆☆☆☆", "Низкий"


def decline_word_prepositional(word):
    """
    Склонение слова в предложный падеж (отвечает на вопрос "о чём? где?")

    Args:
        word: Слово для склонения

    Returns:
        str: Слово в предложном падеже
    """
    word_lower = word.lower()

    # Словарь готовых форм для городов и частых слов
    prepositional_dict = {
        # Города
        'москва': 'Москве',
        'санкт-петербург': 'Санкт-Петербурге',
        'петербург': 'Петербурге',
        'казань': 'Казани',
        'екатеринбург': 'Екатеринбурге',
        'новосибирск': 'Новосибирске',
        'нижний новгород': 'Нижнем Новгороде',
        'самара': 'Самаре',
        'омск': 'Омске',
        'челябинск': 'Челябинске',
        'ростов-на-дону': 'Ростове-на-Дону',
        'уфа': 'Уфе',
        'красноярск': 'Красноярске',
        'воронеж': 'Воронеже',
        'пермь': 'Перми',
        'волгоград': 'Волгограде',
        'краснодар': 'Краснодаре',
        'саратов': 'Саратове',
        'тюмень': 'Тюмени',
        'тольятти': 'Тольятти',
        'ижевск': 'Ижевске',
        'барнаул': 'Барнауле',
        'ульяновск': 'Ульяновске',
        'иркутск': 'Иркутске',
        'хабаровск': 'Хабаровске',
        'ярославль': 'Ярославле',
        'владивосток': 'Владивостоке',
        'махачкала': 'Махачкале',
        'томск': 'Томске',
        'оренбург': 'Оренбурге',
        'кемерово': 'Кемерово',
        'новокузнецк': 'Новокузнецке',
        'рязань': 'Рязани',
        'астрахань': 'Астрахани',
        'набережные челны': 'Набережных Челнах',
        'пенза': 'Пензе',
        'киров': 'Кирове',
        'липецк': 'Липецке',
        'чебоксары': 'Чебоксарах',
        'калининград': 'Калининграде',
        'тула': 'Туле',
        'сочи': 'Сочи',
        'ставрополь': 'Ставрополе',
        'курск': 'Курске',
        'улан-удэ': 'Улан-Удэ',
        'тверь': 'Твери',
        'магнитогорск': 'Магнитогорске',
        'иваново': 'Иваново',
        'брянск': 'Брянске',
        'белгород': 'Белгороде',
        'сургут': 'Сургуте',
        'владимир': 'Владимире',
        'нижний тагил': 'Нижнем Тагиле',
        'архангельск': 'Архангельске',
        'чита': 'Чите',
        'калуга': 'Калуге',
        'смоленск': 'Смоленске',
        'волжский': 'Волжском',
        'якутск': 'Якутске',
        'саранск': 'Саранске',
        'череповец': 'Череповце',
        'вологда': 'Вологде',
        'владикавказ': 'Владикавказе',
        'грозный': 'Грозном',
        'мурманск': 'Мурманске',
        'тамбов': 'Тамбове',
        'петрозаводск': 'Петрозаводске',
        'кострома': 'Костроме',
        'орел': 'Орле',
        'новороссийск': 'Новороссийске',
        'йошкар-ола': 'Йошкар-Оле',

        # Страны
        'россия': 'России',
        'украина': 'Украине',
        'беларусь': 'Беларуси',
        'казахстан': 'Казахстане',
    }

    # Проверяем словарь
    if word_lower in prepositional_dict:
        return prepositional_dict[word_lower]

    # Правила склонения для незнакомых слов
    # Город на -бург → -бурге
    if word_lower.endswith('бург'):
        return word[:-1] + 'е'

    # Город на -ск → -ске
    if word_lower.endswith('ск'):
        return word + 'е'

    # Город на -град → -граде
    if word_lower.endswith('град'):
        return word + 'е'

    # Составные города через дефис (последнее слово склоняем)
    if '-' in word:
        parts = word.split('-')
        last_declined = decline_word_prepositional(parts[-1])
        return '-'.join(parts[:-1] + [last_declined])

    # Город на -а/-я (женский род) → -е
    if word_lower.endswith(('ва', 'на', 'ка', 'га', 'ха', 'ча', 'ща', 'ра', 'ла', 'ма', 'па', 'та', 'да')):
        return word[:-1] + 'е'

    if word_lower.endswith('я'):
        return word[:-1] + 'е'

    # Город на -ь (женский род) → -и
    if word_lower.endswith('ь'):
        return word[:-1] + 'и'

    # Город на -о/-е (средний род) → без изменений
    if word_lower.endswith(('во', 'ко', 'но', 'ро', 'ло', 'то', 'е')):
        return word

    # По умолчанию добавляем 'е' (мужской род)
    return word + 'е'


def capitalize_phrase(phrase):
    """
    Корректная капитализация фразы (первая буква заглавная, остальные как есть)

    Args:
        phrase: Фраза для капитализации

    Returns:
        str: Капитализированная фраза
    """
    if not phrase:
        return phrase
    return phrase[0].upper() + phrase[1:]


def generate_article_title(phrase, category, config, template_index=0):
    """Генерация заголовка статьи на основе ключевой фразы и категории"""
    city = config['business_info']['city']
    phrase_lower = phrase.lower()

    # Определяем варианты названия города
    if '-' in city:
        # Для составных городов: полное название и аббревиатура
        city_full = city
        city_abbr = ''.join([word[0].upper() for word in city.split('-')]) + 'б'  # СПб, НН и т.д.
    else:
        # Для обычных городов: только полное название
        city_full = city
        city_abbr = city

    # Склоняем город в предложный падеж (где? в чём?)
    city_prepositional = decline_word_prepositional(city_full)

    # Проверяем, есть ли уже город в фразе
    has_city_full = city_full.lower() in phrase_lower
    has_city_abbr = city_abbr.lower() in phrase_lower
    has_spb = 'спб' in phrase_lower  # для Санкт-Петербурга

    # Шаблоны заголовков для разных типов
    templates = {
        'commercial': [
            f"{capitalize_phrase(phrase)}: цены 2025, этапы работ",
            f"{capitalize_phrase(phrase)} в {city_prepositional}: выгодные условия" if not has_city_full else f"{capitalize_phrase(phrase)}: выгодные условия",
            f"{capitalize_phrase(phrase)} {city_abbr}: профессиональное качество" if not (has_city_abbr or has_spb) else f"{capitalize_phrase(phrase)}: профессиональное качество"
        ],
        'price': [
            f"Сколько стоит {phrase}" if not phrase_lower.startswith('сколько стоит') else capitalize_phrase(phrase),
            f"{capitalize_phrase(phrase)}: актуальные цены 2025 в {city_prepositional}" if not has_city_full else f"{capitalize_phrase(phrase)}: актуальные цены 2025",
            f"Стоимость {phrase} в {city_prepositional}" if not phrase_lower.startswith('стоимость') and not has_city_full else capitalize_phrase(phrase)
        ],
        'informational': [
            f"{capitalize_phrase(phrase)}: полное руководство в {city_prepositional}" if not has_city_full else f"{capitalize_phrase(phrase)}: полное руководство",
            f"Как выбрать: {phrase}",
            f"{capitalize_phrase(phrase)}: советы экспертов"
        ],
        'comparison': [
            f"{capitalize_phrase(phrase)}: какой вариант выбрать в {city_prepositional}" if not has_city_full else f"{capitalize_phrase(phrase)}: какой вариант выбрать",
            f"{capitalize_phrase(phrase)}: сравнение и отзывы"
        ],
        'other': [
            f"{capitalize_phrase(phrase)} в {city_prepositional}" if not has_city_full else capitalize_phrase(phrase),
            f"{capitalize_phrase(phrase)}: всё что нужно знать"
        ]
    }

    # Получаем список шаблонов для категории
    category_templates = templates.get(category, templates['other'])

    # Циклически выбираем шаблон для разнообразия
    template_idx = template_index % len(category_templates)
    return category_templates[template_idx]


def generate_content_plan(clusters, config):
    """Генерация финального плана статей"""
    business = config['business_info']
    settings = config['content_plan_settings']

    plan = {
        'meta': {
            'date': datetime.now().strftime('%d.%m.%Y %H:%M'),
            'site': business['site'],
            'niche': business['niche'],
            'city': business['city'],
            'target_page': settings['target_page'],
            'total_articles': 0,
            'planning_period_months': settings['planning_period_months'],
            'expected_traffic': settings['expected_traffic_per_month'],
            'conversion_rate': settings['conversion_rate_percent']
        },
        'blocks': []
    }

    # Генерируем блоки статей по категориям
    block_configs = settings['article_blocks']
    article_counter = 1

    for category, cat_config in block_configs.items():
        if category not in clusters or len(clusters[category]) == 0:
            continue

        block_phrases = clusters[category]
        block = {
            'category': category,
            'priority': cat_config['priority'],
            'articles_count': len(block_phrases),
            'articles': []
        }

        for idx, phrase_data in enumerate(block_phrases):
            stars, priority_text = calculate_priority(phrase_data['frequency'])

            article = {
                'number': article_counter,
                'title': generate_article_title(phrase_data['phrase'], phrase_data['category'], config, idx),
                'key_phrase': phrase_data['phrase'],
                'frequency': phrase_data['frequency'],
                'priority': priority_text,
                'stars': stars
            }

            block['articles'].append(article)
            article_counter += 1

        plan['blocks'].append(block)
        plan['meta']['total_articles'] += len(block_phrases)

    return plan


def format_markdown_plan(plan, config):
    """Форматирование плана статей в Markdown"""
    meta = plan['meta']
    business = config['business_info']
    settings = config['content_plan_settings']

    md = f"""# ПЛАН СТАТЕЙ: {business['niche'].upper()} {business['city'].upper()}

## 📊 Общая информация

**Целевая страница:** `{meta['target_page']}`
**Общее количество статей:** {meta['total_articles']}
**Период создания:** {meta['planning_period_months']} месяцев ({settings['articles_per_month']} статей в месяц)
**Ожидаемый результат:** {meta['expected_traffic']} органических переходов/месяц
**Конверсия в заявки:** {meta['conversion_rate']}%

---

"""

    # Генерируем блоки статей
    for idx, block in enumerate(plan['blocks'], 1):
        category_names = {
            'commercial': 'КОММЕРЧЕСКИЕ СТАТЬИ',
            'price': 'ЦЕНОВЫЕ СТАТЬИ',
            'informational': 'ИНФОРМАЦИОННЫЕ СТАТЬИ',
            'comparison': 'СРАВНИТЕЛЬНЫЕ СТАТЬИ',
            'other': 'ДОПОЛНИТЕЛЬНЫЕ СТАТЬИ'
        }

        total_traffic = sum(a['frequency'] for a in block['articles'])

        md += f"""## 🎯 БЛОК {idx}: {category_names.get(block['category'], block['category'].upper())} ({block['articles_count']} статей)
*Приоритет: {block['priority'].upper()} | Целевой трафик: {total_traffic:,}+ запросов/мес*

| № | Тема статьи | Ключевой запрос | Частотность | Приоритет |
|---|-------------|-----------------|-------------|-----------|
"""

        for article in block['articles']:
            md += f"| {article['number']} | **{article['title']}** | {article['key_phrase']} ({article['frequency']}) | {article['priority']} | {article['stars']} |\n"

        md += "\n---\n\n"

    # Добавляем календарный план
    md += generate_calendar_plan(plan, settings)

    # Добавляем целевые показатели
    md += generate_target_metrics(meta, settings)

    # Добавляем рекомендации по контенту
    md += generate_content_recommendations(business, settings)

    # Добавляем стратегию перелинковки
    md += generate_crosslinking_strategy(settings)

    return md


def generate_calendar_plan(plan, settings):
    """Генерация календарного плана публикаций"""
    articles_per_month = settings['articles_per_month']
    total = plan['meta']['total_articles']

    md = """## 📅 КАЛЕНДАРНЫЙ ПЛАН ПУБЛИКАЦИЙ

"""

    month = 1
    article_start = 1

    for block in plan['blocks']:
        articles_in_block = len(block['articles'])
        months_needed = (articles_in_block + articles_per_month - 1) // articles_per_month

        md += f"### **МЕСЯЦ {month}-{month + months_needed - 1}: {block['category'].capitalize()} блок ({articles_in_block} статей)**\n"
        md += f"**Приоритет:** {block['priority']}\n"
        md += f"- Статьи {article_start}-{article_start + articles_in_block - 1}\n\n"

        month += months_needed
        article_start += articles_in_block

    md += "\n---\n\n"
    return md


def generate_target_metrics(meta, settings):
    """Генерация целевых показателей"""
    md = """## 🎯 ЦЕЛЕВЫЕ ПОКАЗАТЕЛИ

### **После 3 месяцев:**
- **Органический трафик:** 30-40% от целевого
- **Позиции в ТОП-10:** 40% от общего числа запросов
- **Конверсия в заявки:** 1.5-2%

### **После 6 месяцев:**
- **Органический трафик:** """ + meta['expected_traffic'] + """ посетителей/месяц
- **Позиции в ТОП-10:** """ + str(settings['target_top_positions']) + """+ ключевых запросов
- **Конверсия в заявки:** """ + meta['conversion_rate'] + """%

---

"""
    return md


def generate_content_recommendations(business, settings):
    """Генерация рекомендаций по контенту"""
    utp_list = '\n'.join([f"✅ **{utp}**" for utp in business['utp']])

    md = f"""## 💡 РЕКОМЕНДАЦИИ ПО КОНТЕНТУ

### **Обязательные элементы каждой статьи:**
✅ **8-12 внутренних ссылок** на смежные страницы
{utp_list}
✅ **Контакты:** {settings['phone']}
✅ **Цены:** {settings['price_per_sqm']}
✅ **Локализация:** {business['city']}, районы

### **Структура статей:**
- **Объем:** {settings['article_length_words']} знаков
- **H2-H3:** 4-6 подзаголовков
- **Призывы к действию:** каждые 500-700 слов
- **Изображения:** фото работ, схемы, инфографика

### **SEO-требования:**
- **Плотность ключей:** 1-2%
- **LSI-слова:** мастер, бригада, смета, гарантия, материалы
- **Title:** до 60 символов с ключом
- **Description:** 150-160 символов с УТП

---

"""
    return md


def generate_crosslinking_strategy(settings):
    """Генерация стратегии перелинковки"""
    links = '\n'.join([f"{i+1}. `{link}`" for i, link in enumerate(settings['internal_links'])])
    anchors = '\n'.join([f'- "{anchor}"' for anchor in settings['anchor_texts']])

    md = f"""## 🔗 СТРАТЕГИЯ ПЕРЕЛИНКОВКИ

### **Приоритетные ссылки в каждой статье:**
{links}

### **Анкоры для ссылок:**
{anchors}

---

**ИТОГО: Полный план статей для продвижения в ТОП-10**

*Планируемый результат: органический трафик и лидогенерация*
"""
    return md


def save_content_plan(markdown_content):
    """Сохранение плана статей в файл"""
    output_file = 'content_plan.md'
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        print(f"✅ План статей сохранён в {output_file}")
        return output_file
    except Exception as e:
        print(f"❌ Ошибка при сохранении: {e}")
        sys.exit(1)


def main():
    """Главная функция"""
    print("🚀 Запуск AI Content Planner\n")

    # Загрузка конфигурации
    print("📂 Загрузка конфигурации...")
    config = load_config()

    # Парсинг results.md
    print("📊 Анализ results.md...")
    phrases = parse_results_md()
    print(f"   ✅ Найдено {len(phrases)} фраз")

    # Кластеризация фраз
    print("🔍 Кластеризация по темам...")
    clusters = cluster_phrases(phrases, config)
    print(f"   ✅ Создано {len(clusters)} категорий")

    # Генерация плана статей
    print("✍️  Генерация плана статей...")
    plan = generate_content_plan(clusters, config)
    print(f"   ✅ Запланировано {plan['meta']['total_articles']} статей")

    # Форматирование в Markdown
    print("📝 Форматирование в Markdown...")
    markdown = format_markdown_plan(plan, config)

    # Сохранение
    print("💾 Сохранение плана...")
    save_content_plan(markdown)

    print("\n🎉 Готово! План статей сформирован")


if __name__ == '__main__':
    main()
