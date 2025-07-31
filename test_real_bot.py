#!/usr/bin/env python3
"""
Тестирование бота через приватные сообщения
"""

import requests
import time
import json
from config import Config

def send_test_message(text):
    """Отправить тестовое сообщение боту"""
    # Для тестирования нужно знать chat_id
    # Обычно это делается через /start в приватных сообщениях
    
    # Получаем последние обновления
    url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/getUpdates"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Получены обновления от Telegram API")
        
        if data.get('ok') and data.get('result'):
            updates = data['result']
            print(f"📊 Количество обновлений: {len(updates)}")
            
            for update in updates[-5:]:  # Последние 5 обновлений
                if 'message' in update:
                    msg = update['message']
                    chat = msg.get('chat', {})
                    user = msg.get('from', {})
                    text = msg.get('text', '')
                    
                    print(f"💬 Сообщение от {user.get('first_name', 'Unknown')}: {text[:50]}...")
                    print(f"   Chat Type: {chat.get('type')}, Chat ID: {chat.get('id')}")
        else:
            print("⚠️ Нет новых обновлений")
    else:
        print(f"❌ Ошибка API: {response.status_code}")

def check_bot_info():
    """Проверить информацию о боте"""
    url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/getMe"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('ok'):
            bot_info = data['result']
            print(f"🤖 Бот: @{bot_info.get('username')}")
            print(f"📛 Имя: {bot_info.get('first_name')}")
            print(f"🔍 Может читать группы: {bot_info.get('can_read_all_group_messages')}")
            print(f"👥 Может вступать в группы: {bot_info.get('can_join_groups')}")
            return True
    return False

if __name__ == "__main__":
    print("🧪 Тестирование Telegram бота...")
    print("=" * 40)
    
    # Проверяем информацию о боте
    if check_bot_info():
        print("\n📡 Проверяем последние обновления...")
        send_test_message("тест")
        
        print(f"\n✅ Тестирование завершено!")
        print(f"💡 Для тестирования:")
        print(f"   1. Найдите бота: @Saint_buddah_bot")
        print(f"   2. Напишите ему: /start")
        print(f"   3. Попробуйте: 'как вступить?'")
        print(f"   4. Или: 'интересно'")
    else:
        print("❌ Не удалось получить информацию о боте")