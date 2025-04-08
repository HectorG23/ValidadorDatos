FROM python:3.9-slim

# 1. Instalar dependencias del sistema
RUN apt-get update && \
    apt-get install -y \
    curl \
    gnupg2 \
    unixodbc-dev \
    gpg \
    && rm -rf /var/lib/apt/lists/*

# 2. Configurar repositorio Microsoft para ODBC Driver 18
RUN curl -sSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /usr/share/keyrings/microsoft-prod.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/debian/11/prod bullseye main" > /etc/apt/sources.list.d/mssql-release.list

# 3. Instalar el driver ODBC
RUN apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql18 && \
    rm -rf /var/lib/apt/lists/*

# 4. Configurar variables de entorno para ODBC
ENV LD_LIBRARY_PATH=/opt/microsoft/msodbcsql18/lib64:$LD_LIBRARY_PATH

# 5. Configurar el entorno de trabajo
WORKDIR /app

# 6. Copiar requirements.txt primero (para cachear la instalación de dependencias)
COPY requirements.txt .

# 7. Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# 8. Copiar el resto de la aplicación
COPY . .

# 9. Comando de inicio (ajusta según tu aplicación)
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8000"]