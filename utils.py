import logging
import schedule
import time
import asyncio
from datetime import datetime
from database import db
from config import Config

logger = logging.getLogger(__name__)

class DailyCronJob:
    """Ежедневные задачи"""
    
    @staticmethod
    async def reset_daily_ai_limits():
        """Сброс ежедневных лимитов AI запросов"""
        try:
            success = await db.reset_daily_requests()
            if success:
                logger.info("✅ Daily AI limits reset successfully")
            else:
                logger.error("❌ Failed to reset daily AI limits")
        except Exception as e:
            logger.error(f"Error resetting daily AI limits: {e}")
    
    @staticmethod
    async def cleanup_expired_subscriptions():
        """Деактивация истекших подписок"""
        try:
            # Получаем всех активных пользователей
            active_users = await db.get_active_users()
            
            deactivated_count = 0
            for user in active_users:
                # Проверяем активна ли подписка
                is_active = await db.is_subscription_active(user['id'])
                
                if not is_active:
                    # Деактивируем пользователя
                    success = await db.supabase.table('buddah_base_ai').update({
                        'status': 'inactive'
                    }).eq('id', user['id']).execute()
                    
                    if success.data:
                        deactivated_count += 1
                        logger.info(f"Deactivated expired subscription for user {user['id']}")
            
            logger.info(f"✅ Processed expired subscriptions: {deactivated_count} users deactivated")
            
        except Exception as e:
            logger.error(f"Error cleaning up expired subscriptions: {e}")

def schedule_daily_tasks():
    """Настройка расписания ежедневных задач"""
    # Сброс лимитов AI в 00:00 MSK
    schedule.every().day.at("00:00").do(
        lambda: asyncio.run(DailyCronJob.reset_daily_ai_limits())
    )
    
    # Проверка истекших подписок в 01:00 MSK
    schedule.every().day.at("01:00").do(
        lambda: asyncio.run(DailyCronJob.cleanup_expired_subscriptions())
    )
    
    logger.info("✅ Daily tasks scheduled")

def run_scheduler():
    """Запуск планировщика задач"""
    logger.info("🕐 Starting task scheduler...")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Проверяем каждую минуту

class BotUtils:
    """Утилиты для бота"""
    
    @staticmethod
    def format_subscription_end_date(iso_date_string: str) -> str:
        """Форматирование даты окончания подписки"""
        try:
            if not iso_date_string:
                return "Не указана"
            
            # Парсим ISO дату
            date_obj = datetime.fromisoformat(iso_date_string.replace('Z', '+00:00'))
            
            # Форматируем в читаемый вид
            return date_obj.strftime("%d.%m.%Y %H:%M")
        except Exception as e:
            logger.error(f"Error formatting date {iso_date_string}: {e}")
            return "Ошибка даты"
    
    @staticmethod
    def validate_material_data(title: str, tags: str, url: str) -> tuple:
        """Валидация данных материала"""
        errors = []
        
        if not title or len(title.strip()) < 3:
            errors.append("Название должно содержать минимум 3 символа")
        
        if not tags or len(tags.strip()) < 2:
            errors.append("Теги должны содержать минимум 2 символа")
        
        if not url or not (url.startswith('http://') or url.startswith('https://')):
            errors.append("URL должен начинаться с http:// или https://")
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 100) -> str:
        """Обрезание текста с добавлением многоточия"""
        if len(text) <= max_length:
            return text
        
        return text[:max_length-3] + "..."
    
    @staticmethod
    def format_user_stats(user_data: dict) -> str:
        """Форматирование статистики пользователя"""
        name = user_data.get('name', 'Без имени')
        username = user_data.get('username', 'без username')
        daily_requests = user_data.get('daily_requests', 0) or 0
        subscription_end = user_data.get('subscription_to_date')
        
        stats = f"👤 **{name}** (@{username})\n"
        stats += f"🤖 AI запросов: {daily_requests}/{Config.DAILY_AI_LIMIT}\n"
        
        if subscription_end:
            formatted_date = BotUtils.format_subscription_end_date(subscription_end)
            stats += f"⏰ Подписка до: {formatted_date}\n"
        
        return stats

# Экземпляр утилит
bot_utils = BotUtils()