#!/usr/bin/env python3
"""
Быстрый тест конфигурации без подключения к внешним сервисам
"""

import logging
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_configuration():
    """Тестирование конфигурации"""
    print("🔧 Тестирование конфигурации Buddah Base AI...")
    print("=" * 50)
    
    tests_passed = 0
    tests_total = 0
    
    # Telegram Bot
    tests_total += 1
    if Config.TELEGRAM_BOT_TOKEN:
        print(f"✅ Telegram Bot Token: {Config.TELEGRAM_BOT_TOKEN[:10]}...")
        tests_passed += 1
    else:
        print("❌ Telegram Bot Token: Не найден")
    
    # Supabase
    tests_total += 1
    if Config.SUPABASE_URL and Config.SUPABASE_SERVICE_KEY:
        print(f"✅ Supabase: {Config.SUPABASE_URL}")
        tests_passed += 1
    else:
        print("❌ Supabase: Конфигурация неполная")
    
    # OpenAI
    tests_total += 1
    if Config.OPENAI_API_KEY:
        print(f"✅ OpenAI API Key: {Config.OPENAI_API_KEY[:10]}...")
        tests_passed += 1
    else:
        print("❌ OpenAI API Key: Не найден")
    
    # YooKassa
    tests_total += 1
    if Config.YOOKASSA_SECRET_KEY and Config.YOOKASSA_SHOP_ID:
        print(f"✅ YooKassa: Shop ID {Config.YOOKASSA_SHOP_ID}")
        tests_passed += 1
    else:
        print("❌ YooKassa: Конфигурация неполная")
    
    # Группа
    tests_total += 1
    if Config.CLOSED_GROUP_ID:
        print(f"✅ Группа: {Config.CLOSED_GROUP_ID}")
        tests_passed += 1
    else:
        print("❌ Группа: ID не указан")
    
    # Админы
    tests_total += 1
    if Config.ADMINS and len(Config.ADMINS) > 0:
        print(f"✅ Админы: {len(Config.ADMINS)} человек - {Config.ADMINS}")
        tests_passed += 1
    else:
        print("❌ Админы: Список пуст")
    
    # Настройки подписки
    tests_total += 1
    if Config.SUBSCRIPTION_PRICE > 0 and Config.SUBSCRIPTION_DAYS > 0:
        print(f"✅ Подписка: {Config.SUBSCRIPTION_PRICE} ₽ на {Config.SUBSCRIPTION_DAYS} дней")
        tests_passed += 1
    else:
        print("❌ Подписка: Неверные настройки цены/срока")
    
    # Лимиты AI
    tests_total += 1
    if Config.DAILY_AI_LIMIT > 0:
        print(f"✅ AI лимит: {Config.DAILY_AI_LIMIT} запросов в день")
        tests_passed += 1
    else:
        print("❌ AI лимит: Неверное значение")
    
    print("\n" + "="*50)
    print(f"📊 РЕЗУЛЬТАТ: {tests_passed}/{tests_total} тестов пройдено")
    
    success_rate = (tests_passed / tests_total) * 100
    print(f"🎯 Успешность: {success_rate:.1f}%")
    
    if success_rate == 100:
        print("🎉 ВСЕ НАСТРОЙКИ КОРРЕКТНЫ!")
        print("✅ Бот готов к запуску")
    elif success_rate >= 75:
        print("⚠️ Большинство настроек корректны")
        print("🔧 Есть несколько проблем для исправления")
    else:
        print("❌ КРИТИЧНЫЕ ПРОБЛЕМЫ КОНФИГУРАЦИИ")
        print("🛠 Необходимо исправить настройки")
    
    return success_rate >= 75

def main():
    """Главная функция"""
    print("🚀 Быстрая проверка готовности Buddah Base AI")
    print("Это базовая проверка конфигурации без подключения к внешним сервисам\n")
    
    is_ready = test_configuration()
    
    if is_ready:
        print(f"\n🎯 СЛЕДУЮЩИЕ ШАГИ:")
        print(f"1. Запустить бота: python bot.py")
        print(f"2. Запустить webhook сервер: python webhook_server.py")
        print(f"3. Или запустить все сервисы: python run_services.py")
        print(f"\n💡 КОМАНДЫ БОТА:")
        print(f"   /start - Регистрация и статус")
        print(f"   /monk [вопрос] - AI-консультант")  
        print(f"   /materials [запрос] - Поиск материалов")
        print(f"   /admin - Админ-панель")
        print(f"\n🔗 ССЫЛКИ:")
        print(f"   Группа: https://t.me/c/{abs(Config.CLOSED_GROUP_ID)}")
        print(f"   Админ: @{Config.ADMIN_CONTACT}")
    
    return 0 if is_ready else 1

if __name__ == "__main__":
    exit(main())