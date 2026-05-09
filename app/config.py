import os


class Settings:
    """Uygulama konfigürasyonu. Tek sorumluluk: ortam değişkenlerini okumak."""

    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_USERNAME: str = os.getenv("DB_USERNAME", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres")
    WALLET_TYPE: str = os.getenv("WALLET_TYPE", "pgsql")
    WALLET_PASSWORD: str = os.getenv("WALLET_PASSWORD", "123456")
    TRUSTEE_SEED: str = os.getenv("TRUSTEE_SEED", "000000000000000000000000Trustee1")
    MAX_CRED_NUM: int = int(os.getenv("MAX_CRED_NUM", "1000"))


settings = Settings()
