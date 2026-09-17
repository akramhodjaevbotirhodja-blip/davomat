"""Aylanuvchi (rotating) QR token.

QR kod har 30 soniyada yangilanadi. Token vaqt oynasidan HMAC bilan
hosil qilinadi, ya'ni ekrandagi QR rasmga olib yuborilsa ham bir daqiqadan
keyin ishlamaydi. Bazada hech narsa saqlanmaydi — faqat maxfiy kalit.
"""
import hashlib
import hmac
import time

from .config import QR_ROTATE_SECONDS, QR_GRACE_WINDOWS


def current_window(now: float | None = None) -> int:
    return int((now if now is not None else time.time()) // QR_ROTATE_SECONDS)


def make_token(secret: str, window: int | None = None) -> str:
    win = current_window() if window is None else window
    digest = hmac.new(secret.encode(), str(win).encode(), hashlib.sha256).digest()
    return digest.hex()[:20]


def verify_token(secret: str, token: str) -> bool:
    """Joriy oyna va undan oldingi bir nechta oyna uchun tekshiradi."""
    if not token:
        return False
    win = current_window()
    for back in range(QR_GRACE_WINDOWS + 1):
        if hmac.compare_digest(make_token(secret, win - back), token):
            return True
    return False


def seconds_left(now: float | None = None) -> int:
    t = now if now is not None else time.time()
    return QR_ROTATE_SECONDS - int(t % QR_ROTATE_SECONDS)
