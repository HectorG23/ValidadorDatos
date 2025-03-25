
from flask import Flask
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Crear las carpetas si no existen
import os
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

if not os.path.exists(app.config['VALIDATED_FOLDER']):
    os.makedirs(app.config['VALIDATED_FOLDER'])

if not os.path.exists(app.config['DIFFERENT_FOLDER']):
    os.makedirs(app.config['DIFFERENT_FOLDER'])

# Importar las rutas al final para evitar importaciones circulares
from app import routes