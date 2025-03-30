from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )

    # QDRANT
    QDRANT_URL: str
    QDRANT_APIKEY: str
    QDRANT_COLLECTION: str

    # GEMINI
    GEMINI_API_KEY: str



settings = Settings()