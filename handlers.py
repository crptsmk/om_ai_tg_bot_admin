import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import Config
from database import db
from payments import payment_service
from ai_service import ai_service
from admin_panel import admin_panel
from group_manager import GroupManager

logger = logging.getLogger(__name__)

class BotHandlers:
    def __init__(self):
        self.group_manager = None  # Инициализируется в bot.py
    
    def set_group_manager(self, group_manager: GroupManager):
        """Установить менеджер группы"""
        self.group_manager = group_manager
    
    @staticmethod
    async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        user = update.effective_user
        chat_id = update.effective_chat.id
        
        logger.info(f"Start command from user {user.id}")
        
        # Проверяем есть ли пользователь в базе
        db_user = await db.get_user(user.id)
        
        if not db_user:
            # Создаем нового пользователя
            success = await db.create_user(
                telegram_id=user.id,
                name=user.full_name or user.first_name or "Unknown",
                username=user.username or "",
                chat_id=chat_id
            )
            if success:
                logger.info(f"Created new user {user.id}")
            
            db_user = await db.get_user(user.id)
        
        # Проверяем статус подписки
        if await db.is_subscription_active(user.id):
            # Активная подписка
            message = f"""👋 Добро пожаловать обратно, {user.first_name}!

✅ Ваша подписка активна
🤖 Доступно AI-запросов сегодня: {Config.DAILY_AI_LIMIT - (db_user.get('daily_requests', 0) or 0)}

🔥 Доступные команды:
/monk [вопрос] - AI-консультант
/materials [запрос] - Поиск материалов
/status - Статус подписки"""
            
            await update.message.reply_text(message)
        else:
            # Неактивная подписка - предлагаем оплату
            message = Config.WELCOME_MESSAGE.format(
                price=Config.SUBSCRIPTION_PRICE,
                days=Config.SUBSCRIPTION_DAYS
            )
            
            keyboard = [[InlineKeyboardButton("💳 Оплатить подписку", callback_data="pay_subscription")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(message, reply_markup=reply_markup)
    
    @staticmethod
    async def monk_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /monk для AI-консультанта"""
        user_id = update.effective_user.id
        
        # Получаем вопрос из аргументов команды
        if not context.args:
            await update.message.reply_text(
                "🤖 AI-консультант Buddah Base\n\n"
                "Использование: /monk [ваш вопрос]\n\n"
                "Пример: /monk Как настроить автоматизацию в n8n?"
            )
            return
        
        question = " ".join(context.args)
        
        # Показываем что бот обрабатывает запрос
        processing_msg = await update.message.reply_text("🤖 Обрабатываю ваш вопрос...")
        
        # Обрабатываем запрос через AI сервис
        response = await ai_service.process_monk_request(user_id, question)
        
        # Удаляем сообщение о обработке и отправляем ответ
        await processing_msg.delete()
        await update.message.reply_text(response)
    
    @staticmethod
    async def materials_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /materials для поиска материалов"""
        user_id = update.effective_user.id
        
        # Проверяем активна ли подписка
        if not await db.is_subscription_active(user_id):
            keyboard = [[InlineKeyboardButton("💳 Оплатить подписку", callback_data="pay_subscription")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "❌ Для поиска материалов нужна активная подписка",
                reply_markup=reply_markup
            )
            return
        
        # Получаем поисковый запрос
        if not context.args:
            await update.message.reply_text(
                "📚 Поиск материалов Buddah Base\n\n"
                "Использование: /materials [поисковый запрос]\n\n"
                "Пример: /materials промпты для ChatGPT"
            )
            return
        
        query = " ".join(context.args)
        
        # Ищем материалы
        materials = await db.search_materials(query, limit=10)
        
        if materials:
            response = f"📚 Найдено материалов по запросу '{query}':\n\n"
            
            for i, material in enumerate(materials, 1):
                response += f"{i}. **{material['title']}**\n"
                if material.get('url'):
                    response += f"   🔗 {material['url']}\n"
                if material.get('tags'):
                    response += f"   🏷 {material['tags']}\n"
                response += "\n"
        else:
            response = f"📚 По запросу '{query}' материалы не найдены.\n\n💡 Попробуйте другие ключевые слова или задайте вопрос AI-консультанту: /monk {query}"
        
        await update.message.reply_text(response, disable_web_page_preview=True)
    
    @staticmethod
    async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /status"""
        user_id = update.effective_user.id
        user = await db.get_user(user_id)
        
        if not user:
            await update.message.reply_text("❌ Пользователь не найден в системе")
            return
        
        is_active = await db.is_subscription_active(user_id)
        
        if is_active:
            daily_requests = user.get('daily_requests', 0) or 0
            remaining_requests = Config.DAILY_AI_LIMIT - daily_requests
            subscription_end = user.get('subscription_to_date', 'Неизвестно')[:10] if user.get('subscription_to_date') else 'Неизвестно'
            
            message = f"""✅ **Статус подписки: АКТИВНА**

👤 Имя: {user.get('name', 'Не указано')}
🆔 Username: @{user.get('username', 'не указан')}
📅 Подписка до: {subscription_end}
💳 Способ оплаты: {user.get('payment_method', 'Не указан')}

🤖 **AI-консультант:**
• Использовано сегодня: {daily_requests}/{Config.DAILY_AI_LIMIT}
• Осталось запросов: {remaining_requests}

🔥 Доступные команды:
/monk [вопрос] - AI-консультант
/materials [запрос] - Поиск материалов"""
        else:
            message = f"""❌ **Статус подписки: НЕАКТИВНА**

👤 Имя: {user.get('name', 'Не указано')}
🆔 Username: @{user.get('username', 'не указан')}

Для получения доступа ко всем возможностям оформите подписку:"""
            
            keyboard = [[InlineKeyboardButton("💳 Оплатить подписку", callback_data="pay_subscription")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(message, reply_markup=reply_markup)
            return
        
        await update.message.reply_text(message)
    
    @staticmethod
    async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /admin"""
        user_id = update.effective_user.id
        
        if not admin_panel.is_admin(user_id):
            await update.message.reply_text("❌ У вас нет прав доступа к админ-панели")
            return
        
        keyboard = await admin_panel.get_admin_keyboard()
        
        await update.message.reply_text(
            "🔧 **Админ-панель Buddah Base AI**\n\nВыберите действие:",
            reply_markup=keyboard
        )
    
    @staticmethod
    async def handle_group_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик сообщений в группе (МОДЕРАЦИЯ ОТКЛЮЧЕНА)"""
        # ВРЕМЕННО ОТКЛЮЧЕНО: Автоматическое удаление сообщений
        # Функция модерации деактивирована по запросу
        
        if not update.message or update.message.chat.id != Config.CLOSED_GROUP_ID:
            return
        
        user_id = update.effective_user.id
        message_id = update.message.message_id
        thread_id = getattr(update.message, 'message_thread_id', None)
        
        # Логируем сообщения для мониторинга, но НЕ удаляем
        logger.info(f"Group message from user {user_id} in thread {thread_id}: message_id {message_id} (MODERATION DISABLED)")
        
        # Получаем менеджер группы из контекста
        group_manager = context.bot_data.get('group_manager')
        if not group_manager:
            return
        
        # МОДЕРАЦИЯ ОТКЛЮЧЕНА - сообщения не удаляются
        # Оставляем только логирование для мониторинга
        
        # Закомментированный код для модерации (можно включить позже):
        # if await group_manager.should_delete_message(user_id, thread_id):
        #     deleted = await group_manager.delete_message(Config.CLOSED_GROUP_ID, message_id)
        #     if deleted:
        #         logger.info(f"Deleted message {message_id} from user {user_id} in thread {thread_id}")
        
        return  # Выходим без удаления сообщений

# Создаем глобальный экземпляр обработчиков
handlers = BotHandlers()