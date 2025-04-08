import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'clave_predeterminada')

    DB_SERVER = os.environ.get('DATABASE_SERVER')
    DB_NAME = os.environ.get('DATABASE_NAME')
    DB_USER = os.environ.get('DATABASE_USER')
    DB_PASSWORD = os.environ.get('DATABASE_PASSWORD')
    DB_DRIVER = os.environ.get('DATABASE_DRIVER')

    SQLALCHEMY_DATABASE_URI = (
        f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}:1433/{DB_NAME}"
        f"?driver={DB_DRIVER.replace(' ', '+')}"
        f"&authentication=ActiveDirectoryPassword"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
