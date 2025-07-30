#!/bin/bash
# Скрипт быстрого управления ботом

echo "🤖 Buddah Base Bot - Управление"
echo "================================"

# Проверяем статус
echo "📊 Текущий статус:"
python manage_bot.py status
echo ""

# Показываем доступные команды
echo "🔧 Доступные команды:"
echo "  python manage_bot.py start    - Запустить бота"
echo "  python manage_bot.py stop     - Остановить бота" 
echo "  python manage_bot.py restart  - Перезапустить бота"
echo "  python manage_bot.py status   - Проверить статус"
echo "  python manage_bot.py logs     - Посмотреть логи"
echo ""

echo "📱 Бот в Telegram: @Saint_buddah_bot"
echo "🔗 Ссылка: https://t.me/Saint_buddah_bot"
echo ""

echo "✅ Бот работает и готов к использованию!"