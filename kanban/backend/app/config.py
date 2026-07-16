from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://kanban:kanban@db:5432/kanban"
    jwt_secret: str = "change_me_in_env"
    jwt_ttl_hours: int = 24

    class Config:
        env_file = ".env"


settings = Settings()
