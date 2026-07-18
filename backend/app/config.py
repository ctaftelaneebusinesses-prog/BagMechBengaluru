from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    allowed_origins: str = "*"
    db_pool_size: int = 5
    db_max_overflow: int = 5

    # ---- Email notifications (SMTP) ----
    enable_email_notifications: bool = False
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    notify_email_from: str = ""
    notify_email_to: str = ""

    # ---- WhatsApp notifications (Twilio) ----
    enable_whatsapp_notifications: bool = False
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_whatsapp_from: str = ""   # e.g. +14155238886 (sandbox) or your approved number
    owner_whatsapp_number: str = ""  # e.g. +9198XXXXXXXX — where alerts should land

    # ---- WhatsApp click-to-chat (public-facing, used by the "WhatsApp Us" buttons) ----
    whatsapp_business_number: str = ""  # e.g. "919876543210" — digits only, no +/spaces

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]


settings = Settings()