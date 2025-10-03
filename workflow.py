#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Workflow Orchestrator - Полная автоматизация от конфигурации до контент-плана

Запуск: python3 workflow.py
"""

import json
import subprocess
import sys
import time
from datetime import datetime


def print_header(text):
    """Красивый заголовок"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")


def print_step(step_num, total_steps, description):
    """Вывод текущего шага"""
    print(f"📍 ШАГ {step_num}/{total_steps}: {description}")
    print("-" * 60)


def load_config():
    """Загрузка и валидация конфигурации"""
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)

        # Проверка обязательных полей
        required_fields = ['business_info', 'parser_settings', 'content_plan_settings']
        for field in required_fields:
            if field not in config:
                print(f"❌ Ошибка: отсутствует секция '{field}' в config.json")
                sys.exit(1)

        return config

    except FileNotFoundError:
        print("❌ Ошибка: файл config.json не найден")
        print("💡 Создайте config.json на основе примера из документации")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка в config.json: {e}")
        sys.exit(1)


def generate_queries(config):
    """Генерация поисковых запросов на основе config.json"""
    print("🤖 Генерация поисковых запросов на основе бизнес-информации...")

    business = config['business_info']
    niche = business['niche']
    city = business['city']
    services = business['services']

    # Базовые шаблоны запросов
    queries = []

    # 1. Прямые запросы по нише
    city_short = 'спб' if 'санкт-петербург' in city.lower() else city.lower()
    queries.append(f"{niche} {city_short}")
    queries.append(f"{niche} цена {city_short}")

    # 2. Запросы по услугам
    for service in services:
        queries.append(service)
        if city_short not in service.lower():
            queries.append(f"{service} {city_short}")

    # 3. Коммерческие запросы
    queries.append(f"{niche} стоимость")
    queries.append(f"сколько стоит {niche}")

    # 4. Запросы по типам объектов (для ремонта)
    if 'ремонт' in niche.lower():
        room_types = ['в хрущевке', 'маленькой', 'в панельном доме', 'детской', 'гостиной']
        for room_type in room_types:
            queries.append(f"{niche} {room_type}")

    # 5. Информационные запросы
    queries.append(f"бюджетный {niche}")

    # Сохраняем queries.txt
    try:
        with open('queries.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(queries))
        print(f"   ✅ Сгенерировано {len(queries)} запросов")
        print(f"   📄 Сохранено в queries.txt")
        return len(queries)
    except Exception as e:
        print(f"   ❌ Ошибка при сохранении queries.txt: {e}")
        sys.exit(1)


def run_parser():
    """Запуск парсера Яндекс Вордстат"""
    print("🚀 Запуск парсера Яндекс Вордстат...")
    print("   ⏳ Это может занять несколько минут...\n")

    try:
        # Запускаем parser.py
        result = subprocess.run(
            ['python3', 'parser.py'],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

        # Выводим результат
        if result.stdout:
            print(result.stdout)

        if result.returncode != 0:
            print(f"❌ Парсер завершился с ошибкой:")
            if result.stderr:
                print(result.stderr)
            sys.exit(1)

        print("   ✅ Парсинг завершён успешно")
        return True

    except FileNotFoundError:
        print("❌ Ошибка: файл parser.py не найден")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Ошибка при запуске парсера: {e}")
        sys.exit(1)


def run_planner():
    """Запуск планировщика контента"""
    print("🎯 Запуск AI Content Planner...")
    print("   📊 Анализ результатов и генерация плана статей...\n")

    try:
        # Запускаем planner.py
        result = subprocess.run(
            ['python3', 'planner.py'],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

        # Выводим результат
        if result.stdout:
            print(result.stdout)

        if result.returncode != 0:
            print(f"❌ Планировщик завершился с ошибкой:")
            if result.stderr:
                print(result.stderr)
            sys.exit(1)

        print("   ✅ План статей сформирован")
        return True

    except FileNotFoundError:
        print("❌ Ошибка: файл planner.py не найден")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Ошибка при запуске планировщика: {e}")
        sys.exit(1)


def display_summary(config, start_time):
    """Вывод итоговой информации"""
    elapsed = time.time() - start_time

    print_header("🎉 WORKFLOW ЗАВЕРШЁН")

    print("📂 Созданные файлы:")
    print("   • queries.txt      - поисковые запросы")
    print("   • results.md       - результаты парсинга Вордстат")
    print("   • content_plan.md  - готовый план статей\n")

    business = config['business_info']
    settings = config['content_plan_settings']

    print("📊 Итоговая информация:")
    print(f"   • Ниша: {business['niche']}")
    print(f"   • Город: {business['city']}")
    print(f"   • Целевая страница: {settings['target_page']}")
    print(f"   • Запланировано статей: {settings['articles_per_month'] * settings['planning_period_months']}")
    print(f"   • Период создания: {settings['planning_period_months']} месяцев")
    print(f"   • Ожидаемый трафик: {settings['expected_traffic_per_month']} в месяц\n")

    print(f"⏱️  Время выполнения: {elapsed:.1f} сек\n")

    print("💡 Следующие шаги:")
    print("   1. Откройте content_plan.md для просмотра плана статей")
    print("   2. Скорректируйте приоритеты и темы при необходимости")
    print("   3. Начните создание контента по календарному плану\n")


def main():
    """Главная функция workflow"""
    start_time = time.time()

    print_header("🤖 AI WORKFLOW: АВТОМАТИЗАЦИЯ SEO-ПЛАНИРОВАНИЯ")

    print(f"🕐 Запуск: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")

    # ШАГ 1: Загрузка конфигурации
    print_step(1, 4, "Загрузка и валидация конфигурации")
    config = load_config()
    print(f"✅ Конфигурация загружена: {config['business_info']['niche']}\n")

    # ШАГ 2: Генерация запросов
    print_step(2, 4, "Генерация поисковых запросов")
    queries_count = generate_queries(config)
    print()

    # ШАГ 3: Парсинг Яндекс Вордстат
    print_step(3, 4, "Парсинг Яндекс Вордстат API")
    run_parser()
    print()

    # ШАГ 4: Генерация контент-плана
    print_step(4, 4, "Генерация плана статей")
    run_planner()
    print()

    # Итоговая информация
    display_summary(config, start_time)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Workflow прерван пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        sys.exit(1)
