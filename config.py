import os
from dotenv import load_dotenv


load_dotenv()


class Config:
    ENV = os.getenv("FLASK_ENV", "development")
    DEBUG = os.getenv("FLASK_DEBUG", "0") == "1" or ENV == "development"
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me")

    # PostgreSQL connection string.
    # Example:
    # postgresql+psycopg2://user:password@localhost:5432/dbname
    DATABASE_URL = os.getenv("DATABASE_URL")

