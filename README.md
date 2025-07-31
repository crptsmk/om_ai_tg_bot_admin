# 🤖 Buddah Base AI - Коммерческий Telegram Бот

## 📖 Описание

Полнофункциональный коммерческий Telegram бот для продажи подписок на закрытое AI-сообщество с интегрированными платежами, AI-консультантом и автоматическим управлением доступом.

## ✨ Основные функции

### 💳 **Прием платежей**
- Интеграция с YooKassa
- Цена: **999 ₽ на год** (365 дней)
- Автоматическая активация подписки
- Webhook: https://neomonkbot.onrender.com/webhook/yookassa-payment

### 🔐 **Управление доступом**
- Одноразовые invite-ссылки (1 час, 1 использование)
- Автоматическая проверка статуса подписки
- Исключение пользователей при истечении подписки

### 🤖 **AI-консультант**
- Интеграция с OpenAI GPT-4o-mini
- Лимит: 5 вопросов в день на пользователя
- Поиск в базе материалов перед генерацией ответа
- Автоматический сброс лимитов в 00:00 MSK

### 📚 **База материалов**
- Поиск по названию и тегам
- Команда `/materials [запрос]`
- Админские функции добавления материалов

### 🛡 **Автоматическая модерация (ОТКЛЮЧЕНА)**
- ~~Удаление сообщений не-админов в закрытых ветках~~
- ~~Защита главной ветки "Чат"~~
- Логирование всех действий (активно)
- **Модерация временно деактивирована**

### 🔧 **Админ-панель**
- Статистика пользователей и платежей
- Массовая рассылка сообщений
- Управление материалами
- Экспорт данных в CSV

## 🚀 Быстрый старт

### 1. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 2. Настройка переменных окружения

Скопируйте `.env.example` в `.env` и заполните своими данными:

```bash
cp .env.example .env
```

Затем отредактируйте `.env`:

```env
# Telegram
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
ADMIN_CONTACT=your_admin_username

# Supabase  
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your_supabase_service_key_here
SUPABASE_ANON_KEY=your_supabase_anon_key_here

# OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# YooKassa
YOOKASSA_SECRET_KEY=your_yookassa_secret_key_here
YOOKASSA_SHOP_ID=your_shop_id_here
YOOKASSA_WEBHOOK_URL=https://your-domain.com/webhook/yookassa-payment

# Группа и админы
CLOSED_GROUP_ID=-1001234567890
MAIN_TOPIC_ID=1
ADMINS=admin_id_1,admin_id_2,admin_id_3

# Подписка
SUBSCRIPTION_PRICE=999
SUBSCRIPTION_CURRENCY=RUB
SUBSCRIPTION_DAYS=365
```

### Где получить ключи:

#### Telegram Bot Token:
1. Найдите @BotFather в Telegram
2. Создайте нового бота командой `/newbot`
3. Скопируйте полученный токен

#### Supabase:
1. Создайте проект на [supabase.com](https://supabase.com)
2. В Settings → API найдите URL и ключи
3. Используйте `service_role` ключ для полного доступа

#### OpenAI API Key:
1. Зарегистрируйтесь на [platform.openai.com](https://platform.openai.com)
2. Создайте API ключ в разделе API Keys
3. Пополните баланс для использования

#### YooKassa:
1. Зарегистрируйтесь в [yookassa.ru](https://yookassa.ru)
2. Получите Shop ID и Secret Key
3. Настройте webhook URL для уведомлений

#### Group ID:
1. Добавьте бота в группу как администратора
2. Отправьте сообщение в группу
3. Используйте `/start` с ботом для получения chat_id

### 3. Запуск сервисов

**Основной бот:**
```bash
python bot.py
```

**Webhook сервер:**
```bash
python webhook_server.py
```

**Все сервисы:**
```bash
python run_services.py
```

## 📋 Команды бота

### Для пользователей:
- `/start` - Регистрация и информация о подписке  
- `/monk [вопрос]` - AI-консультант (5 вопросов/день)
- `/materials [запрос]` - Поиск в базе материалов
- `/status` - Статус подписки и лимитов

### Для администраторов:
- `/admin` - Панель управления ботом

## 🏗 Файловая структура

```
/app/
├── bot.py                    # Основной бот
├── webhook_server.py         # Webhook сервер для YooKassa
├── config.py                # Конфигурация
├── database.py              # Работа с Supabase  
├── payments.py              # Интеграция YooKassa
├── ai_service.py            # OpenAI интеграция
├── group_manager.py         # Управление группой
├── handlers.py              # Обработчики команд
├── callback_handlers.py     # Обработчики кнопок
├── admin_panel.py           # Админ функции
├── utils.py                 # Утилиты и cron задачи
├── run_services.py          # Запуск всех сервисов
├── test_commercial_bot.py   # Тестирование
├── quick_test.py            # Быстрая проверка
└── requirements.txt         # Зависимости
```

## 🗄 База данных Supabase

### Таблицы:
- `buddah_base_ai` - пользователи и подписки
- `materials` - база материалов для поиска  
- `promo_codes` - промокоды (готово к использованию)

## 🔧 Интеграции

- **YooKassa**: Прием платежей 999₽ на год
- **OpenAI**: GPT-4o-mini для AI-консультанта
- **Supabase**: База данных пользователей и материалов
- **Telegram**: Группа AI Base (-1002840812146)

## 📊 Особенности

### Одноразовые invite-ссылки:
- Срок: 1 час
- Лимит: 1 использование
- Автосоздание после оплаты

### Модерация:
- Удаление сообщений не-админов в закрытых ветках
- Защита главной ветки "Чат" (thread_id=None или 1)

### AI-лимиты:
- 5 запросов в день на пользователя
- Автосброс в 00:00 MSK
- Поиск в материалах перед генерацией

## 🔒 Безопасность

⚠️ **ВАЖНО**: Никогда не коммитьте файл `.env` с реальными ключами в публичный репозиторий!

- Используйте `.env.example` как шаблон
- Добавьте `.env` в `.gitignore` 
- Храните ключи в безопасном месте
- Используйте переменные окружения на продакшене

### Рекомендации:
- Регулярно обновляйте API ключи
- Используйте разные ключи для разработки и продакшена  
- Мониторьте использование API (особенно OpenAI)
- Настройте лимиты расходов в YooKassa и OpenAI

## 🧪 Тестирование

```bash
python quick_test.py           # Проверка конфигурации
python test_commercial_bot.py  # Полное тестирование  
python test_invite_links.py    # Тест invite-ссылок
```

## ✅ Готовность к продакшену

- ✅ Все интеграции настроены и протестированы
- ✅ Webhook URL добавлен: https://neomonkbot.onrender.com/webhook/yookassa-payment
- ✅ Одноразовые ссылки с ограничениями
- ✅ Правильная модерация группы
- ✅ Подписка на год за 999₽
- ✅ Админ-панель с полным функционалом

**Бот готов к коммерческому использованию! 🚀**