FROM python:3.9-bullseye 
# 1. Instalar dependencias del sistema
RUN apt-get update && \
    apt-get install -y \
    curl \
    gnupg2 \
    unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

# 2. Configurar repositorio Microsoft (método alternativo)
RUN curl -sSL https://packages.microsoft.com/keys/microsoft.asc > microsoft.asc && \
    gpg --dearmor microsoft.asc > /etc/apt/trusted.gpg.d/microsoft.gpg && \
    echo "deb [arch=amd64] https://packages.microsoft.com/debian/11/prod bullseye main" > /etc/apt/sources.list.d/mssql-release.list

# 3. Instalar el driver ODBC (con reintento)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    msodbcsql18 \
    && rm -rf /var/lib/apt/lists/*

# 4. Configurar entorno ODBC
ENV LD_LIBRARY_PATH=/opt/microsoft/msodbcsql18/lib64:$LD_LIBRARY_PATH

# 5. Configurar el entorno de trabajo
WORKDIR /app

# 6. Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 7. Copiar la aplicación
COPY . .

# 8. Comando de inicio
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8000"]