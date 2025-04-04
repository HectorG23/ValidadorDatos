import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', './uploads')
    VALIDATED_FOLDER = os.getenv('VALIDATED_FOLDER', './validated')
    DIFFERENT_FOLDER = os.getenv('DIFFERENT_FOLDER', './different')

    # Configuración de la base de datos
    DB_CONFIG = {
        'server': os.getenv('DATABASE_SERVER', 'sqls-ur-datamining-dev.database.windows.net'),
        'database': os.getenv('DATABASE_NAME', 'DB_ValidadorArchivos'),
        'username': os.getenv('DATABASE_USER', 'your-username'),
        'password': os.getenv('DATABASE_PASSWORD', 'your-password'),
        'driver': os.getenv('DATABASE_DRIVER', 'ODBC Driver 18 for SQL Server'),
    }