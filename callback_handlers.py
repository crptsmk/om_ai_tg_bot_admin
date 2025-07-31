import logging
import io
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import Config
from database import db
from payments import payment_service
from admin_panel import admin_panel

logger = logging.getLogger(__name__)

class CallbackHandlers:
    
    @staticmethod
    async def handle_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик кнопки оплаты"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        
        # Создаем платеж
        payment_data = await payment_service.create_payment(
            telegram_id=user_id,
            amount=Config.SUBSCRIPTION_PRICE,
            description=f"Подписка Buddah Base AI на {Config.SUBSCRIPTION_DAYS} дней",
            return_url=f"https://t.me/{context.bot.username}"
        )
        
        if payment_data:
            # Сохраняем ссылку на платеж в базе
            await db.update_user_payment(user_id, payment_data['payment_url'])
            
            # Отправляем кнопку для оплаты
            keyboard = [
                [InlineKeyboardButton("💳 Перейти к оплате", url=payment_data['payment_url'])],
                [InlineKeyboardButton("✅ Я оплатил", callback_data=f"check_payment_{payment_data['payment_id']}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            message = f"""💳 **Оплата подписки**

💰 Сумма: {Config.SUBSCRIPTION_PRICE} ₽
⏱ Срок: {Config.SUBSCRIPTION_DAYS} дней

Нажмите кнопку ниже для перехода к оплате.
После оплаты нажмите "Я оплатил" для проверки статуса."""
            
            await query.edit_message_text(message, reply_markup=reply_markup)
        else:
            await query.edit_message_text("❌ Ошибка создания платежа. Попробуйте позже.")
    
    @staticmethod
    async def handle_check_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик проверки платежа"""
        query = update.callback_query
        await query.answer("🔄 Проверяем статус платежа...")
        
        user_id = query.from_user.id
        callback_data = query.data
        payment_id = callback_data.replace("check_payment_", "")
        
        # Проверяем статус платежа
        telegram_id = await payment_service.process_successful_payment(payment_id)
        
        if telegram_id and telegram_id == user_id:
            # Активируем подписку
            success = await db.activate_subscription(user_id)
            
            if success:
                # Создаем одноразовую ссылку-приглашение
                group_manager = context.bot_data.get('group_manager')
                invite_link = None
                
                if group_manager:
                    invite_link = await group_manager.create_invite_link(expire_hours=1, member_limit=1)
                    
                    if invite_link:
                        # Сохраняем ссылку в базе данных
                        await db.save_invite_link(user_id, invite_link)
                        logger.info(f"Created and saved one-time invite link for user {user_id}")
                    else:
                        logger.error(f"Failed to create invite link for user {user_id}")
                        invite_link = "❌ Ошибка создания ссылки. Обратитесь к администратору @smkbdh"
                else:
                    invite_link = "❌ Ошибка создания ссылки. Обратитесь к администратору @smkbdh"
                
                # Отправляем сообщение об успешной оплате
                success_message = Config.PAYMENT_SUCCESS_MESSAGE.format(
                    days=Config.SUBSCRIPTION_DAYS,
                    ai_limit=Config.DAILY_AI_LIMIT,
                    invite_link=invite_link
                )
                
                await query.edit_message_text(success_message, disable_web_page_preview=True)
                
                logger.info(f"User {user_id} successfully activated subscription with one-time invite link")
            else:
                await query.edit_message_text("❌ Ошибка активации подписки. Обратитесь к поддержке.")
        else:
            await query.edit_message_text(
                "⏳ Платеж еще не прошел.\n\n"
                "Если вы уже оплатили, подождите несколько минут и попробуйте снова."
            )
    
    @staticmethod
    async def handle_admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик админских кнопок"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        
        if not admin_panel.is_admin(user_id):
            await query.edit_message_text("❌ У вас нет прав доступа")
            return
        
        callback_data = query.data
        
        if callback_data == "admin_users":
            stats = await admin_panel.get_users_stats()
            active_users = stats.get('active_users', [])
            
            message = admin_panel.format_users_list(active_users, page=0)
            
            # Добавляем кнопки навигации если пользователей много
            keyboard = []
            if len(active_users) > 10:
                keyboard.append([
                    InlineKeyboardButton("◀️ Назад", callback_data="admin_users_0"),
                    InlineKeyboardButton("Вперед ▶️", callback_data="admin_users_1")
                ])
            keyboard.append([InlineKeyboardButton("🔙 Назад в админку", callback_data="admin_back")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(message, reply_markup=reply_markup)
        
        elif callback_data == "admin_stats":
            stats = await admin_panel.get_users_stats()
            message = admin_panel.format_stats_message(stats)
            
            keyboard = [[InlineKeyboardButton("🔙 Назад в админку", callback_data="admin_back")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(message, reply_markup=reply_markup)
        
        elif callback_data == "admin_broadcast":
            await query.edit_message_text(
                "📢 **Рассылка сообщений**\n\n"
                "Отправьте сообщение, которое хотите разослать всем активным пользователям.\n"
                "Для отмены напишите /cancel"
            )
            context.user_data['admin_action'] = 'broadcast'
        
        elif callback_data == "admin_add_material":
            await query.edit_message_text(
                "📚 **Добавление материала**\n\n"
                "Отправьте материал в формате:\n"
                "Название | Теги | URL\n\n"
                "Пример:\n"
                "Промпты для ChatGPT | chatgpt, промпты, ai | https://example.com\n\n"
                "Для отмены напишите /cancel"
            )
            context.user_data['admin_action'] = 'add_material'
        
        elif callback_data == "admin_export_csv":
            # Экспортируем CSV
            csv_data = await admin_panel.export_users_csv()
            
            if csv_data:
                # Отправляем файл
                csv_file = io.BytesIO(csv_data.getvalue().encode('utf-8'))
                csv_file.name = f"buddah_base_users_{context.bot_data.get('export_timestamp', 'export')}.csv"
                
                await context.bot.send_document(
                    chat_id=query.message.chat_id,
                    document=csv_file,
                    caption="📥 Экспорт активных пользователей"
                )
                
                keyboard = [[InlineKeyboardButton("🔙 Назад в админку", callback_data="admin_back")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text("✅ CSV файл отправлен", reply_markup=reply_markup)
            else:
                await query.edit_message_text("❌ Ошибка экспорта данных")
        
        elif callback_data == "admin_reset_ai":
            # Сбрасываем ежедневные лимиты AI
            success = await db.reset_daily_requests()
            
            if success:
                message = "✅ Ежедневные лимиты AI сброшены для всех пользователей"
            else:
                message = "❌ Ошибка сброса лимитов"
            
            keyboard = [[InlineKeyboardButton("🔙 Назад в админку", callback_data="admin_back")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(message, reply_markup=reply_markup)
        
        elif callback_data == "admin_back":
            # Возвращаемся в главное меню админки
            keyboard = await admin_panel.get_admin_keyboard()
            
            await query.edit_message_text(
                "🔧 **Админ-панель Buddah Base AI**\n\nВыберите действие:",
                reply_markup=keyboard
            )
    
    @staticmethod
    async def handle_admin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик сообщений в режиме админки"""
        user_id = update.effective_user.id
        
        if not admin_panel.is_admin(user_id):
            return
        
        admin_action = context.user_data.get('admin_action')
        
        if admin_action == 'broadcast':
            # Обрабатываем рассылку
            message_text = update.message.text
            
            if message_text == '/cancel':
                await update.message.reply_text("❌ Рассылка отменена")
                context.user_data.pop('admin_action', None)
                return
            
            # Подготавливаем рассылку
            broadcast_data = await admin_panel.prepare_broadcast_message(message_text)
            
            if broadcast_data:
                sent_count = 0
                failed_count = 0
                
                for chat_id in broadcast_data['user_ids']:
                    try:
                        await context.bot.send_message(chat_id, message_text)
                        sent_count += 1
                    except Exception as e:
                        failed_count += 1
                        logger.error(f"Failed to send broadcast to {chat_id}: {e}")
                
                result_message = f"📢 **Рассылка завершена**\n\n✅ Отправлено: {sent_count}\n❌ Ошибок: {failed_count}"
                await update.message.reply_text(result_message)
            else:
                await update.message.reply_text("❌ Ошибка подготовки рассылки")
            
            context.user_data.pop('admin_action', None)
        
        elif admin_action == 'add_material':
            # Обрабатываем добавление материала
            message_text = update.message.text
            
            if message_text == '/cancel':
                await update.message.reply_text("❌ Добавление материала отменено")
                context.user_data.pop('admin_action', None)
                return
            
            # Парсим данные материала
            parts = message_text.split(' | ')
            
            if len(parts) != 3:
                await update.message.reply_text(
                    "❌ Неверный формат.\n\n"
                    "Используйте: Название | Теги | URL"
                )
                return
            
            title, tags, url = parts
            
            # Добавляем материал в базу
            success = await db.add_material(
                title=title.strip(),
                tags=tags.strip(),
                url=url.strip(),
                added_by=update.effective_user.username or str(user_id)
            )
            
            if success:
                await update.message.reply_text(f"✅ Материал '{title}' добавлен в базу")
            else:
                await update.message.reply_text("❌ Ошибка добавления материала")
            
            context.user_data.pop('admin_action', None)

# Глобальный экземпляр обработчиков
callback_handlers = CallbackHandlers()