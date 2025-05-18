import os

# Si estamos en Render, usará PostgreSQL, si no, SQLite local
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///local.db")

class Config:
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
