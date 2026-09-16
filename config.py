import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'max_leo_supermercados_secret_key_2026')
    
    # Suporte a PostgreSQL / MySQL ou SQLite como fallback local
    # Exemplo Postgres: postgresql+psycopg2://user:password@localhost:5432/max_candidatos
    # Exemplo MySQL: mysql+pymysql://user:password@localhost:3306/max_candidatos
    DATABASE_URL = os.getenv('DATABASE_URL')
    if DATABASE_URL:
        # Corrigir prefixo postgres:// caso venha de serviços como Render/Heroku
        if DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # Fallback local seguro caso nenhuma URL externa de banco seja fornecida
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(BASE_DIR, "candidatos_max.db")}'
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Uploads
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
