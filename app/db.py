"""Ma'lumotlar bazasi.

Ikki rejimda ishlaydi:
  * `DATABASE_URL` muhit o'zgaruvchisi bo'lsa — PostgreSQL (Neon, Vercel uchun)
  * bo'lmasa — lokal SQLite fayl (ofis kompyuteri uchun)

SQL matnlari ikkala bazaga ham mos yozilgan; farq faqat parametr belgisida
(`?` va `%s`) va jadval yaratish sintaksisida.
"""
import os
import secrets
import sqlite3
from contextlib import contextmanager
from datetime import datetime, date

from .config import DB_PATH, DATA_DIR, DEFAULT_SETTINGS, TZ

def _priority(name: str) -> int | None:
    """O'zgaruvchi nomi baza manzilini saqlashi mumkinmi va qay darajada mos?

    Vercel integratsiyalari nomlarga prefiks qo'shishi mumkin (masalan
    `CHECKIN_DATABASE_URL`), shuning uchun nomning oxiriga qaraymiz.
    Kichik raqam — yuqoriroq ustunlik.
    """
    n = name.upper()
    # Prisma varianti libpq tushunmaydigan parametrlar saqlaydi, NO_SSL esa xavfli
    if n.endswith(("POSTGRES_PRISMA_URL", "NO_SSL")):
        return None
    if n == "DATABASE_URL":
        return 0
    if n.endswith("_DATABASE_URL"):
        return 1
    if n == "POSTGRES_URL" or n.endswith("_POSTGRES_URL"):
        return 2
    # Ulanish hovuzisiz variantlar — faqat boshqasi topilmasa
    if n.endswith(("DATABASE_URL_UNPOOLED", "POSTGRES_URL_NON_POOLING")):
        return 3
    return None


def _is_pg_url(value: str) -> bool:
    return value.strip().startswith(("postgres://", "postgresql://"))


def _find_url() -> tuple[str, str]:
    """Muhit o'zgaruvchilaridan baza manzilini topadi: (nomi, qiymati)."""
    ranked = sorted(
        (p, name) for name in os.environ
        if (p := _priority(name)) is not None
    )
    for _, name in ranked:
        value = os.environ.get(name, "").strip()
        if _is_pg_url(value):
            return name, value
    return "", ""


URL_VAR_NAME, DATABASE_URL = _find_url()
IS_PG = bool(DATABASE_URL)


def db_env_report() -> list[tuple[str, bool, bool]]:
    """Tashxis uchun: (nom, tekshirildimi, yaroqli manzilmi). Qiymat chiqmaydi."""
    out = []
    for name in sorted(os.environ):
        if not any(w in name.upper() for w in ("POSTGRES", "DATABASE", "NEON", "PG")):
            continue
        considered = _priority(name) is not None
        valid = considered and _is_pg_url(os.environ.get(name, ""))
        out.append((name, considered, valid))
    return out

# --------------------------------------------------------------------------
# Jadvallar
# --------------------------------------------------------------------------

_PK = "INTEGER PRIMARY KEY AUTOINCREMENT" if not IS_PG else "SERIAL PRIMARY KEY"

SCHEMA = f"""
CREATE TABLE IF NOT EXISTS employees (
    id          {_PK},
    full_name   TEXT    NOT NULL,
    position    TEXT    DEFAULT '',
    department  TEXT    DEFAULT '',
    phone       TEXT    DEFAULT '',
    shift       INTEGER NOT NULL DEFAULT 1,
    rest_day    INTEGER,
    active      INTEGER NOT NULL DEFAULT 1,
    created_at  TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS attendance (
    id           {_PK},
    employee_id  INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    work_date    TEXT    NOT NULL,
    check_in     TEXT,
    check_out    TEXT,
    late_minutes INTEGER NOT NULL DEFAULT 0,
    status       TEXT    NOT NULL DEFAULT 'keldi',
    note         TEXT    DEFAULT '',
    device_id    TEXT    DEFAULT '',
    ip           TEXT    DEFAULT '',
    manual       INTEGER NOT NULL DEFAULT 0,
    flagged      INTEGER NOT NULL DEFAULT 0,
    UNIQUE (employee_id, work_date)
);

CREATE TABLE IF NOT EXISTS absences (
    id          {_PK},
    employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    date_from   TEXT    NOT NULL,
    date_to     TEXT    NOT NULL,
    kind        TEXT    NOT NULL,
    note        TEXT    DEFAULT '',
    created_at  TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS settings (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS audit (
    id          {_PK},
    ts          TEXT NOT NULL,
    employee_id INTEGER,
    action      TEXT NOT NULL,
    device_id   TEXT DEFAULT '',
    ip          TEXT DEFAULT '',
    user_agent  TEXT DEFAULT '',
    detail      TEXT DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_attendance_date ON attendance(work_date);
CREATE INDEX IF NOT EXISTS idx_absences_range  ON absences(date_from, date_to);
CREATE INDEX IF NOT EXISTS idx_audit_ts        ON audit(ts);
"""


# --------------------------------------------------------------------------
# Ulanish
# --------------------------------------------------------------------------

