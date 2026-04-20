from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    project_name: str = "Nexus Event API"
    project_version: str = "1.0.0"
    db_user: str
    db_pass: str
    db_name: str
    instance_connection_name: str
    google_cloud_project: str = "nexus-event-app-1904"
    location: str = "asia-south1"

    # Expects the .env file to be in the backend/ directory
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
