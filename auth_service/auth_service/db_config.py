from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseConfig(BaseSettings):

    DB_USER: str
    DB_NAME: str
    DB_HOST: str
    DB_PORT: int
    DB_PASSWORD: str

    model_config = SettingsConfigDict(env_file="auth_service/.env")


db_config = DatabaseConfig()
