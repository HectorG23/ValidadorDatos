FROM python:3.9-slim

# Instalar ODBC Driver 18 para SQL Server
RUN apt-get update && \
    apt-get install -y curl gnupg2 unixodbc-dev && \
    curl -sSL https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl -sSL https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql18

# Copiar el código
COPY . /app
WORKDIR /app

# Instalar dependencias
RUN pip install -r requirements.txt

# Comando para iniciar la app
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8000"]