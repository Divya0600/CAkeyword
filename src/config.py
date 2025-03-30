import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str
    keycloak_url: str
    keycloak_realm: str
    keycloak_client_id: str
    keycloak_client_secret: str

class TestSettings(Settings):
    app_env: str = 'test'
    keycloak_url: str = 'unused'
    keycloak_realm: str = 'unused'
    keycloak_client_id: str = 'unused'
    keycloak_client_secret: str = 'unused'

environment_settings = {
    'test': TestSettings,
    'dev': Settings,
    'prod': Settings
}

def get_settings():
    env = os.getenv('APP_ENV', 'test')
    settings = environment_settings[env]
    return settings()