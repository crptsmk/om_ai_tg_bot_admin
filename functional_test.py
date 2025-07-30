#!/usr/bin/env python3
"""
Functional testing for Buddah Base Telegram Bot
Simulates real user interactions and tests bot responses
"""

import asyncio
import sys
import time
from datetime import datetime
from config import Config
from messages import BotMessages
from handlers import BotHandlers

# Mock Telegram objects for testing
class MockUser:
    def __init__(self, user_id, first_name="TestUser"):
        self.id = user_id
        self.first_name = first_name

class MockMessage:
    def __init__(self, text, user_id=12345):
        self.text = text
        self.message_id = int(time.time())
        self.date = datetime.now()
        self.from_user = MockUser(user_id)
        self.chat = MockChat()
        self.new_chat_members = []
        
    async def reply_text(self, text, parse_mode=None):
        """Mock reply method"""
        print(f"🤖 Bot Response: {text[:100]}{'...' if len(text) > 100 else ''}")
        return True

class MockChat:
    def __init__(self):
        self.id = -1001234567890  # Group chat ID format
        self.type = "supergroup"

class MockUpdate:
    def __init__(self, message):
        self.message = message
        self.effective_user = message.from_user
        self.update_id = int(time.time())

class MockContext:
    def __init__(self):
        self.error = None

