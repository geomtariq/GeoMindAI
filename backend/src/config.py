from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # This file can be used for other application-level settings in the future.
    pass

settings = Settings()
