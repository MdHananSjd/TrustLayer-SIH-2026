from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    PROJECT_NAME: str = "TrustLayer"
    API_V1_STR: str = "/api/v1"
    
    # Project paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DEMO_ASSETS_DIR: Path = BASE_DIR / "demo-assets"
    
    class Config:
        case_sensitive = True

settings = Settings()