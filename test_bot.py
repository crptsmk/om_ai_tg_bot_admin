#!/usr/bin/env python3
"""
Тестирование бота - проверка основных функций
"""

import asyncio
import logging
from config import Config
from messages import BotMessages

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_bot_setup():
    """Тестирование настроек бота"""
    logger.info("🧪 Тестирование настроек бота...")
    
    # Проверка токена
    if Config.TELEGRAM_BOT_TOKEN:
        logger.info("✅ Токен бота найден")
        logger.info(f"🔑 Токен начинается с: {Config.TELEGRAM_BOT_TOKEN[:10]}...")
    else:
        logger.error("❌ Токен бота не найден!")
        return False
    
    # Проверка контакта администратора
    if Config.ADMIN_CONTACT:
        logger.info(f"👨‍💼 Контакт администратора: @{Config.ADMIN_CONTACT}")
    else:
        logger.error("❌ Контакт администратора не найден!")
        return False
    
    # Проверка ключевых слов
    logger.info(f"🔍 Ключевые слова для вступления: {len(Config.JOIN_KEYWORDS)} шт.")
    logger.info(f"🎯 Ключевые слова для взаимодействия: {len(Config.ENGAGEMENT_KEYWORDS)} шт.")
    
    return True

def test_messages():
    """Тестирование сообщений"""
    logger.info("📝 Тестирование сообщений...")
    
    # Тест форматирования основного сообщения
    main_msg = BotMessages.format_message(BotMessages.MAIN_INFO_MESSAGE, "testuser")
    if "testuser" in main_msg:
        logger.info("✅ Форматирование основного сообщения работает")
    else:
        logger.error("❌ Ошибка форматирования основного сообщения")
        return False
    
    # Тест сообщения взаимодействия
    engagement_msg = BotMessages.format_message(BotMessages.ENGAGEMENT_MESSAGE, "testuser")
    if "testuser" in engagement_msg:
        logger.info("✅ Форматирование сообщения взаимодействия работает")
    else:
        logger.error("❌ Ошибка форматирования сообщения взаимодействия")
        return False
    
    logger.info("📏 Длина основного сообщения: {} символов".format(len(main_msg)))
    logger.info("📏 Длина сообщения взаимодействия: {} символов".format(len(engagement_msg)))
    
    return True

def test_keywords():
    """Тестирование ключевых слов"""
    logger.info("🔍 Тестирование ключевых слов...")
    
    test_messages = [
        "Как вступить в группу?",
        "Хочу получить доступ",
        "Сколько стоит подписка?",
        "Интересно, расскажи подробнее",
        "Как это работает?",
        "VEO 3 круто!"
    ]
    
    for msg in test_messages:
        msg_lower = msg.lower()
        
        # Проверка ключевых слов вступления
        join_match = any(keyword in msg_lower for keyword in Config.JOIN_KEYWORDS)
        engagement_match = any(keyword in msg_lower for keyword in Config.ENGAGEMENT_KEYWORDS)
        
        if join_match:
            logger.info(f"✅ '{msg}' → JOIN сообщение")
        elif engagement_match:
            logger.info(f"✅ '{msg}' → ENGAGEMENT сообщение")
        else:
            logger.info(f"ℹ️ '{msg}' → Нет реакции")
    
    return True

async def main():
    """Главная функция тестирования"""
    logger.info("🚀 Запуск тестирования Buddah Base бота")
    
    # Тестирование настроек
    if not await test_bot_setup():
        logger.error("💥 Тестирование настроек провалено!")
        return
    
    # Тестирование сообщений
    if not test_messages():
        logger.error("💥 Тестирование сообщений провалено!")
        return
    
    # Тестирование ключевых слов
    if not test_keywords():
        logger.error("💥 Тестирование ключевых слов провалено!")
        return
    
    logger.info("🎉 Все тесты пройдены успешно!")
    logger.info("🚀 Бот готов к запуску!")

if __name__ == "__main__":
    asyncio.run(main())