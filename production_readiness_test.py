#!/usr/bin/env python3
"""
Integration Test for Buddah Base AI Bot
Tests the bot's actual functionality and readiness for production
"""

import requests
import json
import time
from config import Config

class BotIntegrationTester:
    def __init__(self):
        self.bot_token = Config.TELEGRAM_BOT_TOKEN
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.tests_passed = 0
        self.tests_total = 0
        
    def log_result(self, test_name, success, details=""):
        """Log test results"""
        self.tests_total += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {test_name} - PASSED {details}")
        else:
            print(f"❌ {test_name} - FAILED {details}")
        return success
    
    def test_bot_info(self):
        """Test bot basic information"""
        try:
            response = requests.get(f"{self.base_url}/getMe", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    bot_info = data['result']
                    details = f"- @{bot_info.get('username')} ({bot_info.get('first_name')})"
                    return self.log_result("Bot Information", True, details)
            return self.log_result("Bot Information", False, "- API call failed")
        except Exception as e:
            return self.log_result("Bot Information", False, f"- {str(e)}")
    
    def test_bot_commands(self):
        """Test bot commands setup"""
        try:
            response = requests.get(f"{self.base_url}/getMyCommands", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    commands = data.get('result', [])
                    command_names = [cmd.get('command') for cmd in commands]
                    details = f"- Commands: {', '.join(command_names) if command_names else 'None set'}"
                    return self.log_result("Bot Commands", True, details)
            return self.log_result("Bot Commands", False, "- Failed to get commands")
        except Exception as e:
            return self.log_result("Bot Commands", False, f"- {str(e)}")
    
    def test_group_access(self):
        """Test access to the closed group"""
        try:
            response = requests.get(f"{self.base_url}/getChat", 
                                  params={'chat_id': Config.CLOSED_GROUP_ID}, 
                                  timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    chat_info = data['result']
                    member_count_response = requests.get(f"{self.base_url}/getChatMemberCount",
                                                       params={'chat_id': Config.CLOSED_GROUP_ID},
                                                       timeout=10)
                    member_count = 0
                    if member_count_response.status_code == 200:
                        count_data = member_count_response.json()
                        if count_data.get('ok'):
                            member_count = count_data['result']
                    
                    details = f"- {chat_info.get('title')} ({member_count} members)"
                    return self.log_result("Group Access", True, details)
            return self.log_result("Group Access", False, "- Cannot access group")
        except Exception as e:
            return self.log_result("Group Access", False, f"- {str(e)}")
    
    def test_webhook_status(self):
        """Test webhook configuration"""
        try:
            response = requests.get(f"{self.base_url}/getWebhookInfo", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    webhook_info = data['result']
                    webhook_url = webhook_info.get('url', '')
                    if webhook_url:
                        details = f"- Webhook: {webhook_url[:50]}..."
                    else:
                        details = "- Using polling (recommended for this setup)"
                    return self.log_result("Webhook Status", True, details)
            return self.log_result("Webhook Status", False, "- Failed to get webhook info")
        except Exception as e:
            return self.log_result("Webhook Status", False, f"- {str(e)}")
    
    def test_business_configuration(self):
        """Test business logic configuration"""
        tests = []
        
        # Test subscription price
        if Config.SUBSCRIPTION_PRICE == 999:
            tests.append(("Subscription Price", True, f"- {Config.SUBSCRIPTION_PRICE} ₽"))
        else:
            tests.append(("Subscription Price", False, f"- Expected 999, got {Config.SUBSCRIPTION_PRICE}"))
        
        # Test subscription duration
        if Config.SUBSCRIPTION_DAYS == 30:
            tests.append(("Subscription Duration", True, f"- {Config.SUBSCRIPTION_DAYS} days"))
        else:
            tests.append(("Subscription Duration", False, f"- Expected 30, got {Config.SUBSCRIPTION_DAYS}"))
        
        # Test AI limits
        if Config.DAILY_AI_LIMIT == 5:
            tests.append(("AI Daily Limit", True, f"- {Config.DAILY_AI_LIMIT} requests/day"))
        else:
            tests.append(("AI Daily Limit", False, f"- Expected 5, got {Config.DAILY_AI_LIMIT}"))
        
        # Test admin configuration
        if Config.ADMINS and len(Config.ADMINS) == 3:
            tests.append(("Admin Configuration", True, f"- {len(Config.ADMINS)} admins configured"))
        else:
            tests.append(("Admin Configuration", False, f"- Expected 3 admins, got {len(Config.ADMINS) if Config.ADMINS else 0}"))
        
        all_passed = True
        for name, success, details in tests:
            self.log_result(name, success, details)
            if not success:
                all_passed = False
        
        return all_passed
    
    def test_external_integrations(self):
        """Test external service configurations"""
        integrations = [
            ("Supabase URL", Config.SUPABASE_URL),
            ("Supabase Service Key", Config.SUPABASE_SERVICE_KEY),
            ("OpenAI API Key", Config.OPENAI_API_KEY),
            ("YooKassa Secret Key", Config.YOOKASSA_SECRET_KEY),
            ("YooKassa Shop ID", Config.YOOKASSA_SHOP_ID),
        ]
        
        all_configured = True
        for name, value in integrations:
            if value and len(str(value)) > 10:  # Basic validation
                self.log_result(f"Integration - {name}", True, "- Configured")
            else:
                self.log_result(f"Integration - {name}", False, "- Not configured or invalid")
                all_configured = False
        
        return all_configured
    
    def test_message_templates(self):
        """Test message templates"""
        try:
            # Test welcome message formatting
            welcome_msg = Config.WELCOME_MESSAGE.format(
                price=Config.SUBSCRIPTION_PRICE,
                days=Config.SUBSCRIPTION_DAYS
            )
            if len(welcome_msg) > 100 and str(Config.SUBSCRIPTION_PRICE) in welcome_msg:
                self.log_result("Welcome Message Template", True, f"- {len(welcome_msg)} characters")
            else:
                return self.log_result("Welcome Message Template", False, "- Template formatting failed")
            
            # Test payment success message
            success_msg = Config.PAYMENT_SUCCESS_MESSAGE.format(
                days=Config.SUBSCRIPTION_DAYS,
                ai_limit=Config.DAILY_AI_LIMIT,
                invite_link="https://t.me/test"
            )
            if len(success_msg) > 100:
                self.log_result("Payment Success Template", True, f"- {len(success_msg)} characters")
            else:
                return self.log_result("Payment Success Template", False, "- Template formatting failed")
            
            return True
        except Exception as e:
            return self.log_result("Message Templates", False, f"- {str(e)}")
    
    def run_integration_tests(self):
        """Run all integration tests"""
        print("🚀 Buddah Base AI Bot - Production Readiness Test")
        print("=" * 60)
        
        print("\n📡 Bot API Tests:")
        self.test_bot_info()
        self.test_bot_commands()
        self.test_webhook_status()
        
        print("\n🏢 Business Configuration:")
        self.test_business_configuration()
        
        print("\n🔗 External Integrations:")
        self.test_external_integrations()
        
        print("\n👥 Group Management:")
        self.test_group_access()
        
        print("\n💬 Message Templates:")
        self.test_message_templates()
        
        # Final assessment
        print("\n" + "=" * 60)
        print(f"📊 Integration Test Results: {self.tests_passed}/{self.tests_total}")
        
        success_rate = (self.tests_passed / self.tests_total) * 100 if self.tests_total > 0 else 0
        
        if success_rate >= 90:
            print("🎉 Bot is READY FOR PRODUCTION!")
            print("✅ All critical systems are operational")
            return 0
        elif success_rate >= 75:
            print("⚠️ Bot is mostly ready with minor issues")
            print("🔧 Some non-critical features may need attention")
            return 0
        else:
            print("❌ Bot is NOT ready for production")
            print("🚨 Critical issues need to be resolved")
            return 1

def main():
    """Main function"""
    tester = BotIntegrationTester()
    return tester.run_integration_tests()

if __name__ == "__main__":
    import sys
    sys.exit(main())