"""Vercel uchun kirish nuqtasi.

Vercel shu faylni topadi va undagi `app` obyektini ishga tushiradi.
Barcha manzillar `vercel.json` orqali shu yerga yo'naltiriladi.
"""
import pathlib
import sys

# Loyiha ildizini import yo'liga qo'shamiz, shunda `app` paketi topiladi
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from app.main import app  # noqa: E402

__all__ = ["app"]
