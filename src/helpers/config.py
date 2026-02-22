from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)  # settingconfigdict is used to specify the configuration for the settings class, such as the environment file to load and whether to allow extra fields in the settings.


class Settings(
    BaseSettings
):  # inherit from BaseSettings to create a settings class that can read configuration from environment variables or a .env file.
    # Define your configuration variables here

    APP_NAME: str
    APP_VERSION: str
    OPENAI_API_KEY: str

    FILE_ALLOWED_TYPES: list
    FILE_MAX_SIZE: int
    FILE_DEFAULT_CHUNCK_SIZE: int

    MONGODB_URL: str
    MONGODB_DATABASE: str
    
    GENERATION_BACKEND: str
    EMBEDDING_BACKEND: str

    OPENAI_API_KEY: str = None
    OPENAI_API_URL: str = None
    COHERE_API_KEY: str = None

    GENERATION_MODEL_ID: str = None
    EMBEDDING_MODEL_ID: str = None
    EMBEDDING_MODEL_SIZE: int = None
    INPUT_DAFAULT_MAX_CHARACTERS: int = None
    GENERATION_DAFAULT_MAX_TOKENS: int = None
    GENERATION_DAFAULT_TEMPERATURE: float = None

    class Config:
        env_file = ".env"  # specify the name of the environment file to load


def get_settings():
    return Settings()  # create an instance (object) of the Settings class, which will automatically read the configuration from the environment variables or the .env file.
