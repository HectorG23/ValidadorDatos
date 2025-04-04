
class Config:
    # Configuración de la base de datos (Azure SQL) con AAD MFA
    UPLOAD_FOLDER = 'path/to/upload/folder'
    DB_CONFIG = {
        'server':'sqls-ur-datamining-dev.database.windows.net',  # Nombre del servidor Azure
        'database': 'DB_ValidadorArchivos',                             # Nombre de la BD en Azure
        'driver': 'ODBC Driver 18 for SQL Server',  # Ajusta si usas Driver 17 u otra versión
        'authentication': 'ActiveDirectoryInteractive',  # Tipo de autenticación (MFA)          
    }

    # Configuración de la aplicación
    UPLOAD_FOLDER = 'uploads'
    VALIDATED_FOLDER = 'validated'
    DIFFERENT_FOLDER = 'different'
    SECRET_KEY = 'supersecretykey'