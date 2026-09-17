"""Davomat tizimini ishga tushirish: python run.py

`.env` fayli bo'lsa o'qiydi (masalan DATABASE_URL). Fayl bo'lmasa tizim
lokal SQLite bazasi bilan ishlaydi.
"""
import os
import pathlib

env_file = pathlib.Path(__file__).resolve().parent / ".env"
if env_file.exists():
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))

import uvicorn  # noqa: E402

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
