import json

# Leer las credenciales desde un archivo externo
with open('secrets.json') as f:
    secrets = json.load(f)

class Config:
    DB_CONFIG = {
        'server': 'sqls-ur-datamining-dev.database.windows.net',
        'database': 'DB_ValidadorArchivos',
        'driver': 'ODBC Driver 18 for SQL Server',
        'authentication': 'ActiveDirectoryPassword',
        'username': secrets['db_user'],
        'password': secrets['db_password'],
    }

    UPLOAD_FOLDER = 'uploads'
    VALIDATED_FOLDER = 'validated'
    DIFFERENT_FOLDER = 'different'
    SECRET_KEY = 'supersecretykey'
