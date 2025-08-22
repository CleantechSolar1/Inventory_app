import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

# Load environment variables from .env file
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_default_secret_key')
    
    # PostgreSQL connection settings from environment variables
    POSTGRES_USER = os.getenv('POSTGRES_USER', 'inventory_oa06_user')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'HiafztY7PGlYOGqqUdKTDtqaAw9IQY2e')
    POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'dpg-cvhe9g52ng1s73bf72ng-a.oregon-postgres.render.com')
    POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')  # Default PostgreSQL port
    POSTGRES_DB = os.getenv('POSTGRES_DB', 'inventory_oa06')

    # SQLAlchemy database URI for PostgreSQL
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg2://{POSTGRES_USER}:{quote_plus(POSTGRES_PASSWORD)}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
