import logging
from datetime import datetime, timedelta
from typing import Optional
from telegram import Bot, ChatInviteLink
from telegram.error import TelegramError
from config import Config

logger = logging.getLogger(__name__)

class GroupManager:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.group_id = Config.CLOSED_GROUP_ID
        self.main_topic_id = Config.MAIN_TOPIC_ID
        self.admins = Config.ADMINS
    
    async def create_invite_link(self, expire_hours=1, member_limit=1) -> Optional[str]:
        """Создать одноразовую ссылку-приглашение в группу"""
        try:
            # Устанавливаем время истечения через час
            expire_date = datetime.now() + timedelta(hours=expire_hours)
            
            invite_link = await self.bot.create_chat_invite_link(
                chat_id=self.group_id,
                expire_date=expire_date,
                member_limit=member_limit,
                creates_join_request=False,
                name=f"Подписка {datetime.now().strftime('%d.%m %H:%M')}"
            )
            
            logger.info(f"Created one-time invite link: {invite_link.invite_link} (expires: {expire_date}, limit: {member_limit})")
            return invite_link.invite_link
            
        except TelegramError as e:
            logger.error(f"Error creating invite link: {e}")
            return None
    
    async def is_user_in_group(self, user_id: int) -> bool:
        """Проверить находится ли пользователь в группе"""
        try:
            member = await self.bot.get_chat_member(self.group_id, user_id)
            return member.status in ['member', 'administrator', 'creator']
        except TelegramError:
            return False
    
    async def kick_user_from_group(self, user_id: int) -> bool:
        """Исключить пользователя из группы"""
        try:
            await self.bot.ban_chat_member(self.group_id, user_id)
            await self.bot.unban_chat_member(self.group_id, user_id)
            logger.info(f"Kicked user {user_id} from group")
            return True
        except TelegramError as e:
            logger.error(f"Error kicking user {user_id}: {e}")
            return False
    
    async def should_delete_message(self, user_id: int, message_thread_id: Optional[int]) -> bool:
        """Определить нужно ли удалить сообщение"""
        # Не удаляем сообщения админов
        if user_id in self.admins:
            logger.info(f"Not deleting message from admin {user_id}")
            return False
        
        # Не удаляем сообщения в главной теме (ID=1 или None)
        if message_thread_id is None or message_thread_id == self.main_topic_id:
            logger.info(f"Not deleting message from main topic (thread_id: {message_thread_id})")
            return False
        
        # Удаляем сообщения не-админов во всех остальных темах
        logger.info(f"Should delete message from user {user_id} in thread {message_thread_id}")
        return True
    
    async def delete_message(self, chat_id: int, message_id: int) -> bool:
        """Удалить сообщение"""
        try:
            await self.bot.delete_message(chat_id, message_id)
            return True
        except TelegramError as e:
            logger.error(f"Error deleting message {message_id}: {e}")
            return False
    
    async def get_group_info(self) -> dict:
        """Получить информацию о группе"""
        try:
            chat = await self.bot.get_chat(self.group_id)
            member_count = await self.bot.get_chat_member_count(self.group_id)
            
            return {
                'title': chat.title,
                'member_count': member_count,
                'description': chat.description
            }
        except TelegramError as e:
            logger.error(f"Error getting group info: {e}")
            return {}