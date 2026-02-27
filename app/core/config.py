import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # API Keys
    GROQ_API_KEY: str

    # LLM config
    MODEL_NAME: str = "llama-3.3-70b-versatile"
    TEMPERATURE: float = 0.0

    # Project settings
    PROJECT_NAME: str = "Titanic Dataset Chat Agent"
    
    # Dataset path relative to the project root
    DATASET_PATH: str = os.path.join("data", "titanic.csv")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
