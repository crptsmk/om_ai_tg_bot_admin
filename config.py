import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    ADMIN_CONTACT = os.getenv('ADMIN_CONTACT', 'smkbdh')
    
    # Ключевые слова для определения запросов о вступлении
    JOIN_KEYWORDS = [
        'как вступить', 'как попасть', 'как войти', 'как присоединиться',
        'хочу войти', 'хочу вступить', 'как получить доступ', 'доступ',
        'подписка', 'регистрация', 'стоимость', 'цена', 'сколько стоит'
    ]
    
    # Ключевые слова для общего взаимодействия
    ENGAGEMENT_KEYWORDS = [
        'интересно', 'круто', 'хочу', 'расскажи', 'подробнее', 
        'как это работает', 'veo', 'нейросеть', 'ai', 'ии'
    ]