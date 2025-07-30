#!/usr/bin/env python3
"""
Запуск бота в production режиме
"""

import subprocess
import sys
import logging
import signal
import time
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BotRunner:
    def __init__(self):
        self.process = None
        self.running = False
    
    def signal_handler(self, signum, frame):
        """Обработчик сигналов для graceful shutdown"""
        if self.process:
            logger.info("🛑 Останавливаем бота...")
            self.process.terminate()
            self.running = False
    
    def run(self):
        """Запуск бота с автоматическим перезапуском"""
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        self.running = True
        restart_count = 0
        max_restarts = 5
        
        while self.running and restart_count < max_restarts:
            try:
                logger.info(f"🚀 Запуск бота (попытка {restart_count + 1})")
                
                self.process = subprocess.Popen([
                    sys.executable, "bot.py"
                ], cwd=Path(__file__).parent)
                
                # Ожидаем завершения процесса
                return_code = self.process.wait()
                
                if return_code != 0 and self.running:
                    restart_count += 1
                    logger.warning(f"⚠️ Бот завершился с кодом {return_code}. Перезапуск через 5 сек...")
                    time.sleep(5)
                else:
                    logger.info("✅ Бот завершен успешно")
                    break
                    
            except Exception as e:
                logger.error(f"❌ Ошибка запуска: {e}")
                restart_count += 1
                if restart_count < max_restarts:
                    logger.info("🔄 Перезапуск через 10 секунд...")
                    time.sleep(10)
        
        if restart_count >= max_restarts:
            logger.error(f"💥 Превышено максимальное количество перезапусков ({max_restarts})")

if __name__ == "__main__":
    runner = BotRunner()
    runner.run()