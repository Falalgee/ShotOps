import os
from dotenv import load_dotenv

load_dotenv(override=True)

class Settings:
    raw_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY") or ""
    GOOGLE_API_KEY: str = raw_key.strip().strip("'").strip('"')
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
    GRAFANA_URL: str = os.getenv("GRAFANA_URL", "").rstrip("/")
    GRAFANA_API_KEY: str = (os.getenv("GRAFANA_API_KEY") or "").strip().strip("'").strip('"')

settings = Settings()

if settings.GOOGLE_API_KEY:
    os.environ["GOOGLE_API_KEY"] = settings.GOOGLE_API_KEY
    os.environ["GEMINI_API_KEY"] = settings.GOOGLE_API_KEY
if settings.GRAFANA_API_KEY:
    os.environ["GRAFANA_API_KEY"] = settings.GRAFANA_API_KEY
