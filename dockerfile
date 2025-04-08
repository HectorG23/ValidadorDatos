FROM python:3.9-slim

# 1. Instalar dependencias del sistema
RUN apt-get update && \
    apt-get install -y curl gnupg2 unixodbc-dev && \
    curl -sSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /usr/share/keyrings/microsoft-prod.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/debian/11/prod bullseye main" > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql18

# 2. Copiar el código e instalar dependencias de Python
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Variables de entorno para ODBC
ENV LD_LIBRARY_PATH=/opt/microsoft/msodbcsql18/lib64:$LD_LIBRARY_PATH

# 4. Comando de inicio
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8000"]