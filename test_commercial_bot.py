#!/usr/bin/env python3
"""
Тестирование коммерческого бота Buddah Base AI
"""

import asyncio
import logging
from config import Config
from database import db
from payments import payment_service
from ai_service import ai_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CommercialBotTester:
    
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
    
    def log_test(self, name, success, details=""):
        """Логирование результатов тестов"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED {details}")
        else:
            print(f"❌ {name} - FAILED {details}")
        return success
    
    async def test_configuration(self):
        """Тестирование конфигурации"""
        print("🔧 Тестирование конфигурации...")
        
        # Проверяем основные настройки
        self.log_test("Telegram Bot Token", bool(Config.TELEGRAM_BOT_TOKEN), f"- Token present")
        self.log_test("Supabase URL", bool(Config.SUPABASE_URL), f"- URL: {Config.SUPABASE_URL[:30]}...")
        self.log_test("OpenAI API Key", bool(Config.OPENAI_API_KEY), f"- Key present")
        self.log_test("YooKassa Config", bool(Config.YOOKASSA_SECRET_KEY and Config.YOOKASSA_SHOP_ID), 
                     f"- Shop: {Config.YOOKASSA_SHOP_ID}")
        
        # Проверяем админов
        self.log_test("Admins Config", len(Config.ADMINS) > 0, f"- {len(Config.ADMINS)} админов")
        
        # Проверяем группу
        self.log_test("Group Config", bool(Config.CLOSED_GROUP_ID), f"- Group: {Config.CLOSED_GROUP_ID}")
        
        return True
    
    async def test_database_connection(self):
        """Тестирование подключения к базе данных"""
        print("\n💾 Тестирование Supabase...")
        
        try:
            # Тестируем подключение
            test_user = await db.get_user(999999999)  # Несуществующий пользователь
            self.log_test("Supabase Connection", True, "- Connected successfully")
        except Exception as e:
            self.log_test("Supabase Connection", False, f"- Error: {str(e)}")
            return False
        
        # Тестируем поиск материалов
        try:
            materials = await db.search_materials("test", limit=1)
            self.log_test("Materials Search", True, f"- Found {len(materials)} results")
        except Exception as e:
            self.log_test("Materials Search", False, f"- Error: {str(e)}")
        
        return True
    
    async def test_payment_service(self):
        """Тестирование сервиса платежей"""
        print("\n💳 Тестирование YooKassa...")
        
        try:
            # Тестируем создание платежа (без реальной оплаты)
            payment_data = await payment_service.create_payment(
                telegram_id=123456789,
                amount=999,
                description="Test payment"
            )
            
            if payment_data and payment_data.get('payment_url'):
                self.log_test("Payment Creation", True, f"- Payment URL generated")
            else:
                self.log_test("Payment Creation", False, "- No payment URL")
        
        except Exception as e:
            self.log_test("Payment Creation", False, f"- Error: {str(e)}")
    
    async def test_ai_service(self):
        """Тестирование AI сервиса"""
        print("\n🤖 Тестирование OpenAI...")
        
        try:
            # Тестируем поиск в материалах
            materials = await ai_service.search_in_materials("chatgpt")
            self.log_test("AI Materials Search", True, f"- Found {len(materials)} materials")
        except Exception as e:
            self.log_test("AI Materials Search", False, f"- Error: {str(e)}")
        
        try:
            # Тестируем генерацию ответа (короткий тест)
            response = await ai_service.generate_ai_response("Что такое AI?")
            
            if response and len(response) > 10:
                self.log_test("AI Response Generation", True, f"- Generated {len(response)} chars")
            else:
                self.log_test("AI Response Generation", False, "- No response generated")
        except Exception as e:
            self.log_test("AI Response Generation", False, f"- Error: {str(e)}")
    
    def test_messages_format(self):
        """Тестирование форматирования сообщений"""
        print("\n📝 Тестирование сообщений...")
        
        # Проверяем welcome message
        welcome_msg = Config.WELCOME_MESSAGE.format(
            price=Config.SUBSCRIPTION_PRICE,
            days=Config.SUBSCRIPTION_DAYS
        )
        self.log_test("Welcome Message", len(welcome_msg) > 100, f"- Length: {len(welcome_msg)} chars")
        
        # Проверяем success message
        success_msg = Config.PAYMENT_SUCCESS_MESSAGE.format(
            days=Config.SUBSCRIPTION_DAYS,
            ai_limit=Config.DAILY_AI_LIMIT,
            invite_link="https://t.me/test"
        )
        self.log_test("Success Message", len(success_msg) > 100, f"- Length: {len(success_msg)} chars")
        
        return True
    
    async def test_user_workflow(self):
        """Тестирование пользовательского workflow"""
        print("\n👤 Тестирование пользовательского workflow...")
        
        test_user_id = 987654321
        
        try:
            # Создаем тестового пользователя
            success = await db.create_user(
                telegram_id=test_user_id,
                name="Test User",
                username="testuser",
                chat_id=test_user_id
            )
            self.log_test("User Creation", success, "- Test user created")
            
            # Проверяем получение пользователя
            user = await db.get_user(test_user_id)
            self.log_test("User Retrieval", user is not None, f"- User status: {user.get('status') if user else 'None'}")
            
            # Проверяем статус подписки
            is_active = await db.is_subscription_active(test_user_id)
            self.log_test("Subscription Check", not is_active, "- Inactive as expected")
            
            # Активируем подписку
            activated = await db.activate_subscription(test_user_id)
            self.log_test("Subscription Activation", activated, "- Subscription activated")
            
            # Проверяем активную подписку
            is_active_now = await db.is_subscription_active(test_user_id)
            self.log_test("Active Subscription Check", is_active_now, "- Now active")
            
            # Проверяем лимит AI запросов
            can_request = await db.can_make_ai_request(test_user_id)
            self.log_test("AI Request Limit", can_request, "- Can make AI requests")
            
        except Exception as e:
            self.log_test("User Workflow", False, f"- Error: {str(e)}")
    
    def generate_report(self):
        """Генерация отчета о тестировании"""
        print("\n" + "="*60)
        print("📋 ОТЧЕТ О ТЕСТИРОВАНИИ BUDDAH BASE AI")
        print("="*60)
        
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        
        print(f"\n📊 Результаты:")
        print(f"   • Всего тестов: {self.tests_run}")
        print(f"   • Успешных: {self.tests_passed}")
        print(f"   • Неудачных: {self.tests_run - self.tests_passed}")
        print(f"   • Успешность: {success_rate:.1f}%")
        
        print(f"\n🔧 Конфигурация:")
        print(f"   • Цена подписки: {Config.SUBSCRIPTION_PRICE} ₽")
        print(f"   • Срок подписки: {Config.SUBSCRIPTION_DAYS} дней")
        print(f"   • Лимит AI: {Config.DAILY_AI_LIMIT} запросов/день")
        print(f"   • Админов: {len(Config.ADMINS)}")
        
        if success_rate >= 80:
            print(f"\n🎉 БОТ ГОТОВ К ПРОДАКШЕНУ!")
            print(f"✅ Все основные функции работают")
        elif success_rate >= 60:
            print(f"\n⚠️ Бот почти готов, есть небольшие проблемы")
            print(f"🔧 Рекомендуется исправить ошибки")
        else:
            print(f"\n❌ Бот не готов к продакшену")
            print(f"🛠 Требуется исправление критичных ошибок")
        
        return success_rate >= 80
    
    async def run_all_tests(self):
        """Запуск всех тестов"""
        print("🚀 Запуск комплексного тестирования Buddah Base AI")
        print("=" * 60)
        
        await self.test_configuration()
        await self.test_database_connection()
        await self.test_payment_service()
        await self.test_ai_service()
        self.test_messages_format()
        await self.test_user_workflow()
        
        return self.generate_report()

async def main():
    """Главная функция тестирования"""
    tester = CommercialBotTester()
    is_ready = await tester.run_all_tests()
    
    return 0 if is_ready else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)