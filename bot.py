#!/usr/bin/env python3
"""
Telegram бот для группы Buddah Base
Автоматически отвечает на вопросы о вступлении и привлекает новых участников
"""

import logging
import asyncio
from telegram import Update
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    filters,
    ContextTypes
)

from config import Config
from handlers import BotHandlers

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BuddahBaseBot:
    def __init__(self):
        self.application = None
        
    async def initialize(self):
        """Инициализация бота"""
        if not Config.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN не найден в переменных окружения")
        
        # Создаем приложение
        self.application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
        
        # Добавляем обработчики команд
        self.application.add_handler(CommandHandler("start", BotHandlers.start_command))
        self.application.add_handler(CommandHandler("help", BotHandlers.help_command))
        self.application.add_handler(CommandHandler("info", BotHandlers.info_command))
        
        # Обработчик новых участников
        self.application.add_handler(
            MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, BotHandlers.handle_new_member)
        )
        
        # Обработчик обычных сообщений (только в группах)
        self.application.add_handler(
            MessageHandler(
                filters.TEXT & filters.ChatType.GROUPS & ~filters.COMMAND, 
                BotHandlers.handle_message
            )
        )
        
        # Обработчик ошибок
        self.application.add_error_handler(BotHandlers.error_handler)
        
        logger.info("Бот инициализирован успешно")
    
    async def start(self):
        """Запуск бота"""
        await self.initialize()
        
        logger.info("🚀 Запускаем Buddah Base бота...")
        logger.info(f"📱 Admin contact: @{Config.ADMIN_CONTACT}")
        
        # Запускаем бота
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling(drop_pending_updates=True)
        
        logger.info("✅ Бот успешно запущен и готов к работе!")
        
        # Ожидание завершения
        await self.application.updater.idle()
    
    async def stop(self):
        """Остановка бота"""
        if self.application:
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
        logger.info("🛑 Бот остановлен")

async def main():
    """Главная функция"""
    bot = BuddahBaseBot()
    
    try:
        await bot.start()
    except KeyboardInterrupt:
        logger.info("👋 Получен сигнал остановки...")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
    finally:
        await bot.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"❌ Ошибка запуска: {e}")