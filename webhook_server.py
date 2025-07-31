#!/usr/bin/env python3
"""
Webhook сервер для обработки уведомлений от YooKassa
"""

import logging
import json
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from database import db
from payments import payment_service
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Buddah Base Webhook Server")

@app.post("/webhook/yookassa-payment")
async def yookassa_webhook(request: Request):
    """Обработчик webhook от YooKassa"""
    try:
        # Получаем данные запроса
        body = await request.body()
        data = json.loads(body)
        
        logger.info(f"Received YooKassa webhook: {data}")
        
        # Проверяем тип события
        if data.get('event') == 'payment.succeeded':
            payment_data = data.get('object', {})
            payment_id = payment_data.get('id')
            
            if payment_id:
                # Обрабатываем успешный платеж
                telegram_id = await payment_service.process_successful_payment(payment_id)
                
                if telegram_id:
                    # Активируем подписку
                    success = await db.activate_subscription(telegram_id)
                    
                    if success:
                        logger.info(f"Successfully activated subscription for user {telegram_id}")
                        return JSONResponse({"status": "ok"})
                    else:
                        logger.error(f"Failed to activate subscription for user {telegram_id}")
                        raise HTTPException(status_code=500, detail="Failed to activate subscription")
                else:
                    logger.error(f"Failed to process payment {payment_id}")
                    raise HTTPException(status_code=500, detail="Failed to process payment")
            else:
                logger.error("No payment_id in webhook data")
                raise HTTPException(status_code=400, detail="Invalid webhook data")
        
        return JSONResponse({"status": "ok"})
        
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Buddah Base Webhook Server"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Buddah Base Webhook Server is running"}

if __name__ == "__main__":
    uvicorn.run(
        "webhook_server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )