import os


class Settings:
    """Global configuration settings, read from environment variables."""

    DB_CONNECTION_STRING = os.getenv(
        "DB_CONNECTION_STRING",
        "DRIVER={ODBC Driver 18 for SQL Server};SERVER=localhost;DATABASE=SMART_EMP;"
        "Trusted_Connection=yes;TrustServerCertificate=yes",
    )


settings = Settings()
