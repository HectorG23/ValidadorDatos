#!/bin/bash

# Actualiza los paquetes e instala dependencias necesarias
apt-get update && apt-get install -y \
    curl \
    gnupg \
    unixodbc \
    unixodbc-dev \
    libssl-dev

# Agrega la clave y el repositorio de Microsoft
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list

# Actualiza los paquetes e instala el controlador ODBC 18
apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql18

# Limpia los archivos temporales
apt-get clean && rm -rf /var/lib/apt/lists/*

# Ejecuta tu aplicación
gunicorn run:app