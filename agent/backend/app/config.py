import os
os.environ["NO_GCE_CHECK"] = "true"
os.environ["GCE_METADATA_HOST"] = "127.0.0.1:9999"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "false"
os.environ["GEMINI_MODEL"] = "gemini-flash-lite-latest"

import os
from dotenv import load_dotenv

load_dotenv(override=True)

class Settings:
    raw_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY") or ""
    GOOGLE_API_KEY: str = raw_key.strip().strip("'").strip('"')
    GEMINI_MODEL: str = "gemini-flash-lite-latest"
    GRAFANA_URL: str = os.getenv("GRAFANA_URL", "").rstrip("/")
    GRAFANA_API_KEY: str = (os.getenv("GRAFANA_API_KEY") or "").strip().strip("'").strip('"')

settings = Settings()

if settings.GOOGLE_API_KEY:
    os.environ["GOOGLE_API_KEY"] = settings.GOOGLE_API_KEY
    os.environ["GEMINI_API_KEY"] = settings.GOOGLE_API_KEY
if settings.GRAFANA_API_KEY:
    os.environ["GRAFANA_API_KEY"] = settings.GRAFANA_API_KEY