def _sql(query: str) -> str:
    """SQLite uslubidagi `?` belgilarini PostgreSQL uchun `%s` ga o'giradi."""
    return query.replace("?", "%s") if IS_PG else query


class Conn:
    """Ikkala baza ustidan bitta interfeys."""

    def __init__(self, raw):
        self.raw = raw

    def execute(self, query: str, params=()):
        return self.raw.execute(_sql(query), params)

    def executescript(self, script: str):
        if IS_PG:
            return self.raw.execute(script)
        return self.raw.executescript(script)

    def commit(self):
        self.raw.commit()

    def rollback(self):
        self.raw.rollback()

    def close(self):
        self.raw.close()


def connect() -> Conn:
    if IS_PG:
        import psycopg
        from psycopg.rows import dict_row
        raw = psycopg.connect(DATABASE_URL, row_factory=dict_row,
                              connect_timeout=10)
        return Conn(raw)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    raw = sqlite3.connect(DB_PATH, timeout=10)
    raw.row_factory = sqlite3.Row
    raw.execute("PRAGMA foreign_keys = ON")
    raw.execute("PRAGMA journal_mode = WAL")
    return Conn(raw)


_ready = False


def ensure_db() -> None:
    """Jadvallar mavjudligiga ishonch hosil qiladi (bir marta)."""
    global _ready
    if _ready:
        return
    init_db()
    _ready = True


@contextmanager
def db():
    ensure_db()
    conn = connect()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


MIGRATIONS = [
    ("employees", "shift", "INTEGER NOT NULL DEFAULT 1"),
    # Shaxsiy haftalik dam olish kuni (1=Dushanba ... 7=Yakshanba).
    # Bo'sh bo'lsa xodim umumiy ish kunlari jadvaliga bo'ysunadi.
    ("employees", "rest_day", "INTEGER"),
]


def _columns(conn: Conn, table: str) -> set[str]:
    if IS_PG:
        rows = conn.execute(
            "SELECT column_name FROM information_schema.columns WHERE table_name = ?",
            (table,),
        ).fetchall()
        return {r["column_name"] for r in rows}
    rows = conn.raw.execute(f"PRAGMA table_info({table})").fetchall()
    return {r["name"] for r in rows}


def _migrate(conn: Conn) -> None:
    """Eski bazalarga yangi ustunlarni qo'shadi (ma'lumot yo'qolmaydi)."""
    for table, column, definition in MIGRATIONS:
        if column not in _columns(conn, table):
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
            print(f"  baza yangilandi: {table}.{column} qo'shildi", flush=True)


def init_db() -> None:
    conn = connect()
    try:
        conn.executescript(SCHEMA)
        _migrate(conn)
        for key, value in DEFAULT_SETTINGS.items():
            conn.execute(
                "INSERT INTO settings (key, value) VALUES (?, ?)"
                " ON CONFLICT (key) DO NOTHING",
                (key, value),
            )
        # QR imzolash uchun maxfiy kalit — bir marta generatsiya qilinadi
        conn.execute(
            "INSERT INTO settings (key, value) VALUES ('qr_secret', ?)"
            " ON CONFLICT (key) DO NOTHING",
            (secrets.token_hex(32),),
        )
        conn.commit()
    finally:
        conn.close()


# --------------------------------------------------------------------------
# Sozlamalar
# --------------------------------------------------------------------------

def get_settings(conn: Conn) -> dict:
    rows = conn.execute("SELECT key, value FROM settings").fetchall()
    return {r["key"]: r["value"] for r in rows}


def set_setting(conn: Conn, key: str, value: str) -> None:
    conn.execute(
        "INSERT INTO settings (key, value) VALUES (?, ?)"
        " ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value",
        (key, value),
    )


# --------------------------------------------------------------------------
# Umumiy yordamchilar
# --------------------------------------------------------------------------

def now() -> datetime:
    return datetime.now(TZ)


def today_str() -> str:
    return now().date().isoformat()


def log(conn, action: str, employee_id=None, device_id="", ip="", user_agent="", detail=""):
    conn.execute(
        "INSERT INTO audit (ts, employee_id, action, device_id, ip, user_agent, detail) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (now().isoformat(timespec="seconds"), employee_id, action,
         device_id, ip, user_agent[:300], detail),
    )


def absence_for(conn, employee_id: int, day: str):
    """Shu kunga sababli yo'qlik yozilganmi?"""
    return conn.execute(
        "SELECT * FROM absences WHERE employee_id = ? AND date_from <= ? AND date_to >= ?"
        " LIMIT 1",
        (employee_id, day, day),
    ).fetchone()


def active_employees(conn):
    order = "LOWER(full_name)" if IS_PG else "full_name COLLATE NOCASE"
    return conn.execute(
        f"SELECT * FROM employees WHERE active = 1 ORDER BY {order}"
    ).fetchall()


def all_employees(conn):
    order = "LOWER(full_name)" if IS_PG else "full_name COLLATE NOCASE"
    return conn.execute(
        f"SELECT * FROM employees ORDER BY active DESC, {order}"
    ).fetchall()


def parse_date(value: str, fallback: date | None = None) -> date:
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        return fallback or now().date()
