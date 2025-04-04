#!/bin/bash
# Instala ODBC Driver 18
apt-get update && apt-get install -y curl gnupg
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list
apt-get update
ACCEPT_EULA=Y apt-get install -y msodbcsql18 unixodbc-dev

# Instala dependencias de Python
pip install -r requirements.txt

# Inicia la app con Gunicorn (apunta al módulo Flask)
gunicorn --bind 0.0.0.0:$PORT app.__init__:app