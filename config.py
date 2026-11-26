import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Ejecutable empaquetado: los datos viven en una carpeta fija del usuario, no dentro del .exe.
if getattr(sys, "frozen", False):
    DATOS_DIR = Path(os.getenv("HISLA_DATOS") or Path(os.getenv("APPDATA") or Path.home()) / "HISLA")
else:
    DATOS_DIR = Path(os.getenv("HISLA_DATOS") or BASE_DIR)
DATOS_DIR.mkdir(parents=True, exist_ok=True)

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "clave-dev-cambiar")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", f"sqlite:///{DATOS_DIR / 'historias_laborales.db'}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = DATOS_DIR / "uploads" / "historias"
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))
    WTF_CSRF_TIME_LIMIT = 8 * 60 * 60
