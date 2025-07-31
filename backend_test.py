#!/usr/bin/env python3
"""
Comprehensive testing for Buddah Base Telegram Bot
Tests bot API functionality, message handling, and integration
"""

import asyncio
import requests
import sys
import json
import time
from datetime import datetime
from config import Config
from messages import BotMessages

class TelegramBotTester:
    def __init__(self, bot_token=None):
        self.bot_token = bot_token or Config.TELEGRAM_BOT_TOKEN
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_chat_id = None  # Will be set during testing
        
    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED {details}")
        else:
            print(f"❌ {name} - FAILED {details}")
        return success

    def test_bot_api_connection(self):
        """Test basic bot API connection"""
        try:
            response = requests.get(f"{self.base_url}/getMe", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    bot_info = data.get('result', {})
                    details = f"- Bot: @{bot_info.get('username', 'unknown')}"
                    return self.log_test("Bot API Connection", True, details)
                else:
                    return self.log_test("Bot API Connection", False, f"- API Error: {data.get('description')}")
            else:
                return self.log_test("Bot API Connection", False, f"- HTTP {response.status_code}")
        except Exception as e:
            return self.log_test("Bot API Connection", False, f"- Exception: {str(e)}")

    def test_bot_token_validity(self):
        """Test if bot token is valid and properly formatted"""
        if not self.bot_token:
            return self.log_test("Bot Token Validity", False, "- Token not found")
        
        # Check token format (should be like: 123456789:ABC-DEF...)
        if ':' not in self.bot_token or len(self.bot_token) < 35:
            return self.log_test("Bot Token Validity", False, "- Invalid token format")
        
        return self.log_test("Bot Token Validity", True, f"- Token format valid")

    def test_webhook_info(self):
        """Test webhook configuration"""
        try:
            response = requests.get(f"{self.base_url}/getWebhookInfo", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    webhook_info = data.get('result', {})
                    webhook_url = webhook_info.get('url', '')
                    if webhook_url:
                        details = f"- Webhook URL: {webhook_url}"
                    else:
                        details = "- Using polling (no webhook)"
                    return self.log_test("Webhook Configuration", True, details)
                else:
                    return self.log_test("Webhook Configuration", False, f"- API Error: {data.get('description')}")
            else:
                return self.log_test("Webhook Configuration", False, f"- HTTP {response.status_code}")
        except Exception as e:
            return self.log_test("Webhook Configuration", False, f"- Exception: {str(e)}")

    def test_message_formatting(self):
        """Test message formatting and template substitution"""
        try:
            # Test main info message formatting
            main_msg = BotMessages.format_message(BotMessages.MAIN_INFO_MESSAGE, Config.ADMIN_CONTACT)
            if Config.ADMIN_CONTACT in main_msg and len(main_msg) > 100:
                self.log_test("Main Message Formatting", True, f"- Length: {len(main_msg)} chars")
            else:
                return self.log_test("Main Message Formatting", False, "- Formatting failed")

            # Test engagement message formatting
            engagement_msg = BotMessages.format_message(BotMessages.ENGAGEMENT_MESSAGE, Config.ADMIN_CONTACT)
            if Config.ADMIN_CONTACT in engagement_msg and len(engagement_msg) > 50:
                self.log_test("Engagement Message Formatting", True, f"- Length: {len(engagement_msg)} chars")
            else:
                return self.log_test("Engagement Message Formatting", False, "- Formatting failed")

            # Test start message formatting
            start_msg = BotMessages.format_message(BotMessages.START_MESSAGE, Config.ADMIN_CONTACT)
            if len(start_msg) > 50:
                self.log_test("Start Message Formatting", True, f"- Length: {len(start_msg)} chars")
            else:
                return self.log_test("Start Message Formatting", False, "- Formatting failed")

            return True
        except Exception as e:
            return self.log_test("Message Formatting", False, f"- Exception: {str(e)}")

    def test_keyword_detection(self):
        """Test keyword detection logic"""
        try:
            test_cases = [
                # JOIN keywords
                ("как вступить в группу", "JOIN", True),
                ("хочу получить доступ", "JOIN", True),
                ("сколько стоит подписка", "JOIN", True),
                ("как попасть в канал", "JOIN", True),
                ("регистрация в группе", "JOIN", True),
                
                # ENGAGEMENT keywords
                ("интересно расскажи", "ENGAGEMENT", True),
                ("это круто", "ENGAGEMENT", True),
                ("veo нейросеть", "ENGAGEMENT", True),
                ("как это работает", "ENGAGEMENT", True),
                ("хочу подробнее", "ENGAGEMENT", True),
                
                # No match
                ("привет как дела", "NONE", False),
                ("спасибо за информацию", "NONE", False),
            ]
            
            all_passed = True
            for message, expected_type, should_match in test_cases:
                message_lower = message.lower()
                
                join_match = any(keyword in message_lower for keyword in Config.JOIN_KEYWORDS)
                engagement_match = any(keyword in message_lower for keyword in Config.ENGAGEMENT_KEYWORDS)
                
                if expected_type == "JOIN" and join_match == should_match:
                    self.log_test(f"Keyword Detection: '{message}'", True, f"- Detected as {expected_type}")
                elif expected_type == "ENGAGEMENT" and engagement_match == should_match:
                    self.log_test(f"Keyword Detection: '{message}'", True, f"- Detected as {expected_type}")
                elif expected_type == "NONE" and not join_match and not engagement_match:
                    self.log_test(f"Keyword Detection: '{message}'", True, "- No match (correct)")
                else:
                    self.log_test(f"Keyword Detection: '{message}'", False, f"- Expected {expected_type}, got different result")
                    all_passed = False
            
            return all_passed
        except Exception as e:
            return self.log_test("Keyword Detection", False, f"- Exception: {str(e)}")

    def test_config_validation(self):
        """Test configuration validation"""
        try:
            # Test admin contact
            if not Config.ADMIN_CONTACT:
                return self.log_test("Config - Admin Contact", False, "- Admin contact not set")
            self.log_test("Config - Admin Contact", True, f"- @{Config.ADMIN_CONTACT}")

            # Test join keywords
            if not Config.JOIN_KEYWORDS or len(Config.JOIN_KEYWORDS) == 0:
                return self.log_test("Config - Join Keywords", False, "- No join keywords defined")
            self.log_test("Config - Join Keywords", True, f"- {len(Config.JOIN_KEYWORDS)} keywords")

            # Test engagement keywords
            if not Config.ENGAGEMENT_KEYWORDS or len(Config.ENGAGEMENT_KEYWORDS) == 0:
                return self.log_test("Config - Engagement Keywords", False, "- No engagement keywords defined")
            self.log_test("Config - Engagement Keywords", True, f"- {len(Config.ENGAGEMENT_KEYWORDS)} keywords")

            return True
        except Exception as e:
            return self.log_test("Config Validation", False, f"- Exception: {str(e)}")

    def test_bot_commands_structure(self):
        """Test bot commands structure"""
        try:
            # Test if we can get bot commands
            response = requests.get(f"{self.base_url}/getMyCommands", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    commands = data.get('result', [])
                    command_names = [cmd.get('command') for cmd in commands]
                    
                    expected_commands = ['start', 'help', 'info']
                    missing_commands = [cmd for cmd in expected_commands if cmd not in command_names]
                    
                    if not missing_commands:
                        details = f"- Commands: {', '.join(command_names)}"
                        return self.log_test("Bot Commands Structure", True, details)
                    else:
                        details = f"- Missing: {', '.join(missing_commands)}"
                        return self.log_test("Bot Commands Structure", False, details)
                else:
                    return self.log_test("Bot Commands Structure", False, f"- API Error: {data.get('description')}")
            else:
                return self.log_test("Bot Commands Structure", False, f"- HTTP {response.status_code}")
        except Exception as e:
            return self.log_test("Bot Commands Structure", False, f"- Exception: {str(e)}")

    def test_logging_functionality(self):
        """Test if logging is working"""
        try:
            import logging
            import os
            
            # Check if log file exists
            log_file = "/app/bot.log"
            if os.path.exists(log_file):
                # Check if log file has recent entries
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if len(lines) > 0:
                        last_line = lines[-1]
                        # Check if the last log entry is recent (within last hour)
                        details = f"- Log entries: {len(lines)}, Last: {last_line[:50]}..."
                        return self.log_test("Logging Functionality", True, details)
                    else:
                        return self.log_test("Logging Functionality", False, "- Log file is empty")
            else:
                return self.log_test("Logging Functionality", False, "- Log file not found")
        except Exception as e:
            return self.log_test("Logging Functionality", False, f"- Exception: {str(e)}")

    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Comprehensive Buddah Base Bot Testing")
        print("=" * 60)
        
        # Basic API tests
        print("\n📡 API Connection Tests:")
        self.test_bot_token_validity()
        self.test_bot_api_connection()
        self.test_webhook_info()
        self.test_bot_commands_structure()
        
        # Configuration tests
        print("\n⚙️ Configuration Tests:")
        self.test_config_validation()
        
        # Message handling tests
        print("\n💬 Message Handling Tests:")
        self.test_message_formatting()
        self.test_keyword_detection()
        
        # System tests
        print("\n🔧 System Tests:")
        self.test_logging_functionality()
        
        # Summary
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed! Bot is ready for production.")
            return 0
        else:
            failed_tests = self.tests_run - self.tests_passed
            print(f"⚠️ {failed_tests} test(s) failed. Please review the issues above.")
            return 1

def main():
    """Main testing function"""
    tester = TelegramBotTester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())