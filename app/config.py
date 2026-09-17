"""Sozlamalar va umumiy konstantalar."""
import os
from datetime import timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "davomat.db"

try:
    TZ = ZoneInfo("Asia/Tashkent")
except ZoneInfoNotFoundError:
    # `tzdata` o'rnatilmagan tizimlarda (odatda Windows) — sobit UTC+5
    TZ = timezone(timedelta(hours=5), "Asia/Tashkent")

# QR kod necha soniyada yangilanadi
QR_ROTATE_SECONDS = 30
# Skanerlangan QR necha soniya amal qiladi (sekin skanerlaganlar uchun zaxira)
QR_GRACE_WINDOWS = 2

# Proyektor sahifasi bir so'rovda shuncha oldinga tayyorlangan QR oladi.
# Bu serverga murojaatni kamaytiradi (Vercel'da har so'rov pul/limit).
QR_SLOTS_AHEAD = 4

DEFAULT_SETTINGS = {
    "company_name": "Kompaniya",
    # 1-smena (kunduzgi)
    "shift1_name": "1-smena",
    "shift1_start": "09:00",
    "shift1_end": "18:00",
    # 2-smena (kechki) — tugashi yarim tundan o'tishi mumkin
    "shift2_name": "2-smena",
    "shift2_start": "18:00",
    "shift2_end": "03:00",
    "shift2_enabled": "1",
    # Erkin jadval — belgilangan kelish vaqti yo'q (masalan talabalar)
    "flex_name": "Erkin jadval",
    "late_grace_minutes": "5",
    "min_shift_minutes": "60",       # kelgandan keyin kamida shuncha vaqt o'tsa ketish yoziladi
    "device_limit_per_hour": "3",    # bitta telefondan 1 soatda nechta odam belgilanishi mumkin
    "admin_password": os.environ.get("ADMIN_PASSWORD", "admin"),
    # Joylashuv tekshiruvi (internetga chiqarilganda muhim)
    "geo_required": "0",             # 1 bo'lsa GPS majburiy
    "office_lat": "",
    "office_lng": "",
    "geo_radius_m": "200",           # ofis markazidan ruxsat etilgan masofa, metrda
}

STATUS_LABELS = {
    "keldi": "Keldi",
    "belgilanmagan": "—",
    "kechikdi": "Kechikdi",
    "kelmadi": "Kelmadi",
    "tatil": "Ta'til",
    "kasal": "Kasallik",
    "komandirovka": "Komandirovka",
    "sababli": "Sababli",
}

ABSENCE_TYPES = ["tatil", "kasal", "komandirovka", "sababli"]

WEEKDAYS_UZ = [
    "Dushanba", "Seshanba", "Chorshanba", "Payshanba",
    "Juma", "Shanba", "Yakshanba",
]

MONTHS_UZ = [
    "Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun",
    "Iyul", "Avgust", "Sentabr", "Oktabr", "Noyabr", "Dekabr",
]
