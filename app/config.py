import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Database
DATABASE_URL = os.getenv("DATABASE_URL")

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Notification settings
NOTIFICATION_MAX_PRICE = 700

# Base coordinates
BASE_LAT = 42.2313601
BASE_LON = -8.7124252

# Search parameters
BASE_PARAMS = {
    "category_id": "200",
    "distance_in_km": "40",
    "operation": "rent",
    "order_by": "price_low_to_high",
    "source": "side_bar_filters",
    "rooms": "2",
    "min_sale_price": "100",
    "latitude": str(BASE_LAT),
    "longitude": str(BASE_LON),
}

PROPERTY_TYPES = ["apartment", "house"]
MIN_PRICE = 300

TEMPORARY_RENTAL_KEYWORDS = [
    "vacacional",
    "vacaciones",
    "temporada",
    "escolar",
    "enero",
    "febrero",
    "marzo",
    "abril",
    "mayo",
    "junio",
    "julio",
    "agosto",
    "septiembre",
    "octubre",
    "noviembre",
    "diciembre",
    "estancia mínima",
    "minimo",
    "mínimo",
    "noches",
]

# Paths
DATA_DIR = Path(__file__).parent.parent
STATICS_DIR = DATA_DIR / "statics"
