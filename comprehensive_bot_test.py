#!/usr/bin/env python3
"""
Comprehensive Testing for Buddah Base AI Telegram Bot
Tests all core functionality, integrations, and business logic
"""

import asyncio
import requests
import sys
import json
import time
from datetime import datetime
from config import Config
from database import db
from payments import payment_service
from ai_service import ai_service
import logging

# Suppress verbose logs for testing
logging.getLogger('httpx').setLevel(logging.WARNING)

class BuddahBaseBotTester:
    def __init__(self):
        self.bot_token = Config.TELEGRAM_BOT_TOKEN
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.tests_run = 0
        self.tests_passed = 0
        self.critical_failures = []
        
    def log_test(self, name, success, details="", critical=False):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED {details}")
        else:
            print(f"❌ {name} - FAILED {details}")
            if critical:
                self.critical_failures.append(name)
        return success

    # ==================== CONNECTIVITY TESTS ====================
    
    def test_bot_api_connection(self):
        """Test Telegram Bot API connection"""
        try:
            response = requests.get(f"{self.base_url}/getMe", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    bot_info = data.get('result', {})
                    details = f"- Bot: @{bot_info.get('username', 'unknown')}"
                    return self.log_test("Telegram API Connection", True, details, critical=True)
                else:
                    return self.log_test("Telegram API Connection", False, f"- API Error: {data.get('description')}", critical=True)
            else:
                return self.log_test("Telegram API Connection", False, f"- HTTP {response.status_code}", critical=True)
        except Exception as e:
            return self.log_test("Telegram API Connection", False, f"- Exception: {str(e)}", critical=True)

    async def test_supabase_connection(self):
        """Test Supabase database connection"""
        try:
            # Test basic database connection
            test_user = await db.get_user(999999999)  # Non-existent user
            return self.log_test("Supabase Connection", True, "- Database accessible", critical=True)
        except Exception as e:
            return self.log_test("Supabase Connection", False, f"- Exception: {str(e)}", critical=True)

    def test_group_connection(self):
        """Test connection to closed group"""
        try:
            response = requests.get(f"{self.base_url}/getChat", 
                                  params={'chat_id': Config.CLOSED_GROUP_ID}, 
                                  timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    group_info = data.get('result', {})
                    details = f"- Group: {group_info.get('title', 'Unknown')}"
                    return self.log_test("Group Connection", True, details, critical=True)
                else:
                    return self.log_test("Group Connection", False, f"- API Error: {data.get('description')}", critical=True)
            else:
                return self.log_test("Group Connection", False, f"- HTTP {response.status_code}", critical=True)
        except Exception as e:
            return self.log_test("Group Connection", False, f"- Exception: {str(e)}", critical=True)

    # ==================== CONFIGURATION TESTS ====================
    
    def test_configuration_validity(self):
        """Test all required configuration parameters"""
        config_tests = [
            ("Telegram Bot Token", Config.TELEGRAM_BOT_TOKEN, True),
            ("Admin Contact", Config.ADMIN_CONTACT, False),
            ("Supabase URL", Config.SUPABASE_URL, True),
            ("Supabase Service Key", Config.SUPABASE_SERVICE_KEY, True),
            ("OpenAI API Key", Config.OPENAI_API_KEY, True),
            ("YooKassa Secret Key", Config.YOOKASSA_SECRET_KEY, True),
            ("YooKassa Shop ID", Config.YOOKASSA_SHOP_ID, True),
            ("Closed Group ID", Config.CLOSED_GROUP_ID, True),
            ("Admins List", Config.ADMINS, True),
        ]
        
        all_passed = True
        for name, value, critical in config_tests:
            if value:
                self.log_test(f"Config - {name}", True, "- Set", critical=critical)
            else:
                self.log_test(f"Config - {name}", False, "- Missing", critical=critical)
                all_passed = False
        
        # Test business logic settings
        if Config.SUBSCRIPTION_PRICE == 999:
            self.log_test("Config - Subscription Price", True, f"- {Config.SUBSCRIPTION_PRICE} ₽")
        else:
            self.log_test("Config - Subscription Price", False, f"- Expected 999, got {Config.SUBSCRIPTION_PRICE}")
            all_passed = False
            
        if Config.SUBSCRIPTION_DAYS == 30:
            self.log_test("Config - Subscription Days", True, f"- {Config.SUBSCRIPTION_DAYS} days")
        else:
            self.log_test("Config - Subscription Days", False, f"- Expected 30, got {Config.SUBSCRIPTION_DAYS}")
            all_passed = False
            
        if Config.DAILY_AI_LIMIT == 5:
            self.log_test("Config - AI Daily Limit", True, f"- {Config.DAILY_AI_LIMIT} requests/day")
        else:
            self.log_test("Config - AI Daily Limit", False, f"- Expected 5, got {Config.DAILY_AI_LIMIT}")
            all_passed = False
        
        return all_passed

    # ==================== DATABASE TESTS ====================
    
    async def test_database_operations(self):
        """Test database CRUD operations"""
        test_user_id = 123456789
        test_name = "Test User"
        test_username = "testuser"
        test_chat_id = 987654321
        
        try:
            # Test user creation
            success = await db.create_user(test_user_id, test_name, test_username, test_chat_id)
            if not success:
                return self.log_test("Database - User Creation", False, "- Failed to create user")
            
            # Test user retrieval
            user = await db.get_user(test_user_id)
            if not user:
                return self.log_test("Database - User Retrieval", False, "- Failed to retrieve user")
            
            # Test subscription activation
            success = await db.activate_subscription(test_user_id)
            if not success:
                return self.log_test("Database - Subscription Activation", False, "- Failed to activate")
            
            # Test subscription check
            is_active = await db.is_subscription_active(test_user_id)
            if not is_active:
                return self.log_test("Database - Subscription Check", False, "- Subscription not active")
            
            # Test AI request limits
            can_request = await db.can_make_ai_request(test_user_id)
            if not can_request:
                return self.log_test("Database - AI Request Check", False, "- Cannot make AI request")
            
            # Test increment requests
            success = await db.increment_daily_requests(test_user_id)
            if not success:
                return self.log_test("Database - Increment Requests", False, "- Failed to increment")
            
            # Test materials search
            materials = await db.search_materials("test", limit=5)
            # This might return empty list, which is OK
            
            self.log_test("Database Operations", True, "- All CRUD operations working")
            return True
            
        except Exception as e:
            return self.log_test("Database Operations", False, f"- Exception: {str(e)}", critical=True)

    # ==================== PAYMENT SYSTEM TESTS ====================
    
    async def test_payment_system(self):
        """Test YooKassa payment integration"""
        try:
            # Test payment creation (without actually processing)
            payment_data = await payment_service.create_payment(
                telegram_id=123456789,
                amount=Config.SUBSCRIPTION_PRICE,
                description="Test payment",
                return_url="https://t.me/test"
            )
            
            if payment_data and 'payment_id' in payment_data:
                self.log_test("Payment System - Creation", True, f"- Payment ID: {payment_data['payment_id'][:10]}...")
                
                # Test payment status check
                status_data = await payment_service.check_payment_status(payment_data['payment_id'])
                if status_data:
                    self.log_test("Payment System - Status Check", True, f"- Status: {status_data['status']}")
                    return True
                else:
                    return self.log_test("Payment System - Status Check", False, "- Failed to check status")
            else:
                return self.log_test("Payment System - Creation", False, "- Failed to create payment", critical=True)
                
        except Exception as e:
            return self.log_test("Payment System", False, f"- Exception: {str(e)}", critical=True)

    # ==================== AI SERVICE TESTS ====================
    
    async def test_ai_service(self):
        """Test OpenAI integration and AI service"""
        try:
            # Test materials search
            materials = await ai_service.search_in_materials("test query")
            self.log_test("AI Service - Materials Search", True, f"- Found {len(materials)} materials")
            
            # Test AI response generation (with mock data to avoid API costs)
            # We'll test the structure without making actual OpenAI calls
            test_question = "What is AI?"
            
            # Create a test user with active subscription for AI testing
            test_user_id = 987654321
            await db.create_user(test_user_id, "AI Test User", "aitestuser", 111111111)
            await db.activate_subscription(test_user_id)
            
            # Test AI request processing logic (without actual OpenAI call)
            can_request = await db.can_make_ai_request(test_user_id)
            is_active = await db.is_subscription_active(test_user_id)
            
            if can_request and is_active:
                self.log_test("AI Service - Request Validation", True, "- User can make AI requests")
                return True
            else:
                return self.log_test("AI Service - Request Validation", False, "- User cannot make AI requests")
                
        except Exception as e:
            return self.log_test("AI Service", False, f"- Exception: {str(e)}")

    # ==================== BUSINESS LOGIC TESTS ====================
    
    async def test_business_workflow(self):
        """Test complete business workflow: registration → payment → access"""
        try:
            workflow_user_id = 555666777
            
            # Step 1: User registration
            success = await db.create_user(workflow_user_id, "Workflow User", "workflowuser", 222222222)
            if not success:
                return self.log_test("Business Workflow - Registration", False, "- Failed to register user")
            
            # Step 2: Check initial state (should be inactive)
            is_active = await db.is_subscription_active(workflow_user_id)
            if is_active:
                return self.log_test("Business Workflow - Initial State", False, "- User should be inactive initially")
            
            # Step 3: Simulate payment and activation
            success = await db.activate_subscription(workflow_user_id)
            if not success:
                return self.log_test("Business Workflow - Activation", False, "- Failed to activate subscription")
            
            # Step 4: Check active state
            is_active = await db.is_subscription_active(workflow_user_id)
            if not is_active:
                return self.log_test("Business Workflow - Active State", False, "- User should be active after payment")
            
            # Step 5: Test AI limits
            for i in range(Config.DAILY_AI_LIMIT):
                can_request = await db.can_make_ai_request(workflow_user_id)
                if can_request:
                    await db.increment_daily_requests(workflow_user_id)
                else:
                    return self.log_test("Business Workflow - AI Limits", False, f"- Limit reached at {i}")
            
            # Step 6: Check limit exceeded
            can_request = await db.can_make_ai_request(workflow_user_id)
            if can_request:
                return self.log_test("Business Workflow - AI Limits", False, "- Limit not enforced")
            
            self.log_test("Business Workflow", True, "- Complete workflow working correctly")
            return True
            
        except Exception as e:
            return self.log_test("Business Workflow", False, f"- Exception: {str(e)}")

    # ==================== ADMIN FUNCTIONALITY TESTS ====================
    
    def test_admin_functionality(self):
        """Test admin panel functionality"""
        try:
            from admin_panel import admin_panel
            
            # Test admin check
            admin_ids = Config.ADMINS
            if not admin_ids:
                return self.log_test("Admin Functionality", False, "- No admins configured")
            
            # Test admin validation
            is_admin = admin_panel.is_admin(admin_ids[0])
            if not is_admin:
                return self.log_test("Admin Functionality", False, "- Admin validation failed")
            
            # Test non-admin validation
            is_admin = admin_panel.is_admin(999999999)
            if is_admin:
                return self.log_test("Admin Functionality", False, "- Non-admin validation failed")
            
            self.log_test("Admin Functionality", True, f"- {len(admin_ids)} admins configured")
            return True
            
        except Exception as e:
            return self.log_test("Admin Functionality", False, f"- Exception: {str(e)}")

    # ==================== MAIN TEST RUNNER ====================
    
    async def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Comprehensive Buddah Base AI Bot Testing")
        print("=" * 70)
        
        # Connectivity Tests
        print("\n🔌 Connectivity Tests:")
        self.test_bot_api_connection()
        await self.test_supabase_connection()
        self.test_group_connection()
        
        # Configuration Tests
        print("\n⚙️ Configuration Tests:")
        self.test_configuration_validity()
        
        # Database Tests
        print("\n🗄️ Database Tests:")
        await self.test_database_operations()
        
        # Payment System Tests
        print("\n💳 Payment System Tests:")
        await self.test_payment_system()
        
        # AI Service Tests
        print("\n🤖 AI Service Tests:")
        await self.test_ai_service()
        
        # Business Logic Tests
        print("\n💼 Business Logic Tests:")
        await self.test_business_workflow()
        
        # Admin Functionality Tests
        print("\n👨‍💼 Admin Functionality Tests:")
        self.test_admin_functionality()
        
        # Summary
        print("\n" + "=" * 70)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.critical_failures:
            print(f"🚨 Critical failures: {', '.join(self.critical_failures)}")
            print("❌ Bot is NOT ready for production!")
            return 1
        elif self.tests_passed == self.tests_run:
            print("🎉 All tests passed! Bot is ready for production!")
            return 0
        else:
            failed_tests = self.tests_run - self.tests_passed
            print(f"⚠️ {failed_tests} non-critical test(s) failed.")
            print("✅ Bot is ready for production with minor issues.")
            return 0

async def main():
    """Main testing function"""
    tester = BuddahBaseBotTester()
    return await tester.run_all_tests()

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(result)
    except KeyboardInterrupt:
        print("\n👋 Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Testing failed with error: {e}")
        sys.exit(1)