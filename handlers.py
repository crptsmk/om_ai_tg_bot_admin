import logging
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ContextTypes
from config import Config
from messages import BotMessages

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class BotHandlers:
    
    @staticmethod
    async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        message = BotMessages.format_message(
            BotMessages.START_MESSAGE, 
            Config.ADMIN_CONTACT
        )
        await update.message.reply_text(message, parse_mode='Markdown')
        logger.info(f"Start command from user {update.effective_user.id}")

    @staticmethod
    async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        message = BotMessages.format_message(
            BotMessages.GROUP_INFO_MESSAGE, 
            Config.ADMIN_CONTACT
        )
        await update.message.reply_text(message, parse_mode='Markdown')
        logger.info(f"Help command from user {update.effective_user.id}")

    @staticmethod
    async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /info - полная информация"""
        message = BotMessages.format_message(
            BotMessages.MAIN_INFO_MESSAGE, 
            Config.ADMIN_CONTACT
        )
        await update.message.reply_text(message, parse_mode='Markdown')
        logger.info(f"Info command from user {update.effective_user.id}")

    @staticmethod
    async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик обычных сообщений"""
        if not update.message or not update.message.text:
            return

        message_text = update.message.text.lower()
        user_id = update.effective_user.id
        chat_type = update.message.chat.type
        
        logger.info(f"Message from user {user_id} in {chat_type}: {message_text[:50]}...")

        # В группах отвечаем только если:
        # 1. Сообщение содержит упоминание бота
        # 2. Сообщение является ответом на сообщение бота
        # 3. Сообщение содержит ключевые слова
        is_group = chat_type in ['group', 'supergroup']
        bot_mentioned = '@saint_buddah_bot' in message_text or 'saint_buddah' in message_text
        is_reply_to_bot = (update.message.reply_to_message and 
                          update.message.reply_to_message.from_user and
                          update.message.reply_to_message.from_user.is_bot)
        
        # Проверяем ключевые слова
        has_join_keywords = any(keyword in message_text for keyword in Config.JOIN_KEYWORDS)
        has_files_keywords = any(keyword in message_text for keyword in Config.FILES_KEYWORDS)
        has_engagement_keywords = any(keyword in message_text for keyword in Config.ENGAGEMENT_KEYWORDS)
        
        # В приватном чате отвечаем всегда, в группе - только при определенных условиях
        should_respond = (not is_group) or bot_mentioned or is_reply_to_bot or has_join_keywords or has_files_keywords or has_engagement_keywords
        
        if not should_respond:
            logger.info(f"Ignoring message in group without trigger")
            return

        # Приоритет ответов: файлы > вступление > взаимодействие > упоминания
        
        # Проверяем запросы файлов (высший приоритет)
        if has_files_keywords:
            response = BotMessages.format_message(
                BotMessages.FILES_REQUEST_MESSAGE, 
                Config.ADMIN_CONTACT
            )
            await update.message.reply_text(response, parse_mode='Markdown')
            logger.info(f"Sent files request message to user {user_id}")
            
        # Проверяем запросы о вступлении
        elif has_join_keywords:
            response = BotMessages.format_message(
                BotMessages.MAIN_INFO_MESSAGE, 
                Config.ADMIN_CONTACT
            )
            await update.message.reply_text(response, parse_mode='Markdown')
            logger.info(f"Sent join info to user {user_id}")
            
        # Проверяем ключевые слова для общего взаимодействия
        elif has_engagement_keywords:
            response = BotMessages.format_message(
                BotMessages.ENGAGEMENT_MESSAGE, 
                Config.ADMIN_CONTACT
            )
            await update.message.reply_text(response, parse_mode='Markdown')
            logger.info(f"Sent engagement message to user {user_id}")
        
        # Если упоминули бота, но нет ключевых слов - отправляем стартовое сообщение
        elif bot_mentioned or is_reply_to_bot:
            response = BotMessages.format_message(
                BotMessages.START_MESSAGE, 
                Config.ADMIN_CONTACT
            )
            await update.message.reply_text(response, parse_mode='Markdown')
            logger.info(f"Sent start message to user {user_id} (bot mentioned)")
        
        # В приватном чате, если нет ключевых слов - отправляем стартовое сообщение
        elif not is_group:
            response = BotMessages.format_message(
                BotMessages.START_MESSAGE, 
                Config.ADMIN_CONTACT
            )
            await update.message.reply_text(response, parse_mode='Markdown')
            logger.info(f"Sent start message to user {user_id} (private chat fallback)")

    @staticmethod
    async def handle_inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик inline-запросов"""
        query = update.inline_query.query.lower() if update.inline_query.query else ""
        
        results = []
        
        # Определяем, какой контент показать
        if "файл" in query or "дайте" in query or "скинь" in query or "промпт" in query:
            # Показываем сообщение о файлах
            results.append(
                InlineQueryResultArticle(
                    id="files_request",
                    title="📁 Хочешь файлы и промпты?",
                    description="2000+ промптов, шаблоны, AI-инструменты",
                    input_message_content=InputTextMessageContent(
                        message_text=BotMessages.format_message(
                            BotMessages.FILES_REQUEST_MESSAGE, 
                            Config.ADMIN_CONTACT
                        ),
                        parse_mode='Markdown'
                    )
                )
            )
        
        if not query or "вступить" in query or "доступ" in query:
            # Показываем информацию о вступлении
            results.append(
                InlineQueryResultArticle(
                    id="join_info",
                    title="💎 Как вступить в Buddah Base",
                    description="Полная информация о VEO 3 и подписке за 999₽",
                    input_message_content=InputTextMessageContent(
                        message_text=BotMessages.format_message(
                            BotMessages.MAIN_INFO_MESSAGE, 
                            Config.ADMIN_CONTACT
                        ),
                        parse_mode='Markdown'
                    )
                )
            )
        
        if not query or "интересн" in query or "круто" in query or "veo" in query:
            # Показываем призыв к действию
            results.append(
                InlineQueryResultArticle(
                    id="engagement",
                    title="🔥 Заинтересовался?",
                    description="Получи доступ к VEO 3 и AI-инструментам",
                    input_message_content=InputTextMessageContent(
                        message_text=BotMessages.format_message(
                            BotMessages.ENGAGEMENT_MESSAGE, 
                            Config.ADMIN_CONTACT
                        ),
                        parse_mode='Markdown'
                    )
                )
            )
        
        # Всегда показываем информацию о группе
        results.append(
            InlineQueryResultArticle(
                id="group_info",
                title="📌 О группе Buddah Base",
                description="Структура группы и что внутри",
                input_message_content=InputTextMessageContent(
                    message_text=BotMessages.format_message(
                        BotMessages.GROUP_INFO_MESSAGE, 
                        Config.ADMIN_CONTACT
                    ),
                    parse_mode='Markdown'
                )
            )
        )
        
        await update.inline_query.answer(results, cache_time=300)
        logger.info(f"Answered inline query: '{query}' with {len(results)} results")

    @staticmethod
    async def handle_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик новых участников группы"""
        for member in update.message.new_chat_members:
            welcome_message = BotMessages.format_message(
                BotMessages.GROUP_INFO_MESSAGE, 
                Config.ADMIN_CONTACT
            )
            await update.message.reply_text(
                f"👋 Добро пожаловать, {member.first_name}!\n\n{welcome_message}", 
                parse_mode='Markdown'
            )
            logger.info(f"Welcomed new member: {member.first_name} (ID: {member.id})")

    @staticmethod
    async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик ошибок"""
        logger.error(f"Exception while handling an update: {context.error}")