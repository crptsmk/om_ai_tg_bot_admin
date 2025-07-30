#!/usr/bin/env python3
"""
Integration test for Buddah Base Telegram Bot
Tests actual bot functionality and message processing
"""

import requests
import json
import time
import sys
from config import Config

class BotIntegrationTester:
    def __init__(self):
        self.bot_token = Config.TELEGRAM_BOT_TOKEN
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

    def test_bot_info(self):
        """Test getting bot information"""
        try:
            response = requests.get(f"{self.base_url}/getMe", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    bot_info = data.get('result', {})
                    username = bot_info.get('username', 'unknown')
                    first_name = bot_info.get('first_name', 'unknown')
                    details = f"- @{username} ({first_name})"
                    return self.log_test("Bot Information", True, details)
                else:
                    return self.log_test("Bot Information", False, f"- API Error: {data.get('description')}")
            else:
                return self.log_test("Bot Information", False, f"- HTTP {response.status_code}")
        except Exception as e:
            return self.log_test("Bot Information", False, f"- Exception: {str(e)}")

    def test_get_updates(self):
        """Test getting updates from Telegram"""
        try:
            response = requests.get(f"{self.base_url}/getUpdates?limit=1", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    updates = data.get('result', [])
                    details = f"- Retrieved {len(updates)} recent updates"
                    return self.log_test("Get Updates", True, details)
                else:
                    return self.log_test("Get Updates", False, f"- API Error: {data.get('description')}")
            else:
                return self.log_test("Get Updates", False, f"- HTTP {response.status_code}")
        except Exception as e:
            return self.log_test("Get Updates", False, f"- Exception: {str(e)}")

    def test_set_bot_commands(self):
        """Test setting bot commands"""
        commands = [
            {"command": "start", "description": "Начать работу с ботом"},
            {"command": "help", "description": "Получить помощь и информацию о группе"},
            {"command": "info", "description": "Полная информация о VEO 3 и Buddah Base"}
        ]
        
        try:
            response = requests.post(
                f"{self.base_url}/setMyCommands",
                json={"commands": commands},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    details = f"- Set {len(commands)} commands"
                    return self.log_test("Set Bot Commands", True, details)
                else:
                    return self.log_test("Set Bot Commands", False, f"- API Error: {data.get('description')}")
            else:
                return self.log_test("Set Bot Commands", False, f"- HTTP {response.status_code}")
        except Exception as e:
            return self.log_test("Set Bot Commands", False, f"- Exception: {str(e)}")

    def test_bot_description(self):
        """Test setting bot description"""
        description = "Бот группы Buddah Base - помогает получить доступ к VEO 3 и материалам по нейросетям"
        
        try:
            response = requests.post(
                f"{self.base_url}/setMyDescription",
                json={"description": description},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    return self.log_test("Set Bot Description", True, "- Description updated")
                else:
                    return self.log_test("Set Bot Description", False, f"- API Error: {data.get('description')}")
            else:
                return self.log_test("Set Bot Description", False, f"- HTTP {response.status_code}")
        except Exception as e:
            return self.log_test("Set Bot Description", False, f"- Exception: {str(e)}")

    def test_message_length_limits(self):
        """Test message length limits"""
        from messages import BotMessages
        
        # Test main message length (Telegram limit is 4096 characters)
        main_msg = BotMessages.format_message(BotMessages.MAIN_INFO_MESSAGE, Config.ADMIN_CONTACT)
        if len(main_msg) <= 4096:
            self.log_test("Main Message Length", True, f"- {len(main_msg)}/4096 chars")
        else:
            self.log_test("Main Message Length", False, f"- {len(main_msg)}/4096 chars (too long)")

        # Test engagement message length
        engagement_msg = BotMessages.format_message(BotMessages.ENGAGEMENT_MESSAGE, Config.ADMIN_CONTACT)
        if len(engagement_msg) <= 4096:
            self.log_test("Engagement Message Length", True, f"- {len(engagement_msg)}/4096 chars")
        else:
            self.log_test("Engagement Message Length", False, f"- {len(engagement_msg)}/4096 chars (too long)")

        # Test group info message length
        group_msg = BotMessages.format_message(BotMessages.GROUP_INFO_MESSAGE, Config.ADMIN_CONTACT)
        if len(group_msg) <= 4096:
            self.log_test("Group Info Message Length", True, f"- {len(group_msg)}/4096 chars")
        else:
            self.log_test("Group Info Message Length", False, f"- {len(group_msg)}/4096 chars (too long)")

        return True

    def test_markdown_formatting(self):
        """Test markdown formatting in messages"""
        from messages import BotMessages
        
        try:
            # Check if messages contain valid markdown
            main_msg = BotMessages.format_message(BotMessages.MAIN_INFO_MESSAGE, Config.ADMIN_CONTACT)
            
            # Basic markdown validation
            markdown_elements = ['[', ']', '(', ')', '*', '_', '`']
            has_markdown = any(elem in main_msg for elem in markdown_elements)
            
            if has_markdown:
                # Check for balanced brackets
                open_brackets = main_msg.count('[')
                close_brackets = main_msg.count(']')
                open_parens = main_msg.count('(')
                close_parens = main_msg.count(')')
                
                if open_brackets == close_brackets and open_parens == close_parens:
                    return self.log_test("Markdown Formatting", True, "- Balanced brackets and parentheses")
                else:
                    return self.log_test("Markdown Formatting", False, "- Unbalanced brackets or parentheses")
            else:
                return self.log_test("Markdown Formatting", True, "- No markdown formatting used")
        except Exception as e:
            return self.log_test("Markdown Formatting", False, f"- Exception: {str(e)}")

    def test_admin_contact_format(self):
        """Test admin contact format"""
        admin_contact = Config.ADMIN_CONTACT
        
        # Check if admin contact is properly formatted (no @ symbol in config)
        if admin_contact and not admin_contact.startswith('@'):
            return self.log_test("Admin Contact Format", True, f"- @{admin_contact}")
        elif admin_contact and admin_contact.startswith('@'):
            return self.log_test("Admin Contact Format", False, "- Contains @ symbol (should not)")
        else:
            return self.log_test("Admin Contact Format", False, "- Admin contact not set")

    def run_integration_tests(self):
        """Run all integration tests"""
        print("🔗 Starting Bot Integration Testing")
        print("=" * 50)
        
        # API tests
        print("\n📡 Telegram API Tests:")
        self.test_bot_info()
        self.test_get_updates()
        
        # Configuration tests
        print("\n⚙️ Bot Configuration Tests:")
        self.test_set_bot_commands()
        self.test_bot_description()
        
        # Message validation tests
        print("\n💬 Message Validation Tests:")
        self.test_message_length_limits()
        self.test_markdown_formatting()
        self.test_admin_contact_format()
        
        # Summary
        print("\n" + "=" * 50)
        print(f"📊 Integration Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All integration tests passed!")
            return 0
        else:
            failed_tests = self.tests_run - self.tests_passed
            print(f"⚠️ {failed_tests} integration test(s) failed.")
            return 1

def main():
    """Main function"""
    tester = BotIntegrationTester()
    return tester.run_integration_tests()

if __name__ == "__main__":
    sys.exit(main())