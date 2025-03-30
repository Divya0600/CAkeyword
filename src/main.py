from fastapi import FastAPI
from fastapi_keycloak_middleware import KeycloakConfiguration, KeycloakMiddleware

from src.config import get_settings
from src.routes import router

def get_app():
    settings = get_settings()
    app = FastAPI()

    if settings.app_env != 'test':
        # Set up Keycloak
        keycloak_config = KeycloakConfiguration(
            url=settings.keycloak_url,
            realm=settings.keycloak_realm,
            client_id=settings.keycloak_client_id,
            client_secret=settings.keycloak_client_secret,
            decode_options={
                "verify_signature": True,
                "verify_aud": False,
                "verify_exp": True,
            }
        )
        # Add keycloak middleware
        app.add_middleware(
            KeycloakMiddleware,
            keycloak_configuration=keycloak_config,
            exclude_patterns=['/health', '/ready']
        )

    app.include_router(router)
    return app

app = get_app()
