"""
Application Configuration
"""

class Settings:
    app_name: str = "Electric Demand Forecasting API"
    debug: bool = True
    api_version: str = "1.0.0"
    cors_origins: list = ["http://localhost:5173", "http://127.0.0.1:5173"]
    model_dir: str = "ml/models"

settings = Settings()
