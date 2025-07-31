#!/usr/bin/env python3
"""
Тест логики одноразовых ссылок-приглашений
"""

import asyncio
from datetime import datetime, timedelta
from group_manager import GroupManager
from telegram import Bot
from config import Config

async def test_invite_link_logic():
    """Тестирование создания одноразовых ссылок"""
    print("🔗 Тестирование логики одноразовых ссылок...")
    print("=" * 50)
    
    # Создаем бота для тестирования
    bot = Bot(token=Config.TELEGRAM_BOT_TOKEN)
    group_manager = GroupManager(bot)
    
    print(f"🎯 Настройки:")
    print(f"   • Группа: {Config.CLOSED_GROUP_ID}")
    print(f"   • Срок действия: 1 час")
    print(f"   • Лимит использований: 1 раз")
    
    try:
        # Тестируем создание ссылки
        print(f"\n🔄 Создаем одноразовую ссылку...")
        invite_link = await group_manager.create_invite_link(expire_hours=1, member_limit=1)
        
        if invite_link:
            print(f"✅ Ссылка создана успешно!")
            print(f"🔗 URL: {invite_link}")
            
            # Рассчитываем время истечения
            expire_time = datetime.now() + timedelta(hours=1)
            print(f"⏰ Истекает: {expire_time.strftime('%d.%m.%Y %H:%M:%S')}")
            print(f"👤 Лимит использований: 1 человек")
            
            print(f"\n📝 Сообщение пользователю:")
            success_message = Config.PAYMENT_SUCCESS_MESSAGE.format(
                days=Config.SUBSCRIPTION_DAYS,
                ai_limit=Config.DAILY_AI_LIMIT,
                invite_link=invite_link
            )
            print(success_message)
            
        else:
            print(f"❌ Ошибка создания ссылки")
            
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
    
    print(f"\n" + "="*50)
    print(f"🎉 Тест завершен!")

async def main():
    """Главная функция"""
    print("🚀 Тестирование одноразовых ссылок Buddah Base AI")
    await test_invite_link_logic()

if __name__ == "__main__":
    asyncio.run(main())