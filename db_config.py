from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    duckdb_string: str = "duckdb:///adtech.db"
    
settings = Settings()