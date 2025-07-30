#!/usr/bin/env python3
"""
Тестирование новых ключевых слов для запросов файлов
"""

import asyncio
from config import Config
from handlers import BotHandlers
from messages import BotMessages
from unittest.mock import Mock, AsyncMock

class FileKeywordsTest:
    
    def test_keywords_detection(self):
        """Тестирование обнаружения ключевых слов файлов"""
        print("🧪 Тестирование новых ключевых слов...")
        print("=" * 50)
        
        # Тестовые сообщения для файлов
        files_test_cases = [
            "дайте файлик пожалуйста",
            "скиньте student id",
            "есть файл с промптами?", 
            "поделитесь материалами",
            "где скачать базу?",
            "можно файл с шаблонами",
            "хочу файлы и гайды"
        ]
        
        # Тестовые сообщения для вступления
        join_test_cases = [
            "как вступить в группу",
            "нужен доступ к каналу",
            "сколько стоит подписка"
        ]
        
        # Тестовые сообщения для взаимодействия
        engagement_test_cases = [
            "интересно расскажи",
            "veo круто",
            "как это работает"
        ]
        
        print("📁 ФАЙЛЫ И МАТЕРИАЛЫ:")
        for msg in files_test_cases:
            msg_lower = msg.lower()
            has_files = any(keyword in msg_lower for keyword in Config.FILES_KEYWORDS)
            has_join = any(keyword in msg_lower for keyword in Config.JOIN_KEYWORDS)
            has_engagement = any(keyword in msg_lower for keyword in Config.ENGAGEMENT_KEYWORDS)
            
            if has_files:
                print(f"✅ '{msg}' → ФАЙЛЫ")
            elif has_join:
                print(f"🔄 '{msg}' → ВСТУПЛЕНИЕ")
            elif has_engagement:
                print(f"💬 '{msg}' → ВЗАИМОДЕЙСТВИЕ")
            else:
                print(f"❌ '{msg}' → НЕТ РЕАКЦИИ")
        
        print(f"\n💎 ВСТУПЛЕНИЕ:")
        for msg in join_test_cases:
            msg_lower = msg.lower()
            has_files = any(keyword in msg_lower for keyword in Config.FILES_KEYWORDS)
            has_join = any(keyword in msg_lower for keyword in Config.JOIN_KEYWORDS)
            has_engagement = any(keyword in msg_lower for keyword in Config.ENGAGEMENT_KEYWORDS)
            
            if has_files:
                print(f"🔄 '{msg}' → ФАЙЛЫ")
            elif has_join:
                print(f"✅ '{msg}' → ВСТУПЛЕНИЕ")
            elif has_engagement:
                print(f"💬 '{msg}' → ВЗАИМОДЕЙСТВИЕ")
            else:
                print(f"❌ '{msg}' → НЕТ РЕАКЦИИ")
        
        print(f"\n🔥 ВЗАИМОДЕЙСТВИЕ:")
        for msg in engagement_test_cases:
            msg_lower = msg.lower()
            has_files = any(keyword in msg_lower for keyword in Config.FILES_KEYWORDS)
            has_join = any(keyword in msg_lower for keyword in Config.JOIN_KEYWORDS)
            has_engagement = any(keyword in msg_lower for keyword in Config.ENGAGEMENT_KEYWORDS)
            
            if has_files:
                print(f"🔄 '{msg}' → ФАЙЛЫ")
            elif has_join:
                print(f"💎 '{msg}' → ВСТУПЛЕНИЕ")
            elif has_engagement:
                print(f"✅ '{msg}' → ВЗАИМОДЕЙСТВИЕ")
            else:
                print(f"❌ '{msg}' → НЕТ РЕАКЦИИ")
        
        print(f"\n📊 СТАТИСТИКА:")
        print(f"📁 Ключевых слов для файлов: {len(Config.FILES_KEYWORDS)}")
        print(f"💎 Ключевых слов для вступления: {len(Config.JOIN_KEYWORDS)}")
        print(f"🔥 Ключевых слов для взаимодействия: {len(Config.ENGAGEMENT_KEYWORDS)}")
        
        print(f"\n📝 КЛЮЧЕВЫЕ СЛОВА ДЛЯ ФАЙЛОВ:")
        for i, keyword in enumerate(Config.FILES_KEYWORDS, 1):
            print(f"   {i:2d}. {keyword}")

    def test_message_formatting(self):
        """Тестирование форматирования нового сообщения"""
        print(f"\n📋 НОВОЕ СООБЩЕНИЕ ДЛЯ ФАЙЛОВ:")
        print("=" * 50)
        
        files_message = BotMessages.format_message(
            BotMessages.FILES_REQUEST_MESSAGE, 
            Config.ADMIN_CONTACT
        )
        
        print(files_message)
        print(f"\n📏 Длина сообщения: {len(files_message)} символов")
        
        # Проверка ссылки
        if f"t.me/{Config.ADMIN_CONTACT}" in files_message:
            print("✅ Ссылка на администратора корректна")
        else:
            print("❌ Ошибка в ссылке на администратора")

if __name__ == "__main__":
    tester = FileKeywordsTest()
    tester.test_keywords_detection()
    tester.test_message_formatting()
    
    print(f"\n🎉 Тестирование завершено!")
    print(f"🚀 Бот теперь умеет:")
    print(f"   📁 Определять запросы файлов и материалов")
    print(f"   💎 Различать типы запросов (файлы/вступление/взаимодействие)")
    print(f"   🎯 Отправлять специализированные ответы")
    print(f"   🔗 Направлять к @{Config.ADMIN_CONTACT} с правильным CTA")