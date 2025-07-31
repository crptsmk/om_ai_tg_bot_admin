import logging
import io
import csv
from typing import List, Dict, Any
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database import db
from config import Config

logger = logging.getLogger(__name__)

class AdminPanel:
    def __init__(self):
        self.admins = Config.ADMINS
    
    def is_admin(self, user_id: int) -> bool:
        """Проверить является ли пользователь админом"""
        return user_id in self.admins
    
    async def get_admin_keyboard(self) -> InlineKeyboardMarkup:
        """Клавиатура админ-панели"""
        keyboard = [
            [InlineKeyboardButton("👥 Активные пользователи", callback_data="admin_users")],
            [InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")],
            [InlineKeyboardButton("📢 Рассылка", callback_data="admin_broadcast")],
            [InlineKeyboardButton("📚 Добавить материал", callback_data="admin_add_material")],
            [InlineKeyboardButton("📥 Выгрузить CSV", callback_data="admin_export_csv")],
            [InlineKeyboardButton("🔄 Сбросить лимиты AI", callback_data="admin_reset_ai")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    async def get_users_stats(self) -> Dict[str, Any]:
        """Получить статистику пользователей"""
        try:
            active_users = await db.get_active_users()
            
            # Подсчитываем статистику
            total_active = len(active_users)
            total_requests_today = sum(user.get('daily_requests', 0) or 0 for user in active_users)
            
            # Группируем по методам оплаты
            payment_methods = {}
            for user in active_users:
                method = user.get('payment_method', 'Unknown')
                payment_methods[method] = payment_methods.get(method, 0) + 1
            
            return {
                'total_active': total_active,
                'total_requests_today': total_requests_today,
                'payment_methods': payment_methods,
                'active_users': active_users
            }
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return {}
    
    async def export_users_csv(self) -> io.StringIO:
        """Экспортировать пользователей в CSV"""
        try:
            active_users = await db.get_active_users()
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Заголовки
            writer.writerow([
                'ID', 'Name', 'Username', 'Status', 'Created At', 
                'Subscription To', 'Payment Method', 'Daily Requests'
            ])
            
            # Данные пользователей
            for user in active_users:
                writer.writerow([
                    user.get('id', ''),
                    user.get('name', ''),
                    user.get('username', ''),
                    user.get('status', ''),
                    user.get('created_at', ''),
                    user.get('subscription_to_date', ''),
                    user.get('payment_method', ''),
                    user.get('daily_requests', 0)
                ])
            
            output.seek(0)
            return output
            
        except Exception as e:
            logger.error(f"Error exporting CSV: {e}")
            return None
    
    async def prepare_broadcast_message(self, message_text: str) -> Dict[str, Any]:
        """Подготовить сообщение для рассылки"""
        try:
            active_users = await db.get_active_users()
            user_ids = [user['chatid'] for user in active_users if user.get('chatid')]
            
            return {
                'message_text': message_text,
                'recipient_count': len(user_ids),
                'user_ids': user_ids
            }
        except Exception as e:
            logger.error(f"Error preparing broadcast: {e}")
            return {}
    
    def format_stats_message(self, stats: Dict[str, Any]) -> str:
        """Форматировать сообщение со статистикой"""
        if not stats:
            return "❌ Ошибка получения статистики"
        
        message = f"""📊 **Статистика Buddah Base AI**

👥 **Пользователи:**
• Активных подписчиков: {stats.get('total_active', 0)}
• AI-запросов сегодня: {stats.get('total_requests_today', 0)}

💳 **Методы оплаты:**"""
        
        for method, count in stats.get('payment_methods', {}).items():
            message += f"\n• {method}: {count}"
        
        return message
    
    def format_users_list(self, users: List[Dict[str, Any]], page: int = 0, per_page: int = 10) -> str:
        """Форматировать список пользователей"""
        if not users:
            return "👥 Активных пользователей не найдено"
        
        start = page * per_page
        end = start + per_page
        page_users = users[start:end]
        
        message = f"👥 **Активные пользователи** (стр. {page + 1}):\n\n"
        
        for i, user in enumerate(page_users, start=start+1):
            name = user.get('name', 'Без имени')
            username = user.get('username', 'без username')
            requests = user.get('daily_requests', 0) or 0
            subscription = user.get('subscription_to_date', 'Нет данных')[:10] if user.get('subscription_to_date') else 'Нет данных'
            
            message += f"{i}. **{name}** (@{username})\n"
            message += f"   • Запросов сегодня: {requests}/{Config.DAILY_AI_LIMIT}\n"
            message += f"   • Подписка до: {subscription}\n\n"
        
        total_pages = (len(users) + per_page - 1) // per_page
        message += f"📄 Страница {page + 1} из {total_pages}"
        
        return message

# Глобальный экземпляр админ-панели
admin_panel = AdminPanel()