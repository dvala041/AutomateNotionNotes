import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App settings
    app_name: str = "Automate Notion Notes API"
    debug: bool = False

    #OpenAI API settings
    openai_api_key: str = ""
    
    # Notion API settings
    notion_api_key: str = ""
    notion_database_id: str = ""
    
    # Instagram Authentication (optional)
    instagram_username: str = ""
    instagram_password: str = ""
    
    # Security
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"

settings = Settings()
