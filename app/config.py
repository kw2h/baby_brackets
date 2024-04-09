from pydantic_settings import BaseSettings


class Settings(BaseSettings):
   # Base
   api_v1_prefix: str
   debug: bool
   project_name: str
   version: str
   description: str

   # Database
   db_async_connection_str: str

   # OAuth
   secret_key: str
   algorithm: str
   access_token_expire_minutes: int
   cookie_name: str