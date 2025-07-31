import logging
import openai
from typing import Optional, List, Dict, Any
from config import Config
from database import db

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        openai.api_key = Config.OPENAI_API_KEY
        self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
    
    async def search_in_materials(self, query: str) -> List[Dict[str, Any]]:
        """Поиск в базе материалов"""
        try:
            materials = await db.search_materials(query, limit=5)
            return materials
        except Exception as e:
            logger.error(f"Error searching materials: {e}")
            return []
    
    async def generate_ai_response(self, question: str, materials: List[Dict[str, Any]] = None) -> Optional[str]:
        """Генерация ответа через OpenAI"""
        try:
            # Формируем контекст из найденных материалов
            context = ""
            if materials:
                context = "\n\nНайденные материалы:\n"
                for material in materials[:3]:  # Берем только первые 3
                    context += f"- {material['title']}: {material.get('url', 'Нет ссылки')}\n"
            
            system_prompt = """Ты AI-консультант сообщества Buddah Base - экспертов по нейросетям и автоматизации.

Отвечай кратко и по делу. Если есть материалы в контексте - обязательно на них ссылайся.
Если нет подходящих материалов - дай общий совет по теме AI/нейросетей/автоматизации.

Стиль: дружелюбный, экспертный, с эмодзи."""

            user_prompt = f"Вопрос: {question}{context}"
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return None
    
    async def process_monk_request(self, telegram_id: int, question: str) -> Optional[str]:
        """Обработка запроса /monk с проверками лимитов"""
        try:
            # Проверяем активна ли подписка
            if not await db.is_subscription_active(telegram_id):
                return "❌ Для использования AI-консультанта нужна активная подписка"
            
            # Проверяем лимит запросов
            if not await db.can_make_ai_request(telegram_id):
                return f"🤖 Лимит AI-вопросов исчерпан\n\nВы использовали все {Config.DAILY_AI_LIMIT} вопросов на сегодня.\nЛимит обновится завтра в 00:00 МСК."
            
            # Ищем в материалах
            materials = await self.search_in_materials(question)
            
            # Генерируем ответ
            ai_response = await self.generate_ai_response(question, materials)
            
            if ai_response:
                # Увеличиваем счетчик запросов
                await db.increment_daily_requests(telegram_id)
                
                # Формируем итоговый ответ
                response = f"🤖 AI-консультант Buddah Base:\n\n{ai_response}"
                
                # Добавляем найденные материалы
                if materials:
                    response += "\n\n📚 Полезные материалы:"
                    for material in materials[:3]:
                        response += f"\n• {material['title']}"
                        if material.get('url'):
                            response += f" - {material['url']}"
                
                user = await db.get_user(telegram_id)
                remaining = Config.DAILY_AI_LIMIT - ((user.get('daily_requests', 0) or 0))
                response += f"\n\n💡 Осталось вопросов сегодня: {remaining}"
                
                return response
            else:
                return "❌ Извините, произошла ошибка при обработке запроса"
                
        except Exception as e:
            logger.error(f"Error processing monk request: {e}")
            return "❌ Произошла ошибка. Попробуйте позже"

# Глобальный экземпляр AI сервиса
ai_service = AIService()