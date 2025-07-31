#!/usr/bin/env python3
"""
Test inline queries functionality for files support
"""

import asyncio
import sys
from unittest.mock import Mock, AsyncMock
from config import Config
from handlers import BotHandlers
from messages import BotMessages
from telegram import Update, InlineQuery, User
from telegram.ext import ContextTypes

class InlineQueryTester:
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

    def create_mock_inline_query(self, query_text, user_id=12345):
        """Create a mock inline query for testing"""
        # Create mock user
        user = Mock(spec=User)
        user.id = user_id
        user.first_name = "TestUser"
        user.username = "testuser"
        
        # Create mock inline query
        inline_query = Mock(spec=InlineQuery)
        inline_query.query = query_text
        inline_query.from_user = user
        inline_query.answer = AsyncMock()
        
        # Create mock update
        update = Mock(spec=Update)
        update.inline_query = inline_query
        
        return update

    async def test_files_inline_queries(self):
        """Test inline queries for files-related searches"""
        print("\n🔍 Testing Files Inline Queries...")
        
        files_queries = [
            "файл",
            "дайте",
            "скинь",
            "промпт",
            "материалы"
        ]
        
        all_passed = True
        for query in files_queries:
            update = self.create_mock_inline_query(query)
            context = Mock(spec=ContextTypes.DEFAULT_TYPE)
            
            await BotHandlers.handle_inline_query(update, context)
            
            # Check if answer was called
            if update.inline_query.answer.called:
                # Get the results that were passed to answer
                call_args = update.inline_query.answer.call_args
                results = call_args[0][0]  # First positional argument
                
                # Check if files result is present
                files_result_found = False
                for result in results:
                    if hasattr(result, 'id') and result.id == "files_request":
                        files_result_found = True
                        break
                
                if files_result_found:
                    self.log_test(f"Files Inline Query: '{query}'", True, "- Files result included")
                else:
                    self.log_test(f"Files Inline Query: '{query}'", False, "- Files result not found")
                    all_passed = False
            else:
                self.log_test(f"Files Inline Query: '{query}'", False, "- No answer provided")
                all_passed = False
        
        return all_passed

    async def test_join_inline_queries(self):
        """Test inline queries for join-related searches"""
        print("\n💎 Testing Join Inline Queries...")
        
        join_queries = [
            "вступить",
            "доступ",
            ""  # Empty query should show join info
        ]
        
        all_passed = True
        for query in join_queries:
            update = self.create_mock_inline_query(query)
            context = Mock(spec=ContextTypes.DEFAULT_TYPE)
            
            await BotHandlers.handle_inline_query(update, context)
            
            if update.inline_query.answer.called:
                call_args = update.inline_query.answer.call_args
                results = call_args[0][0]
                
                # Check if join result is present
                join_result_found = False
                for result in results:
                    if hasattr(result, 'id') and result.id == "join_info":
                        join_result_found = True
                        break
                
                if join_result_found:
                    self.log_test(f"Join Inline Query: '{query or 'empty'}'", True, "- Join result included")
                else:
                    self.log_test(f"Join Inline Query: '{query or 'empty'}'", False, "- Join result not found")
                    all_passed = False
            else:
                self.log_test(f"Join Inline Query: '{query or 'empty'}'", False, "- No answer provided")
                all_passed = False
        
        return all_passed

    async def test_engagement_inline_queries(self):
        """Test inline queries for engagement-related searches"""
        print("\n🔥 Testing Engagement Inline Queries...")
        
        engagement_queries = [
            "интересн",
            "круто", 
            "veo"
        ]
        
        all_passed = True
        for query in engagement_queries:
            update = self.create_mock_inline_query(query)
            context = Mock(spec=ContextTypes.DEFAULT_TYPE)
            
            await BotHandlers.handle_inline_query(update, context)
            
            if update.inline_query.answer.called:
                call_args = update.inline_query.answer.call_args
                results = call_args[0][0]
                
                # Check if engagement result is present
                engagement_result_found = False
                for result in results:
                    if hasattr(result, 'id') and result.id == "engagement":
                        engagement_result_found = True
                        break
                
                if engagement_result_found:
                    self.log_test(f"Engagement Inline Query: '{query}'", True, "- Engagement result included")
                else:
                    self.log_test(f"Engagement Inline Query: '{query}'", False, "- Engagement result not found")
                    all_passed = False
            else:
                self.log_test(f"Engagement Inline Query: '{query}'", False, "- No answer provided")
                all_passed = False
        
        return all_passed

    async def test_inline_results_content(self):
        """Test that inline results contain correct content"""
        print("\n📋 Testing Inline Results Content...")
        
        # Test files inline result
        update = self.create_mock_inline_query("файл")
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        
        await BotHandlers.handle_inline_query(update, context)
        
        if update.inline_query.answer.called:
            call_args = update.inline_query.answer.call_args
            results = call_args[0][0]
            
            files_result = None
            for result in results:
                if hasattr(result, 'id') and result.id == "files_request":
                    files_result = result
                    break
            
            if files_result:
                # Check title
                if "📁 Хочешь файлы и промпты?" in files_result.title:
                    self.log_test("Files Inline Title", True, "- Correct title")
                else:
                    self.log_test("Files Inline Title", False, f"- Wrong title: {files_result.title}")
                
                # Check description
                if "2000+ промптов" in files_result.description:
                    self.log_test("Files Inline Description", True, "- Correct description")
                else:
                    self.log_test("Files Inline Description", False, f"- Wrong description: {files_result.description}")
                
                # Check message content
                message_content = files_result.input_message_content.message_text
                if "📁 Хочешь получить файлы" in message_content:
                    self.log_test("Files Inline Message", True, "- Correct message content")
                else:
                    self.log_test("Files Inline Message", False, "- Wrong message content")
            else:
                self.log_test("Files Inline Result", False, "- Files result not found")
        else:
            self.log_test("Files Inline Query", False, "- No answer provided")

    async def run_all_tests(self):
        """Run all inline query tests"""
        print("🚀 Starting Inline Query Testing")
        print("=" * 50)
        
        await self.test_files_inline_queries()
        await self.test_join_inline_queries()
        await self.test_engagement_inline_queries()
        await self.test_inline_results_content()
        
        # Summary
        print("\n" + "=" * 50)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All inline query tests passed!")
            print("✅ Files inline queries work correctly")
            print("✅ Join inline queries work correctly")
            print("✅ Engagement inline queries work correctly")
            print("✅ Inline result content is correct")
            return 0
        else:
            failed_tests = self.tests_run - self.tests_passed
            print(f"⚠️ {failed_tests} test(s) failed. Please review the issues above.")
            return 1

async def main():
    """Main testing function"""
    tester = InlineQueryTester()
    return await tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))