#!/usr/bin/env python3
"""
Comprehensive test for new file request keywords and priority system
Tests the updated Telegram bot functionality
"""

import asyncio
import sys
from unittest.mock import Mock, AsyncMock
from config import Config
from handlers import BotHandlers
from messages import BotMessages
from telegram import Update, Message, Chat, User
from telegram.ext import ContextTypes

class FilesPriorityTester:
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

    def create_mock_update(self, message_text, chat_type="private", user_id=12345, chat_id=67890):
        """Create a mock Update object for testing"""
        # Create mock user
        user = Mock(spec=User)
        user.id = user_id
        user.first_name = "TestUser"
        user.username = "testuser"
        user.is_bot = False
        
        # Create mock chat
        chat = Mock(spec=Chat)
        chat.id = chat_id
        chat.type = chat_type
        
        # Create mock message
        message = Mock(spec=Message)
        message.text = message_text
        message.chat = chat
        message.from_user = user
        message.reply_to_message = None
        message.reply_text = AsyncMock()
        
        # Create mock update
        update = Mock(spec=Update)
        update.message = message
        update.effective_user = user
        
        return update

    async def test_files_keywords_priority(self):
        """Test that file keywords have highest priority"""
        print("\n🔥 Testing Files Keywords Priority...")
        
        test_cases = [
            # Mixed keywords - files should win
            ("дайте файлик как вступить", "FILES", "Mixed files+join should trigger files"),
            ("скинь материалы интересно", "FILES", "Mixed files+engagement should trigger files"),
            ("поделитесь промптами как попасть", "FILES", "Mixed files+join should trigger files"),
            
            # Pure files keywords
            ("дайте файлик", "FILES", "Pure files keyword"),
            ("скиньте student id", "FILES", "Student ID request"),
            ("есть промпты?", "FILES", "Prompts request"),
            ("материалы где скачать", "FILES", "Materials download request"),
            ("хочу файлы", "FILES", "Want files request"),
        ]
        
        all_passed = True
        for message_text, expected_type, description in test_cases:
            update = self.create_mock_update(message_text)
            context = Mock(spec=ContextTypes.DEFAULT_TYPE)
            
            # Call the handler
            await BotHandlers.handle_message(update, context)
            
            # Check what message was sent
            reply_calls = update.message.reply_text.call_args_list
            if reply_calls:
                sent_message = reply_calls[0][0][0]  # First positional argument
                
                if expected_type == "FILES":
                    if "📁 Хочешь получить файлы" in sent_message:
                        self.log_test(f"Priority Test: '{message_text}'", True, f"- {description}")
                    else:
                        self.log_test(f"Priority Test: '{message_text}'", False, f"- Expected FILES message, got different")
                        all_passed = False
                else:
                    self.log_test(f"Priority Test: '{message_text}'", False, f"- Unexpected message type")
                    all_passed = False
            else:
                self.log_test(f"Priority Test: '{message_text}'", False, f"- No message sent")
                all_passed = False
        
        return all_passed

    async def test_join_keywords_priority(self):
        """Test join keywords when no files keywords present"""
        print("\n💎 Testing Join Keywords Priority...")
        
        test_cases = [
            ("как вступить в группу", "JOIN", "Join request"),
            ("нужен доступ", "JOIN", "Access request"),
            ("сколько стоит подписка", "JOIN", "Price inquiry"),
            ("как попасть интересно", "JOIN", "Mixed join+engagement should trigger join"),
        ]
        
        all_passed = True
        for message_text, expected_type, description in test_cases:
            update = self.create_mock_update(message_text)
            context = Mock(spec=ContextTypes.DEFAULT_TYPE)
            
            await BotHandlers.handle_message(update, context)
            
            reply_calls = update.message.reply_text.call_args_list
            if reply_calls:
                sent_message = reply_calls[0][0][0]
                
                if expected_type == "JOIN":
                    if "👋 Привет! Спасибо, что заглянул к нам" in sent_message:
                        self.log_test(f"Join Priority Test: '{message_text}'", True, f"- {description}")
                    else:
                        self.log_test(f"Join Priority Test: '{message_text}'", False, f"- Expected JOIN message, got different")
                        all_passed = False
            else:
                self.log_test(f"Join Priority Test: '{message_text}'", False, f"- No message sent")
                all_passed = False
        
        return all_passed

    async def test_engagement_keywords_priority(self):
        """Test engagement keywords when no files/join keywords present"""
        print("\n🔥 Testing Engagement Keywords Priority...")
        
        test_cases = [
            ("интересно расскажи", "ENGAGEMENT", "Interest request"),
            ("veo круто", "ENGAGEMENT", "VEO mention"),
            ("как это работает", "ENGAGEMENT", "How it works"),
            ("хочу подробнее", "ENGAGEMENT", "Want details"),
        ]
        
        all_passed = True
        for message_text, expected_type, description in test_cases:
            update = self.create_mock_update(message_text)
            context = Mock(spec=ContextTypes.DEFAULT_TYPE)
            
            await BotHandlers.handle_message(update, context)
            
            reply_calls = update.message.reply_text.call_args_list
            if reply_calls:
                sent_message = reply_calls[0][0][0]
                
                if expected_type == "ENGAGEMENT":
                    if "🔥 Заинтересовался?" in sent_message:
                        self.log_test(f"Engagement Priority Test: '{message_text}'", True, f"- {description}")
                    else:
                        self.log_test(f"Engagement Priority Test: '{message_text}'", False, f"- Expected ENGAGEMENT message, got different")
                        all_passed = False
            else:
                self.log_test(f"Engagement Priority Test: '{message_text}'", False, f"- No message sent")
                all_passed = False
        
        return all_passed

    async def test_group_vs_private_behavior(self):
        """Test different behavior in groups vs private chats"""
        print("\n👥 Testing Group vs Private Chat Behavior...")
        
        # Test private chat - should respond to everything
        private_update = self.create_mock_update("привет как дела", chat_type="private")
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        
        await BotHandlers.handle_message(private_update, context)
        
        private_reply_calls = private_update.message.reply_text.call_args_list
        if private_reply_calls:
            self.log_test("Private Chat Response", True, "- Responds to non-keyword message")
        else:
            self.log_test("Private Chat Response", False, "- Should respond in private chat")
        
        # Test group chat - should NOT respond to non-keyword message
        group_update = self.create_mock_update("привет как дела", chat_type="group")
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        
        await BotHandlers.handle_message(group_update, context)
        
        group_reply_calls = group_update.message.reply_text.call_args_list
        if not group_reply_calls:
            self.log_test("Group Chat No Response", True, "- Correctly ignores non-keyword message")
        else:
            self.log_test("Group Chat No Response", False, "- Should not respond to non-keyword in group")
        
        # Test group chat with files keyword - should respond
        group_files_update = self.create_mock_update("дайте файлик", chat_type="group")
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        
        await BotHandlers.handle_message(group_files_update, context)
        
        group_files_reply_calls = group_files_update.message.reply_text.call_args_list
        if group_files_reply_calls:
            sent_message = group_files_reply_calls[0][0][0]
            if "📁 Хочешь получить файлы" in sent_message:
                self.log_test("Group Chat Files Response", True, "- Responds to files keyword in group")
            else:
                self.log_test("Group Chat Files Response", False, "- Wrong message type for files keyword")
        else:
            self.log_test("Group Chat Files Response", False, "- Should respond to files keyword in group")

    async def test_all_files_keywords(self):
        """Test all 20 files keywords individually"""
        print("\n📁 Testing All Files Keywords...")
        
        files_keywords = Config.FILES_KEYWORDS
        all_passed = True
        
        for keyword in files_keywords:
            test_message = f"Привет, {keyword} пожалуйста"
            update = self.create_mock_update(test_message)
            context = Mock(spec=ContextTypes.DEFAULT_TYPE)
            
            await BotHandlers.handle_message(update, context)
            
            reply_calls = update.message.reply_text.call_args_list
            if reply_calls:
                sent_message = reply_calls[0][0][0]
                if "📁 Хочешь получить файлы" in sent_message:
                    self.log_test(f"Files Keyword: '{keyword}'", True, "- Triggers files message")
                else:
                    self.log_test(f"Files Keyword: '{keyword}'", False, "- Does not trigger files message")
                    all_passed = False
            else:
                self.log_test(f"Files Keyword: '{keyword}'", False, "- No response")
                all_passed = False
        
        return all_passed

    def test_message_content_validation(self):
        """Test that the FILES_REQUEST_MESSAGE contains correct content"""
        print("\n📋 Testing Files Message Content...")
        
        files_message = BotMessages.format_message(
            BotMessages.FILES_REQUEST_MESSAGE, 
            Config.ADMIN_CONTACT
        )
        
        required_elements = [
            ("📁 Хочешь получить файлы", "Header"),
            ("2000+ готовых промптов", "Prompts mention"),
            ("50+ шаблонов автоматизации", "Templates mention"),
            ("1000+ AI-инструментов", "AI tools mention"),
            ("999 ₽ на год", "Price mention"),
            (f"t.me/{Config.ADMIN_CONTACT}", "Admin contact link"),
            ("Хочу файлы и доступ", "CTA text"),
        ]
        
        all_passed = True
        for element, description in required_elements:
            if element in files_message:
                self.log_test(f"Message Content: {description}", True, f"- Found: '{element}'")
            else:
                self.log_test(f"Message Content: {description}", False, f"- Missing: '{element}'")
                all_passed = False
        
        return all_passed

    async def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Files Priority & Functionality Testing")
        print("=" * 60)
        
        # Test message content first
        self.test_message_content_validation()
        
        # Test priority system
        await self.test_files_keywords_priority()
        await self.test_join_keywords_priority()
        await self.test_engagement_keywords_priority()
        
        # Test group vs private behavior
        await self.test_group_vs_private_behavior()
        
        # Test all files keywords
        await self.test_all_files_keywords()
        
        # Summary
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All files functionality tests passed!")
            print("✅ Files keywords have highest priority")
            print("✅ All 20 files keywords work correctly")
            print("✅ Group/private chat logic works")
            print("✅ Message content is correct")
            return 0
        else:
            failed_tests = self.tests_run - self.tests_passed
            print(f"⚠️ {failed_tests} test(s) failed. Please review the issues above.")
            return 1

async def main():
    """Main testing function"""
    tester = FilesPriorityTester()
    return await tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))