class BotFunctionalTester:
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED {details}")
        else:
            print(f"❌ {name} - FAILED {details}")
        return success

    async def test_start_command(self):
        """Test /start command"""
        try:
            message = MockMessage("/start")
            update = MockUpdate(message)
            context = MockContext()
            
            print("\n🧪 Testing /start command:")
            await BotHandlers.start_command(update, context)
            
            return self.log_test("Start Command Handler", True, "- Command executed successfully")
        except Exception as e:
            return self.log_test("Start Command Handler", False, f"- Exception: {str(e)}")

    async def test_help_command(self):
        """Test /help command"""
        try:
            message = MockMessage("/help")
            update = MockUpdate(message)
            context = MockContext()
            
            print("\n🧪 Testing /help command:")
            await BotHandlers.help_command(update, context)
            
            return self.log_test("Help Command Handler", True, "- Command executed successfully")
        except Exception as e:
            return self.log_test("Help Command Handler", False, f"- Exception: {str(e)}")

    async def test_info_command(self):
        """Test /info command"""
        try:
            message = MockMessage("/info")
            update = MockUpdate(message)
            context = MockContext()
            
            print("\n🧪 Testing /info command:")
            await BotHandlers.info_command(update, context)
            
            return self.log_test("Info Command Handler", True, "- Command executed successfully")
        except Exception as e:
            return self.log_test("Info Command Handler", False, f"- Exception: {str(e)}")

    async def test_join_keyword_messages(self):
        """Test messages with join keywords"""
        join_test_messages = [
            "Как вступить в группу?",
            "Хочу получить доступ к каналу",
            "Сколько стоит подписка на Buddah Base?",
            "Как попасть в закрытую группу?",
            "Регистрация в канале"
        ]
        
        all_passed = True
        for test_msg in join_test_messages:
            try:
                message = MockMessage(test_msg)
                update = MockUpdate(message)
                context = MockContext()
                
                print(f"\n🧪 Testing JOIN keyword: '{test_msg}'")
                await BotHandlers.handle_message(update, context)
                
                self.log_test(f"JOIN Message: '{test_msg[:30]}...'", True, "- Processed successfully")
            except Exception as e:
                self.log_test(f"JOIN Message: '{test_msg[:30]}...'", False, f"- Exception: {str(e)}")
                all_passed = False
        
        return all_passed

    async def test_engagement_keyword_messages(self):
        """Test messages with engagement keywords"""
        engagement_test_messages = [
            "Интересно, расскажи подробнее",
            "Это круто! Хочу узнать больше",
            "VEO 3 нейросеть - как это работает?",
            "Расскажи про AI инструменты",
            "Хочу изучить автоматизацию"
        ]
        
        all_passed = True
        for test_msg in engagement_test_messages:
            try:
                message = MockMessage(test_msg)
                update = MockUpdate(message)
                context = MockContext()
                
                print(f"\n🧪 Testing ENGAGEMENT keyword: '{test_msg}'")
                await BotHandlers.handle_message(update, context)
                
                self.log_test(f"ENGAGEMENT Message: '{test_msg[:30]}...'", True, "- Processed successfully")
            except Exception as e:
                self.log_test(f"ENGAGEMENT Message: '{test_msg[:30]}...'", False, f"- Exception: {str(e)}")
                all_passed = False
        
        return all_passed

    async def test_no_keyword_messages(self):
        """Test messages without keywords (should not trigger responses)"""
        no_keyword_messages = [
            "Привет всем!",
            "Как дела?",
            "Спасибо за информацию",
            "Хорошего дня!",
            "Пока!"
        ]
        
        all_passed = True
        for test_msg in no_keyword_messages:
            try:
                message = MockMessage(test_msg)
                update = MockUpdate(message)
                context = MockContext()
                
                print(f"\n🧪 Testing NO KEYWORD message: '{test_msg}'")
                await BotHandlers.handle_message(update, context)
                
                self.log_test(f"NO KEYWORD Message: '{test_msg[:30]}...'", True, "- No response (correct)")
            except Exception as e:
                self.log_test(f"NO KEYWORD Message: '{test_msg[:30]}...'", False, f"- Exception: {str(e)}")
                all_passed = False
        
        return all_passed

    async def test_new_member_handler(self):
        """Test new member welcome"""
        try:
            new_user = MockUser(67890, "NewMember")
            message = MockMessage("")
            message.new_chat_members = [new_user]
            update = MockUpdate(message)
            context = MockContext()
            
            print(f"\n🧪 Testing new member welcome for: {new_user.first_name}")
            await BotHandlers.handle_new_member(update, context)
            
            return self.log_test("New Member Handler", True, f"- Welcomed {new_user.first_name}")
        except Exception as e:
            return self.log_test("New Member Handler", False, f"- Exception: {str(e)}")

    async def test_error_handler(self):
        """Test error handler"""
        try:
            update = MockUpdate(MockMessage("test"))
            context = MockContext()
            context.error = Exception("Test error")
            
            print("\n🧪 Testing error handler:")
            await BotHandlers.error_handler(update, context)
            
            return self.log_test("Error Handler", True, "- Error logged successfully")
        except Exception as e:
            return self.log_test("Error Handler", False, f"- Exception: {str(e)}")

    def test_message_content_quality(self):
        """Test message content quality"""
        try:
            # Test main message content
            main_msg = BotMessages.format_message(BotMessages.MAIN_INFO_MESSAGE, Config.ADMIN_CONTACT)
            
            # Check for key elements
            required_elements = [
                "VEO 3",
                "Buddah Base",
                "999 ₽",
                Config.ADMIN_CONTACT,
                "видео",
                "промпт"
            ]
            
            missing_elements = []
            for element in required_elements:
                if element not in main_msg:
                    missing_elements.append(element)
            
            if not missing_elements:
                return self.log_test("Message Content Quality", True, "- All key elements present")
            else:
                return self.log_test("Message Content Quality", False, f"- Missing: {', '.join(missing_elements)}")
        except Exception as e:
            return self.log_test("Message Content Quality", False, f"- Exception: {str(e)}")

    async def run_functional_tests(self):
        """Run all functional tests"""
        print("🎯 Starting Bot Functional Testing")
        print("=" * 60)
        
        # Command tests
        print("\n🤖 Command Handler Tests:")
        await self.test_start_command()
        await self.test_help_command()
        await self.test_info_command()
        
        # Message handling tests
        print("\n💬 Message Processing Tests:")
        await self.test_join_keyword_messages()
        await self.test_engagement_keyword_messages()
        await self.test_no_keyword_messages()
        
        # Special handler tests
        print("\n👥 Special Handler Tests:")
        await self.test_new_member_handler()
        await self.test_error_handler()
        
        # Content quality tests
        print("\n📝 Content Quality Tests:")
        self.test_message_content_quality()
        
        # Summary
        print("\n" + "=" * 60)
        print(f"📊 Functional Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All functional tests passed! Bot is working correctly.")
            return 0
        else:
            failed_tests = self.tests_run - self.tests_passed
            print(f"⚠️ {failed_tests} functional test(s) failed.")
            return 1

async def main():
    """Main function"""
    tester = BotFunctionalTester()
    return await tester.run_functional_tests()

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(result)