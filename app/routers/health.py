from datetime import datetime, timezone

from fastapi import APIRouter
from sqlalchemy import text

from app.db import SessionLocal
from app.services.telegram import test_bot

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check():
    """Health check for server and database"""
    timestamp = datetime.now(timezone.utc).isoformat()

    # Check database connection
    db_status = "error"
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {str(e)[:50]}"

    return {
        "status": "ok",
        "timestamp": timestamp,
        "database": db_status,
    }


@router.get("/health/telegram")
def telegram_health():
    """Test Telegram bot and send hello message"""
    return test_bot()
