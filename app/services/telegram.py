import httpx

from app.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"


def send_message(text: str, parse_mode: str = "HTML") -> bool:
    """Send message to Telegram channel"""
    try:
        response = httpx.post(
            f"{BASE_URL}/sendMessage",
            json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": text,
                "parse_mode": parse_mode,
            },
        )
        return response.status_code == 200
    except Exception:
        return False


def send_listing_notification(item: dict) -> bool:
    """Send notification for a new listing"""
    title = item.get("title", "Sin título")
    price = item.get("price", "?")
    city = item.get("location", {}).get("city", "")
    rooms = item.get("type_attributes", {}).get("rooms", "?")
    surface = item.get("type_attributes", {}).get("surface", "?")
    slug = item.get("web_slug", "")
    url = f"https://es.wallapop.com/item/{slug}"

    message = (
        f"🏠 <b>New listing!</b>\n\n"
        f"<b>{title}</b>\n"
        f"💰 {price}€\n"
        f"📍 {city}\n"
        f"🛏 {rooms} rooms | 📐 {surface}m²\n\n"
        f'<a href="{url}">View on Wallapop</a>'
    )

    return send_message(message)


def test_bot() -> dict:
    """Test bot connection and send hello message"""
    try:
        # Test getMe
        response = httpx.get(f"{BASE_URL}/getMe")
        if response.status_code != 200:
            return {"ok": False, "error": "Failed to connect to bot"}

        bot_info = response.json().get("result", {})

        # Send test message
        success = send_message("👋 Hello! BuscaPisos bot is working!")

        return {
            "ok": success,
            "bot_username": bot_info.get("username"),
            "chat_id": TELEGRAM_CHAT_ID,
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}
