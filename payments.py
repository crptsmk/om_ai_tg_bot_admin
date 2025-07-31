import logging
import uuid
from typing import Optional, Dict, Any
from yookassa import Configuration, Payment
from config import Config

logger = logging.getLogger(__name__)

class PaymentService:
    def __init__(self):
        Configuration.account_id = Config.YOOKASSA_SHOP_ID
        Configuration.secret_key = Config.YOOKASSA_SECRET_KEY
    
    async def create_payment(self, telegram_id: int, amount: int, description: str, 
                           return_url: str = None, promo_code: str = None) -> Optional[Dict[str, Any]]:
        """Создать платеж в YooKassa"""
        try:
            # Применяем промокод если есть
            final_amount = amount
            if promo_code:
                # Здесь должна быть логика применения промокода
                # Пока заглушка
                pass
            
            payment_data = {
                "amount": {
                    "value": f"{final_amount}",
                    "currency": Config.SUBSCRIPTION_CURRENCY
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": return_url or f"https://t.me/{Config.ADMIN_CONTACT}"
                },
                "capture": True,
                "description": description,
                "metadata": {
                    "telegram_id": str(telegram_id),
                    "promo_code": promo_code or ""
                }
            }
            
            payment = Payment.create(payment_data)
            
            if payment.status == 'pending':
                logger.info(f"Payment created for user {telegram_id}: {payment.id}")
                return {
                    'payment_id': payment.id,
                    'payment_url': payment.confirmation.confirmation_url,
                    'amount': final_amount,
                    'status': payment.status
                }
            else:
                logger.error(f"Payment creation failed for user {telegram_id}: {payment.status}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating payment for user {telegram_id}: {e}")
            return None
    
    async def check_payment_status(self, payment_id: str) -> Optional[Dict[str, Any]]:
        """Проверить статус платежа"""
        try:
            payment = Payment.find_one(payment_id)
            
            return {
                'payment_id': payment.id,
                'status': payment.status,
                'amount': payment.amount.value,
                'currency': payment.amount.currency,
                'metadata': payment.metadata
            }
        except Exception as e:
            logger.error(f"Error checking payment {payment_id}: {e}")
            return None
    
    async def process_successful_payment(self, payment_id: str) -> Optional[int]:
        """Обработать успешный платеж"""
        try:
            payment_info = await self.check_payment_status(payment_id)
            
            if payment_info and payment_info['status'] == 'succeeded':
                telegram_id = int(payment_info['metadata'].get('telegram_id', 0))
                if telegram_id:
                    logger.info(f"Processing successful payment for user {telegram_id}")
                    return telegram_id
            
            return None
        except Exception as e:
            logger.error(f"Error processing payment {payment_id}: {e}")
            return None

# Глобальный экземпляр сервиса платежей
payment_service = PaymentService()