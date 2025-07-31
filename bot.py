#!/usr/bin/env python3
"""
Buddah Base AI - Коммерческий Telegram бот
Функции:
- Прием оплаты через YooKassa
- Управление доступом к закрытой группе
- AI-консультант через OpenAI
- Поиск по базе материалов
- Админ-панель
- Автоматическая модерация веток
"""

import logging
import asyncio
from datetime import datetime
from telegram import Update
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler,
    filters,
    ContextTypes
)

from config import Config
from database import db
from handlers import handlers
from callback_handlers import callback_handlers
from group_manager import GroupManager

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('buddah_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BuddahBaseBot:
    def __init__(self):
        self.application = None
        self.group_manager = None
        
    async def initialize(self):
        """Инициализация бота"""
        if not Config.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN не найден в переменных окружения")
        
        # Создаем приложение
        self.application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
        
        # Создаем менеджер группы
        self.group_manager = GroupManager(self.application.bot)
        handlers.set_group_manager(self.group_manager)
        
        # Сохраняем в bot_data для доступа из обработчиков
        self.application.bot_data['group_manager'] = self.group_manager
        self.application.bot_data['export_timestamp'] = datetime.now().strftime("%Y%m%d_%H%M")
        
        # Добавляем обработчики команд
        self.application.add_handler(CommandHandler("start", handlers.start_command))
        self.application.add_handler(CommandHandler("monk", handlers.monk_command))
        self.application.add_handler(CommandHandler("materials", handlers.materials_command))
        self.application.add_handler(CommandHandler("status", handlers.status_command))
        self.application.add_handler(CommandHandler("admin", handlers.admin_command))
        
        # Обработчики callback кнопок
        self.application.add_handler(
            CallbackQueryHandler(callback_handlers.handle_payment_callback, pattern="^pay_subscription$")
        )
        self.application.add_handler(
            CallbackQueryHandler(callback_handlers.handle_check_payment_callback, pattern="^check_payment_")
        )
        self.application.add_handler(
            CallbackQueryHandler(callback_handlers.handle_admin_callback, pattern="^admin_")
        )
        
        # Обработчик сообщений в группе (МОДЕРАЦИЯ ОТКЛЮЧЕНА)
        # ВРЕМЕННО ЗАКОММЕНТИРОВАНО: Автоматическое удаление сообщений
        # Раскомментируйте для включения модерации:
        # self.application.add_handler(
        #     MessageHandler(
        #         filters.Chat(Config.CLOSED_GROUP_ID) & ~filters.COMMAND,
        #         handlers.handle_group_message
        #     )
        # )
        
        # Обработчик админских сообщений (для рассылки и добавления материалов)
        self.application.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE,
                callback_handlers.handle_admin_message
            )
        )
        
        # Обработчик ошибок
        self.application.add_error_handler(self.error_handler)
        
        logger.info("Бот инициализирован успешно")
    
    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик ошибок"""
        logger.error(f"Exception while handling an update: {context.error}")
        
        # Отправляем уведомление админу о критичных ошибках
        if context.error and str(context.error) not in ['Message is not modified']:
            try:
                error_message = f"🚨 Ошибка в боте:\n\n{str(context.error)}"
                for admin_id in Config.ADMINS:
                    try:
                        await context.bot.send_message(admin_id, error_message)
                        break  # Отправляем только первому доступному админу
                    except:
                        continue
            except:
                pass
    
    async def start(self):
        """Запуск бота"""
        await self.initialize()
        
        logger.info("🚀 Запускаем Buddah Base AI бота...")
        logger.info(f"📱 Admin contact: @{Config.ADMIN_CONTACT}")
        logger.info(f"👥 Группа: {Config.CLOSED_GROUP_ID}")
        logger.info(f"🔧 Админы: {Config.ADMINS}")
        
        # Проверяем подключения к сервисам
        try:
            # Проверяем Supabase
            test_user = await db.get_user(0)  # Тестовый запрос
            logger.info("✅ Supabase подключена")
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к Supabase: {e}")
        
        try:
            # Проверяем группу
            group_info = await self.group_manager.get_group_info()
            logger.info(f"✅ Подключен к группе: {group_info.get('title', 'Unknown')}")
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к группе: {e}")
        
        # Запускаем бота
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling(drop_pending_updates=True)
        
        logger.info("✅ Buddah Base AI бот успешно запущен и готов к работе!")
        
        # Отправляем уведомление админам о запуске
        startup_message = f"""🚀 **Buddah Base AI бот запущен**

⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🤖 Версия: Коммерческая v1.0
✅ Все сервисы подключены"""
        
        for admin_id in Config.ADMINS:
            try:
                await self.application.bot.send_message(admin_id, startup_message)
                break
            except:
                continue
        
        # Ожидание завершения
        await asyncio.Event().wait()
    
    async def stop(self):
        """Остановка бота"""
        if self.application:
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
        logger.info("🛑 Buddah Base AI бот остановлен")

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