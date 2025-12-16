from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    PS3838_LOGIN: str | None = None
    PS3838_PASSWORD: str | None = None
    PS3838_API_BASE_URL: str | None = None
    billing_period_day: int

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()  # type: ignore[call-arg]
