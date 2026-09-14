from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "BlueVerify AI"
    database_url: str = "sqlite:///./blueverify.db"
    admin_api_key: str = "changeme"
    # How close (in km) two submissions must be to trigger a duplicate flag
    duplicate_radius_km: float = 50.0

    class Config:
        env_file = ".env"


# Single shared instance used across the app
settings = Settings()
