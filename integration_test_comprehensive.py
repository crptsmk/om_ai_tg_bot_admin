#!/usr/bin/env python3
"""
Comprehensive Integration Test for Buddah Base Telegram Bot
Tests the actual bot functionality including group/private chat logic
"""

import asyncio
import requests
import sys
import json
import time
from datetime import datetime
from config import Config
from handlers import BotHandlers
from telegram import Update, Message, Chat, User
from telegram.ext import ContextTypes
from unittest.mock import Mock, AsyncMock

class BotIntegrationTester:
    def __init__(self, bot_token=None):
        self.bot_token = bot_token or Config.TELEGRAM_BOT_TOKEN
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
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

    def create_mock_update(self, message_text, chat_type="private", user_id=12345, chat_id=67890, 
                          bot_mentioned=False, reply_to_bot=False):
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
        message.message_id = 123
        
        # Handle bot mentions
        if bot_mentioned:
            message.text = f"@saint_buddah_bot {message_text}"
        
        # Handle reply to bot
        if reply_to_bot:
            reply_message = Mock(spec=Message)
            reply_user = Mock(spec=User)
            reply_user.is_bot = True
            reply_message.from_user = reply_user
            message.reply_to_message = reply_message
        else:
            message.reply_to_message = None
        
        # Create mock update
        update = Mock(spec=Update)
        update.message = message
        update.effective_user = user
        update.effective_chat = chat
        
        return update

    async def test_private_chat_responses(self):
        """Test bot responses in private chats"""
        try:
            test_cases = [
                ("как вступить", "Should respond with join info"),
                ("интересно", "Should respond with engagement message"),
                ("привет", "Should respond with start message"),
                ("@saint_buddah_bot привет", "Should respond even with mention"),
            ]
            
            all_passed = True
            for message_text, expected_behavior in test_cases:
                # Create mock update for private chat
                update = self.create_mock_update(message_text, chat_type="private")
                context = Mock(spec=ContextTypes.DEFAULT_TYPE)
                
                # Mock the reply_text method
                reply_called = False
                reply_text = ""
                
                async def mock_reply_text(text, parse_mode=None):
                    nonlocal reply_called, reply_text
                    reply_called = True
                    reply_text = text
                
                update.message.reply_text = mock_reply_text
                
                # Test the handler
                await BotHandlers.handle_message(update, context)
                
                if reply_called:
                    self.log_test(f"Private Chat: '{message_text}'", True, f"- {expected_behavior}")
                else:
                    self.log_test(f"Private Chat: '{message_text}'", False, f"- No response when {expected_behavior}")
                    all_passed = False
            
            return all_passed
        except Exception as e:
            return self.log_test("Private Chat Responses", False, f"- Exception: {str(e)}")

    async def test_group_chat_responses(self):
        """Test bot responses in group chats"""
        try:
            test_cases = [
                # Should respond in groups
                ("как вступить", False, False, True, "Should respond to join keywords"),
                ("интересно", False, False, True, "Should respond to engagement keywords"),
                ("@saint_buddah_bot привет", True, False, True, "Should respond to bot mentions"),
                ("привет", False, True, True, "Should respond to replies to bot"),
                
                # Should NOT respond in groups
                ("привет как дела", False, False, False, "Should NOT respond to regular messages"),
                ("спасибо", False, False, False, "Should NOT respond to non-keyword messages"),
            ]
            
            all_passed = True
            for message_text, bot_mentioned, reply_to_bot, should_respond, expected_behavior in test_cases:
                # Create mock update for group chat
                update = self.create_mock_update(
                    message_text, 
                    chat_type="group", 
                    bot_mentioned=bot_mentioned,
                    reply_to_bot=reply_to_bot
                )
                context = Mock(spec=ContextTypes.DEFAULT_TYPE)
                
                # Mock the reply_text method
                reply_called = False
                reply_text = ""
                
                async def mock_reply_text(text, parse_mode=None):
                    nonlocal reply_called, reply_text
                    reply_called = True
                    reply_text = text
                
                update.message.reply_text = mock_reply_text
                
                # Test the handler
                await BotHandlers.handle_message(update, context)
                
                test_passed = (reply_called == should_respond)
                if test_passed:
                    status = "Responded" if reply_called else "No response"
                    self.log_test(f"Group Chat: '{message_text}'", True, f"- {status} - {expected_behavior}")
                else:
                    status = "Responded" if reply_called else "No response"
                    self.log_test(f"Group Chat: '{message_text}'", False, f"- {status} but {expected_behavior}")
                    all_passed = False
            
            return all_passed
        except Exception as e:
            return self.log_test("Group Chat Responses", False, f"- Exception: {str(e)}")

    async def test_command_handlers(self):
        """Test command handlers"""
        try:
            commands = [
                ("/start", BotHandlers.start_command, "START_MESSAGE"),
                ("/help", BotHandlers.help_command, "GROUP_INFO_MESSAGE"),
                ("/info", BotHandlers.info_command, "MAIN_INFO_MESSAGE"),
            ]
            
            all_passed = True
            for command, handler, expected_message_type in commands:
                # Create mock update
                update = self.create_mock_update(command, chat_type="private")
                context = Mock(spec=ContextTypes.DEFAULT_TYPE)
                
                # Mock the reply_text method
                reply_called = False
                reply_text = ""
                
                async def mock_reply_text(text, parse_mode=None):
                    nonlocal reply_called, reply_text
                    reply_called = True
                    reply_text = text
                
                update.message.reply_text = mock_reply_text
                
                # Test the handler
                await handler(update, context)
                
                if reply_called and len(reply_text) > 50:
                    self.log_test(f"Command Handler: {command}", True, f"- Response length: {len(reply_text)} chars")
                else:
                    self.log_test(f"Command Handler: {command}", False, "- No proper response")
                    all_passed = False
            
            return all_passed
        except Exception as e:
            return self.log_test("Command Handlers", False, f"- Exception: {str(e)}")

    async def test_inline_query_handler(self):
        """Test inline query handler"""
        try:
            # Create mock inline query
            inline_query = Mock()
            inline_query.query = "вступить"
            inline_query.answer = AsyncMock()
            
            update = Mock(spec=Update)
            update.inline_query = inline_query
            
            context = Mock(spec=ContextTypes.DEFAULT_TYPE)
            
            # Test the handler
            await BotHandlers.handle_inline_query(update, context)
            
            # Check if answer was called
            if inline_query.answer.called:
                args = inline_query.answer.call_args
                results = args[0][0] if args and len(args[0]) > 0 else []
                
                if len(results) > 0:
                    self.log_test("Inline Query Handler", True, f"- Returned {len(results)} results")
                    return True
                else:
                    self.log_test("Inline Query Handler", False, "- No results returned")
                    return False
            else:
                self.log_test("Inline Query Handler", False, "- Answer method not called")
                return False
        except Exception as e:
            return self.log_test("Inline Query Handler", False, f"- Exception: {str(e)}")

    def test_bot_status_check(self):
        """Test if bot is running and responsive"""
        try:
            # Check if bot process is running
            import subprocess
            result = subprocess.run(['pgrep', '-f', 'bot.py'], capture_output=True, text=True)
            
            if result.returncode == 0:
                pid = result.stdout.strip()
                self.log_test("Bot Process Status", True, f"- Running with PID: {pid}")
                
                # Check API responsiveness
                response = requests.get(f"{self.base_url}/getMe", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('ok'):
                        self.log_test("Bot API Responsiveness", True, "- API responding correctly")
                        return True
                    else:
                        self.log_test("Bot API Responsiveness", False, f"- API Error: {data.get('description')}")
                        return False
                else:
                    self.log_test("Bot API Responsiveness", False, f"- HTTP {response.status_code}")
                    return False
            else:
                self.log_test("Bot Process Status", False, "- Bot process not found")
                return False
        except Exception as e:
            return self.log_test("Bot Status Check", False, f"- Exception: {str(e)}")

    async def run_all_tests(self):
        """Run all integration tests"""
        print("🚀 Starting Comprehensive Bot Integration Testing")
        print("=" * 70)
        
        # Bot status tests
        print("\n🔍 Bot Status Tests:")
        self.test_bot_status_check()
        
        # Message handling tests
        print("\n💬 Message Handling Tests:")
        await self.test_private_chat_responses()
        await self.test_group_chat_responses()
        
        # Command tests
        print("\n⚡ Command Handler Tests:")
        await self.test_command_handlers()
        
        # Inline query tests
        print("\n🔗 Inline Query Tests:")
        await self.test_inline_query_handler()
        
        # Summary
        print("\n" + "=" * 70)
        print(f"📊 Integration Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All integration tests passed! Bot functionality is working correctly.")
            return 0
        else:
            failed_tests = self.tests_run - self.tests_passed
            print(f"⚠️ {failed_tests} integration test(s) failed. Please review the issues above.")
            return 1

async def main():
    """Main testing function"""
    tester = BotIntegrationTester()
    return await tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))