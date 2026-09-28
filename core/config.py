from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    database_url: str
    openai_api_key: str
    openrouter_api_key: str
    openai_model: str
    jev_model: str
    jev_base_url: str


settings = Settings()