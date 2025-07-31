import logging
import requests
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from config import Config

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.base_url = Config.SUPABASE_URL
        self.api_key = Config.SUPABASE_SERVICE_KEY
        self.headers = {
            'apikey': self.api_key,
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        }
    
    async def get_user(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """Получить пользователя по Telegram ID"""
        try:
            url = f"{self.base_url}/rest/v1/buddah_base_ai?id=eq.{telegram_id}"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                return data[0] if data else None
            else:
                logger.error(f"Error getting user {telegram_id}: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error getting user {telegram_id}: {e}")
            return None
    
    async def create_user(self, telegram_id: int, name: str, username: str, chat_id: int) -> bool:
        """Создать нового пользователя"""
        try:
            url = f"{self.base_url}/rest/v1/buddah_base_ai"
            user_data = {
                'id': telegram_id,
                'name': name,
                'username': username,
                'status': 'inactive',
                'chatid': chat_id,
                'created_at': datetime.utcnow().isoformat(),
                'payed': 'false',
                'subscription_to_date': None,
                'payment_method': None,
                'payment_link': None,
                'daily_requests': 0
            }
            
            response = requests.post(url, json=user_data, headers=self.headers)
            return response.status_code in [200, 201]
        except Exception as e:
            logger.error(f"Error creating user {telegram_id}: {e}")
            return False
    
    async def update_user_payment(self, telegram_id: int, payment_link: str, payment_method: str = 'YooKassa') -> bool:
        """Обновить данные о платеже"""
        try:
            url = f"{self.base_url}/rest/v1/buddah_base_ai?id=eq.{telegram_id}"
            update_data = {
                'payment_link': payment_link,
                'payment_method': payment_method
            }
            
            response = requests.patch(url, json=update_data, headers=self.headers)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error updating payment for user {telegram_id}: {e}")
            return False
    
    async def activate_subscription(self, telegram_id: int, payment_method: str = 'YooKassa') -> bool:
        """Активировать подписку после успешной оплаты"""
        try:
            subscription_end = datetime.utcnow() + timedelta(days=Config.SUBSCRIPTION_DAYS)
            
            url = f"{self.base_url}/rest/v1/buddah_base_ai?id=eq.{telegram_id}"
            update_data = {
                'status': 'active',
                'payed': 'true',
                'subscription_to_date': subscription_end.isoformat(),
                'payment_method': payment_method,
                'daily_requests': 0
            }
            
            response = requests.patch(url, json=update_data, headers=self.headers)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error activating subscription for user {telegram_id}: {e}")
            return False
    
    async def is_subscription_active(self, telegram_id: int) -> bool:
        """Проверить активна ли подписка"""
        try:
            user = await self.get_user(telegram_id)
            if not user or user['status'] != 'active':
                return False
            
            if not user['subscription_to_date']:
                return False
            
            subscription_end = datetime.fromisoformat(user['subscription_to_date'].replace('Z', ''))
            return datetime.utcnow() < subscription_end
        except Exception as e:
            logger.error(f"Error checking subscription for user {telegram_id}: {e}")
            return False
    
    async def increment_daily_requests(self, telegram_id: int) -> bool:
        """Увеличить счетчик ежедневных запросов"""
        try:
            user = await self.get_user(telegram_id)
            if not user:
                return False
            
            new_count = (user.get('daily_requests', 0) or 0) + 1
            
            url = f"{self.base_url}/rest/v1/buddah_base_ai?id=eq.{telegram_id}"
            update_data = {'daily_requests': new_count}
            
            response = requests.patch(url, json=update_data, headers=self.headers)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error incrementing requests for user {telegram_id}: {e}")
            return False
    
    async def can_make_ai_request(self, telegram_id: int) -> bool:
        """Проверить можно ли сделать AI запрос"""
        try:
            user = await self.get_user(telegram_id)
            if not user:
                return False
            
            return (user.get('daily_requests', 0) or 0) < Config.DAILY_AI_LIMIT
        except Exception as e:
            logger.error(f"Error checking AI requests for user {telegram_id}: {e}")
            return False
    
    async def reset_daily_requests(self) -> bool:
        """Сбросить ежедневные запросы для всех пользователей"""
        try:
            url = f"{self.base_url}/rest/v1/buddah_base_ai"
            update_data = {'daily_requests': 0}
            
            response = requests.patch(url, json=update_data, headers=self.headers)
            logger.info(f"Reset daily requests for all users")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error resetting daily requests: {e}")
            return False
    
    async def search_materials(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Поиск материалов по запросу"""
        try:
            # Поиск в title и tags с использованием ilike
            url = f"{self.base_url}/rest/v1/materials?or=(title.ilike.*{query}*,tags.ilike.*{query}*)&limit={limit}"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error searching materials: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error searching materials: {e}")
            return []
    
    async def add_material(self, title: str, tags: str, url: str, added_by: str) -> bool:
        """Добавить материал"""
        try:
            api_url = f"{self.base_url}/rest/v1/materials"
            material_data = {
                'title': title,
                'tags': tags,
                'url': url,
                'added_by': added_by
            }
            
            response = requests.post(api_url, json=material_data, headers=self.headers)
            return response.status_code in [200, 201]
        except Exception as e:
            logger.error(f"Error adding material: {e}")
            return False
    
    async def get_active_users(self) -> List[Dict[str, Any]]:
        """Получить список активных пользователей"""
        try:
            url = f"{self.base_url}/rest/v1/buddah_base_ai?status=eq.active"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error getting active users: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error getting active users: {e}")
            return []
    
    async def save_invite_link(self, telegram_id: int, invite_link: str) -> bool:
        """Сохранить invite_link для пользователя"""
        try:
            url = f"{self.base_url}/rest/v1/buddah_base_ai?id=eq.{telegram_id}"
            update_data = {
                'payment_link': invite_link  # Сохраняем invite_link в поле payment_link
            }
            
            response = requests.patch(url, json=update_data, headers=self.headers)
            if response.status_code == 200:
                logger.info(f"Saved invite link for user {telegram_id}")
                return True
            else:
                logger.error(f"Error saving invite link for user {telegram_id}: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Error saving invite link for user {telegram_id}: {e}")
            return False

    async def get_promo_code(self, promo_code: str) -> Optional[Dict[str, Any]]:
        """Получить информацию о промокоде"""
        try:
            url = f"{self.base_url}/rest/v1/promo_codes?promo_code=eq.{promo_code}"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                return data[0] if data else None
            else:
                return None
        except Exception as e:
            logger.error(f"Error getting promo code {promo_code}: {e}")
            return None

# Глобальный экземпляр базы данных
db = Database()