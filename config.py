import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', './uploads')
    VALIDATED_FOLDER = os.getenv('VALIDATED_FOLDER', './validated')
    DIFFERENT_FOLDER = os.getenv('DIFFERENT_FOLDER', './different')

    # Configuración de la base de datos
    DATABASE_SERVER = os.getenv('DATABASE_SERVER')
    DATABASE_NAME = os.getenv('DATABASE_NAME')
    DATABASE_USER = os.getenv('DATABASE_USER')
    DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')
    DATABASE_DRIVER = os.getenv('DATABASE_DRIVER')

    SQLALCHEMY_DATABASE_URI = (
        f"mssql+pyodbc://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_SERVER}/{DATABASE_NAME}"
        f"?driver={DATABASE_DRIVER}"
    )   