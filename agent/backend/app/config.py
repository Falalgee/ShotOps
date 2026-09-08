import os
from dotenv import load_dotenv

load_dotenv(override=True)

class Settings:
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    GRAFANA_URL: str = os.getenv("GRAFANA_URL", "").rstrip("/")

settings = Settings()
