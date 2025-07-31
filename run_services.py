#!/usr/bin/env python3
"""
Запуск всех сервисов Buddah Base AI
"""

import subprocess
import sys
import signal
import time
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ServiceManager:
    def __init__(self):
        self.processes = {}
        self.running = True
    
    def signal_handler(self, signum, frame):
        """Обработчик сигналов для graceful shutdown"""
        logger.info("🛑 Получен сигнал остановки, завершаем сервисы...")
        self.running = False
        self.stop_all_services()
    
    def start_bot(self):
        """Запуск основного бота"""
        try:
            logger.info("🤖 Запускаем Telegram бота...")
            proc = subprocess.Popen([
                sys.executable, "bot.py"
            ], cwd=Path(__file__).parent)
            
            self.processes['bot'] = proc
            logger.info(f"✅ Бот запущен (PID: {proc.pid})")
            return proc
        except Exception as e:
            logger.error(f"❌ Ошибка запуска бота: {e}")
            return None
    
    def start_webhook_server(self):
        """Запуск webhook сервера"""
        try:
            logger.info("🌐 Запускаем webhook сервер...")
            proc = subprocess.Popen([
                sys.executable, "webhook_server.py"
            ], cwd=Path(__file__).parent)
            
            self.processes['webhook'] = proc
            logger.info(f"✅ Webhook сервер запущен (PID: {proc.pid})")
            return proc
        except Exception as e:
            logger.error(f"❌ Ошибка запуска webhook сервера: {e}")
            return None
    
    def start_scheduler(self):
        """Запуск планировщика задач"""
        try:
            logger.info("🕐 Запускаем планировщик задач...")
            proc = subprocess.Popen([
                sys.executable, "-c", "from utils import run_scheduler; run_scheduler()"
            ], cwd=Path(__file__).parent)
            
            self.processes['scheduler'] = proc
            logger.info(f"✅ Планировщик запущен (PID: {proc.pid})")
            return proc
        except Exception as e:
            logger.error(f"❌ Ошибка запуска планировщика: {e}")
            return None
    
    def check_services(self):
        """Проверка состояния сервисов"""
        for name, proc in list(self.processes.items()):
            if proc.poll() is not None:
                logger.warning(f"⚠️ Сервис {name} завершился (код: {proc.returncode})")
                
                # Перезапускаем сервис
                if self.running:
                    logger.info(f"🔄 Перезапускаем {name}...")
                    if name == 'bot':
                        new_proc = self.start_bot()
                    elif name == 'webhook':
                        new_proc = self.start_webhook_server()
                    elif name == 'scheduler':
                        new_proc = self.start_scheduler()
                    
                    if new_proc:
                        self.processes[name] = new_proc
                    else:
                        del self.processes[name]
    
    def stop_all_services(self):
        """Остановка всех сервисов"""
        for name, proc in self.processes.items():
            try:
                logger.info(f"🛑 Останавливаем {name}...")
                proc.terminate()
                
                # Ждем завершения
                try:
                    proc.wait(timeout=10)
                    logger.info(f"✅ {name} остановлен")
                except subprocess.TimeoutExpired:
                    logger.warning(f"⚡ Принудительная остановка {name}...")
                    proc.kill()
                    proc.wait()
            except Exception as e:
                logger.error(f"❌ Ошибка остановки {name}: {e}")
        
        self.processes.clear()
    
    def run(self):
        """Главный цикл менеджера сервисов"""
        # Настраиваем обработчики сигналов
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        logger.info("🚀 Запускаем все сервисы Buddah Base AI...")
        
        # Запускаем сервисы
        self.start_bot()
        time.sleep(2)  # Даем боту время запуститься
        
        self.start_webhook_server()
        time.sleep(1)
        
        self.start_scheduler()
        
        logger.info("✅ Все сервисы запущены!")
        logger.info("📊 Состояние сервисов:")
        for name, proc in self.processes.items():
            logger.info(f"   • {name}: PID {proc.pid}")
        
        # Главный цикл мониторинга
        while self.running:
            try:
                self.check_services()
                time.sleep(30)  # Проверяем каждые 30 секунд
            except KeyboardInterrupt:
                break
        
        logger.info("👋 Завершение работы менеджера сервисов")

def main():
    """Главная функция"""
    manager = ServiceManager()
    
    try:
        manager.run()
    except KeyboardInterrupt:
        logger.info("👋 Получен Ctrl+C, завершаем работу...")
    finally:
        manager.stop_all_services()

if __name__ == "__main__":
    main()