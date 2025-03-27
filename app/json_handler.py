import datetime
import pyodbc
from flask import current_app, render_template, request, redirect, url_for, flash
import os
import json
import shutil

def conectar_db():
    # 1. Obtén la configuración desde la clase Config
    cfg = current_app.config['DB_CONFIG']
    server = cfg['server']
    database = cfg['database']
    driver = cfg['driver']

    # 2. Construye la cadena de conexión con Authentication=ActiveDirectoryInteractive
    connection_string = (
        f"DRIVER={{{driver}}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        "Authentication=ActiveDirectoryInteractive;"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
        "Connection Timeout=30;"
    )

    # 3. Conéctate a la base de datos
    try:
        print(f"Intentando conectar a la base de datos con la cadena de conexión: {connection_string}")
        conn = pyodbc.connect(connection_string)
        print("Conexión a la base de datos establecida.")
        return conn
    except pyodbc.Error as e:
        print(f"Error al conectar a la base de datos: {str(e)}")
        return None

def mover_a_historicos(nombre_plantilla, ruta_actual):
    # Define la nueva ruta donde se moverá el archivo
    nueva_ruta = os.path.join("uploads/historicos", nombre_plantilla)

    # Verifica si el archivo existe en la ruta actual
    if not os.path.exists(ruta_actual):
        print(f"Advertencia: El archivo no existe en la ruta especificada: {ruta_actual}")
        return None  # O manejar el caso según sea necesario

    # Crea la carpeta de destino si no existe
    os.makedirs(os.path.dirname(nueva_ruta), exist_ok=True)

    # Mueve el archivo a la nueva ruta
    shutil.move(ruta_actual, nueva_ruta)
    return nueva_ruta

def subir_json(json_path,idProcesoAdmin):
    # Leer el contenido del archivo JSON desde la ruta proporcionada
    try:
        with open(json_path, 'r', encoding='utf-8') as file:
            contenido_json = file.read()
        print(f"Contenido del JSON leído correctamente.")
    except Exception as e:
        return f"Error al leer el archivo JSON: {str(e)}"

    # El nombre puede venir de la ruta del archivo
    nombre_plantilla = os.path.basename(json_path)
    fecha_carga = datetime.datetime.now()
    fecha_modificacion = datetime.datetime.now()
    usuario_cargue = "hectord.godoy@urosario.edu.co"
    estado_plantilla = "Activo"

    conn = conectar_db()
    if not conn:
        return "Error al conectar a la base de datos."

    cursor = conn.cursor()
    
        # Verificar si ya existe un archivo con el mismo nombre
    cursor.execute("SELECT RutaJSON FROM dbo.PlantillasValidacion WHERE NombrePlantilla = ?", nombre_plantilla)
    row = cursor.fetchone()
    if row:
        ruta_actual = row[0]
        if not os.path.exists(ruta_actual):
            print(f"Advertencia: La ruta almacenada en la base de datos no es válida: {ruta_actual}")
            ruta_actual = None  # O manejar el caso según sea necesario
        else:
            nueva_ruta = mover_a_historicos(nombre_plantilla, ruta_actual)
            cursor.execute("UPDATE dbo.PlantillasValidacion SET RutaJSON = ? WHERE NombrePlantilla = ?", nueva_ruta, nombre_plantilla)
            conn.commit()
            print(f"Ruta actual obtenida de la base de datos: {ruta_actual}")
            print(f"Archivo existente movido a {nueva_ruta}")
    
    insert_query = """
        INSERT INTO [dbo].[PlantillasValidacion]
        (NombrePlantilla, ContenidoJson, RutaJSON, FechaCarga, FechaUltimaModificacion, UsuarioCargue, EstadoPlantilla, idProcesoAdmin)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    print(f"Ejecutando consulta SQL: {insert_query}")
    try:
        cursor.execute(
            insert_query,
            (
                nombre_plantilla,
                contenido_json,
                json_path,
                fecha_carga,
                fecha_modificacion,
                usuario_cargue,
                estado_plantilla,
                idProcesoAdmin
            )
        )
        conn.commit()
        print("Transacción confirmada.")
    except pyodbc.Error as e:
        conn.rollback()
        print(f"Error al ejecutar la consulta SQL: {str(e)}")
        return f"Error al guardar el archivo JSON en la base de datos: {str(e)}"
    finally:
        cursor.close()
        conn.close()
        print("Conexión a la base de datos cerrada.")

    return "Archivo JSON guardado exitosamente en la base de datos."

def obtener_nombres_json():
    conn = conectar_db()  # Usa la función conectar_db() para establecer la conexión
    cursor = conn.cursor()

    query = """
    SELECT NombrePlantilla, MAX(FechaCarga) as FechaUltimaModificacion 
    FROM [dbo].[PlantillasValidacion]
    GROUP BY NombrePlantilla
    ORDER BY NombrePlantilla, FechaUltimaModificacion DESC
    """
    cursor.execute(query)

    archivos_json = [{"nombre": row[0]} for row in cursor.fetchall()]

    cursor.close()
    conn.close()
    return archivos_json

def obtener_fechas_json(nombre_plantilla):
    conn = conectar_db()
    if not conn:
        return []

    cursor = conn.cursor()
    query = """
    SELECT FechaCarga 
    FROM [dbo].[PlantillasValidacion]
    WHERE NombrePlantilla = ?
    ORDER BY FechaCarga DESC
    """
    cursor.execute(query, (nombre_plantilla,))
    fechas = [row[0].strftime('%Y-%m-%d %H:%M:%S') for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    return fechas