import os
from dotenv import load_dotenv
from typing import List

load_dotenv()

class Config:
    # Telegram
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    ADMIN_CONTACT = os.getenv('ADMIN_CONTACT', 'smkbdh')
    
    # Supabase
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')
    SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')
    
    # OpenAI
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # YooKassa
    YOOKASSA_SECRET_KEY = os.getenv('YOOKASSA_SECRET_KEY')
    YOOKASSA_SHOP_ID = os.getenv('YOOKASSA_SHOP_ID')
    YOOKASSA_WEBHOOK_URL = os.getenv('YOOKASSA_WEBHOOK_URL')
    
    # Group Settings
    CLOSED_GROUP_ID = int(os.getenv('CLOSED_GROUP_ID', -1002840812146))
    MAIN_TOPIC_ID = int(os.getenv('MAIN_TOPIC_ID', 1))
    ADMINS = [int(x.strip()) for x in os.getenv('ADMINS', '').split(',') if x.strip()]
    
    # Payment Settings
    SUBSCRIPTION_PRICE = int(os.getenv('SUBSCRIPTION_PRICE', 999))  
    SUBSCRIPTION_CURRENCY = os.getenv('SUBSCRIPTION_CURRENCY', 'RUB')
    SUBSCRIPTION_DAYS = int(os.getenv('SUBSCRIPTION_DAYS', 365))
    
    # AI Settings
    DAILY_AI_LIMIT = 5
    
    # Bot Messages
    WELCOME_MESSAGE = """👋 Добро пожаловать в Buddah Base AI!

🤖 Это закрытое сообщество для изучения нейросетей, автоматизации и заработка на AI.

💎 Что вас ждёт после подписки:
✅ Доступ к закрытой группе с 2000+ участниками
✅ 30+ эксклюзивных видеоуроков
✅ 2000+ готовых промптов
✅ 50+ шаблонов автоматизации
✅ AI-консультант (5 вопросов в день)
✅ База знаний с поиском /monk

💳 Стоимость: {price} ₽ на {days} дней

🔥 Начать обучение?"""

    PAYMENT_SUCCESS_MESSAGE = """🎉 Оплата прошла успешно!

✅ Ваша подписка активирована на {days} дней
🤖 Доступ к AI-консультанту: {ai_limit} вопросов в день

🔗 **Ссылка на вступление в группу:**
{invite_link}

⚠️ **ВАЖНО:**
• Ссылка будет работать только 1 час
• Ссылка предназначена только для вас
• После перехода ссылка станет недействительной

🚀 После вступления в группу используйте:
/monk [вопрос] - AI-консультант  
/materials [запрос] - Поиск материалов

Добро пожаловать в Buddah Base! 🎉"""

    SUBSCRIPTION_EXPIRED_MESSAGE = """⏰ Ваша подписка истекла

Чтобы продолжать пользоваться всеми возможностями Buddah Base, продлите подписку:

💳 Стоимость: {price} ₽ на {days} дней"""

    AI_LIMIT_EXCEEDED_MESSAGE = """🤖 Лимит AI-вопросов исчерпан

Вы использовали все {limit} вопросов на сегодня.
Лимит обновится завтра в 00:00 МСК.

💡 Попробуйте поискать ответ в базе материалов командой /materials"""