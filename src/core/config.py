from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = 'domain_api'
    log_level: str = 'INFO'
    api_login: str
    api_pass: str
    sign_key: str
    partner_id: int

    class Config:
        env_file = '.env'


settings = Settings()
