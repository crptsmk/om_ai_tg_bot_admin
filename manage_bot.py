#!/usr/bin/env python3
"""
Управление ботом - старт, стоп, статус, перезапуск
"""

import subprocess
import sys
import time
import signal
import psutil
from pathlib import Path

class BotManager:
    def __init__(self):
        self.bot_script = "bot.py"
        self.log_file = "bot.log"
    
    def get_bot_process(self):
        """Найти процесс бота"""
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if 'python' in proc.info['name'] and any('bot.py' in cmd for cmd in proc.info['cmdline']):
                    return proc
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return None
    
    def start_bot(self):
        """Запуск бота"""
        if self.get_bot_process():
            print("⚠️ Бот уже запущен!")
            return False
        
        print("🚀 Запускаем бота...")
        subprocess.Popen([
            sys.executable, self.bot_script
        ], stdout=open(self.log_file, 'w'), stderr=subprocess.STDOUT)
        
        time.sleep(2)
        
        if self.get_bot_process():
            print("✅ Бот успешно запущен!")
            return True
        else:
            print("❌ Ошибка запуска бота")
            return False
    
    def stop_bot(self):
        """Остановка бота"""
        proc = self.get_bot_process()
        if not proc:
            print("⚠️ Бот не запущен")
            return False
        
        print("🛑 Останавливаем бота...")
        try:
            proc.terminate()
            proc.wait(timeout=10)
            print("✅ Бот остановлен")
            return True
        except psutil.TimeoutExpired:
            print("⚡ Принудительная остановка...")
            proc.kill()
            print("✅ Бот принудительно остановлен")
            return True
        except Exception as e:
            print(f"❌ Ошибка остановки: {e}")
            return False
    
    def restart_bot(self):
        """Перезапуск бота"""
        print("🔄 Перезапускаем бота...")
        self.stop_bot()
        time.sleep(1)
        return self.start_bot()
    
    def status(self):
        """Статус бота"""
        proc = self.get_bot_process()
        if proc:
            print(f"✅ Бот запущен (PID: {proc.pid})")
            print(f"📊 Использование CPU: {proc.cpu_percent():.1f}%")
            print(f"💾 Использование памяти: {proc.memory_info().rss / 1024 / 1024:.1f} MB")
            
            # Показать последние логи
            if Path(self.log_file).exists():
                print("\n📋 Последние логи:")
                try:
                    with open(self.log_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        for line in lines[-5:]:
                            print(f"   {line.strip()}")
                except Exception as e:
                    print(f"   ❌ Ошибка чтения логов: {e}")
            
            return True
        else:
            print("❌ Бот не запущен")
            return False
    
    def logs(self, lines=20):
        """Показать логи"""
        if not Path(self.log_file).exists():
            print("❌ Файл логов не найден")
            return
        
        print(f"📋 Последние {lines} строк логов:")
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                log_lines = f.readlines()
                for line in log_lines[-lines:]:
                    print(line.rstrip())
        except Exception as e:
            print(f"❌ Ошибка чтения логов: {e}")

def main():
    if len(sys.argv) < 2:
        print("🤖 Buddah Base Bot Manager")
        print("\nКоманды:")
        print("  start    - Запуск бота")
        print("  stop     - Остановка бота")
        print("  restart  - Перезапуск бота")
        print("  status   - Статус бота")
        print("  logs     - Показать логи")
        print("\nПример: python manage_bot.py start")
        return
    
    manager = BotManager()
    command = sys.argv[1].lower()
    
    if command == "start":
        manager.start_bot()
    elif command == "stop":
        manager.stop_bot()
    elif command == "restart":
        manager.restart_bot()
    elif command == "status":
        manager.status()
    elif command == "logs":
        lines = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        manager.logs(lines)
    else:
        print(f"❌ Неизвестная команда: {command}")

if __name__ == "__main__":
    main()