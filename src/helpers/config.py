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

    class Config:
        env_file = ".env"  # specify the name of the environment file to load


def get_settings():
    return Settings()  # create an instance (object) of the Settings class, which will automatically read the configuration from the environment variables or the .env file.
