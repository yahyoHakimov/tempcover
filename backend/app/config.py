"""
App Configuration — environment variables (.env)
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://tempcover:tempcover@localhost:5432/tempcover"

    # JWT
    SECRET_KEY: str = "change-this-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Email (Brevo). Empty key = dev mode: emails are printed to the log.
    BREVO_API_KEY: str = ""
    FROM_EMAIL: str = "noreply@tempcovermyaccount.com"
    FROM_NAME: str = "Tempcover"
    SUPPORT_EMAIL: str = "support@tempcovermyaccount.com"

    # App
    APP_URL: str = "https://tempcovermyaccount.com"
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: str = "http://localhost:3000"
    STATIC_DIR: str = "./static"

    # Internal "house" agent the super admin acts as when issuing policies directly
    HOUSE_TENANT_USERNAME: str = "tempcover-hq"

    # Brand / legal identity — printed in email footers and PDF footers.
    # Leave a value blank to omit that line entirely (nothing is invented).
    # Standart qiymatlar asl Tempcover tasdiqlash xatidan olingan.
    SITE_NAME: str = "tempcover.com"          # "Thanks for choosing tempcover.com", banner, mavzu
    TRADING_NAME: str = "Tempcover"
    COMPANY_LEGAL_NAME: str = "Tempcover Ltd"
    COMPANY_REG_NO: str = "9923259"
    REGISTERED_OFFICE: str = "2nd Floor Admiral House, Harlington Way, Fleet, Hampshire, GU51 4BB"
    FCA_FRN: str = "746985"
    UNDERWRITER_NAME: str = "First Underwriting"
    UNDERWRITER_FRN: str = ""
    CLAIMS_HOTLINE: str = "0333 241 3392"      # sertifikat sarlavhasidagi raqam
    POLICY_NUMBER_PREFIX: str = "TCV-MOT-"

    # Policy lifecycle jobs (0 = disabled)
    LIFECYCLE_TICK_SECONDS: int = 60
    REMINDER_HOURS_BEFORE_EXPIRY: int = 24
    AGENT_DIGEST_HOUR_UTC: int = 8
    AGENT_DIGEST_DAYS_AHEAD: int = 3

    # First-run seed (see seed.py)
    SEED_SUPERADMIN_USERNAME: str = "superadmin"
    SEED_SUPERADMIN_PASSWORD: str = ""
    SEED_SUPERADMIN_EMAIL: str = "admin@tempcovermyaccount.com"
    SEED_SUPERADMIN_NAME: str = "TempCover Admin"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


settings = Settings()
