from flask import render_template,render_template_string, request, redirect, url_for, flash, jsonify,send_from_directory,session
from app import app
import pyodbc
from datetime import datetime
from app.json_handler import conectar_db, obtener_nombres_json, subir_json
from app.validations import validar_excel_con_cerberus
from app.json_handler import obtener_fechas_json
import shutil
import os
from ldap3 import Server, Connection, ALL
import smtplib
from config import Config
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd, json, time, os,re
from app.json_routes import json_routes
app.register_blueprint(json_routes)


def enviar_reporte_errores(errores, destinatario):
    # Configuración del servidor SMTP
    smtp_server = "smtp.office365.com"
    smtp_port = 587
    smtp_user = "notificacionessii@urosario.edu.co"
    smtp_password = "30dQ0dIQDJ4L3rzpUHMo"

    # Crear el mensaje
    msg = MIMEMultipart()
    msg["From"] = smtp_user
    msg["To"] = destinatario
    msg["Subject"] = "Reporte de Errores en Validación de Excel"

    # Crear el contenido del correo en formato HTML
    html = [
            "<html>",
            "<body>",
            "<h2>Reporte de Errores en Validación de Excel</h2>",
            "<table border='1' style='border-collapse: collapse;'>",
            "<tr>",
            "<th>hoja</th>",
            "<th>fila</th>",
            "<th>Error</th>",
            "</tr>"
    ]
    for error in errores:
            hoja = error.get('hoja', 'N/A')
            fila = error.get('fila', 'N/A')
            error_desc = error.get('errores', 'N/A')
            html.append(f"<tr><td>{hoja}</td><td>{fila}</td><td>{error_desc}</td></tr>")
    html.extend([
            "</table>",
            "</body>",
            "</html>"
        ])
    html_content = "".join(html)

    # Adjuntar el contenido HTML al mensaje
    msg.attach(MIMEText(html_content, "html"))

    # Enviar el correo
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, destinatario, msg.as_string())
        server.quit()
        print("Correo enviado exitosamente")
    except Exception as e:
        print(f"Error al enviar el correo: {str(e)}")

def get_db_parameters():
    try:
        conn = conectar_db()
        if not conn:
            print("Error: No se pudo establecer conexión con la base de datos.")
            return None

        cursor = conn.cursor()
        cursor.execute("SELECT nombreParametro, valorParametro FROM dbo.Parametros")
        params = {row.nombreParametro: row.valorParametro for row in cursor.fetchall()}
        conn.close()
        print("Parámetros obtenidos de la base de datos:", params)  # Depuración
        return params
    except Exception as e:
        print(f"Error al obtener parámetros de la base de datos: {e}")
        return None

# Función para autenticar con LDAP usando los parámetros obtenidos de la BD
def ldap_authenticate(email, password):
    # Obtiene los parámetros desde la base de datos
    params = get_db_parameters()
    if not params:
        print("Error: No se pudieron obtener los parámetros de la base de datos.")
        return False

    # Extrae los parámetros necesarios
    server_address = params.get("server_address")
    admin_user = params.get("admin_user")
    admin_pass = params.get("admin_pass")
    search_base = params.get("search_base")

    # Verifica que todos los parámetros estén presentes
    if not all([server_address, admin_user, admin_pass, search_base]):
        print("Error: Faltan parámetros en la base de datos.")
        return False

    try:
        # Conexión al servidor LDAP
        print(f"Conectando al servidor LDAP: {server_address}")
        server = Server(server_address, port=389, get_info=ALL)
        conn = Connection(server, user=email, password=password, auto_bind=True)  # Autenticación del usuario
        print(f"Autenticación exitosa para el usuario: {email}")

        username = email.split("@")[0]
        conn_admin = Connection(server, user=admin_user, password=admin_pass, auto_bind=True)
        print(f"Conexión como administrador exitosa: {admin_user}")

        search_filter = f"(&(objectClass=user)(sAMAccountName={username}))"
        attributes = ["ou", "sn", "givenname", "mail", "extensionattribute8", "postofficebox",
                      "extensionattribute4", "info", "title", "department"]

        # Realiza la búsqueda en el directorio activo
        conn_admin.search(search_base, search_filter, attributes=attributes)
        print(f"Búsqueda LDAP realizada con éxito para el usuario: {username}")

        # Devuelve True si se encontraron entradas, False en caso contrario
        return bool(conn_admin.entries)

    except Exception as e:
        print(f"Error en autenticación LDAP: {e}")
        return False
@app.route('/paginaInicial')
def index_page():
    return render_template('index.html')

@app.route('/', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def inicio_sesion():
    print(f"Request method: {request.method}")  # Depuración
    if request.method == 'GET':
        # Renderiza la página de inicio de sesión
        return render_template('inicioSesion.html')

    if request.method == 'POST':
        # Obtiene las credenciales del formulario
        email = request.form.get('email')
        password = request.form.get('password')

        # Verifica las credenciales con LDAP
        if ldap_authenticate(email, password):
            session['user'] = email  # Guarda el usuario en la sesión
            flash("Inicio de sesión exitoso.", "success")
            return redirect(url_for('index_page'))  # Redirige a la página validador.html
        else:
            flash("Usuario y/o Contraseña incorrecta.", "error")
            return redirect(url_for('inicio_sesion'))

    # Si por alguna razón no se ejecuta ninguno de los bloques anteriores
    return redirect(url_for('inicio_sesion'))


@app.route('/cerrar_sesion')
def cerrar_sesion():
    # Elimina la sesión del usuario
    session.pop('user', None)
    flash("Sesión cerrada exitosamente.", "success")
    return redirect(url_for('inicio_sesion'))

@app.route('/dashboard', methods=['GET'])
def dashboard():
    if 'user' not in session:
        flash("Debe iniciar sesión para acceder al dashboard.", "error")
        return redirect(url_for('inicio_sesion'))
    return render_template('validador.html')
    
@app.route('/validador', methods=['GET', 'POST'])
def validador():
    if request.method == 'GET':
        # Lógica para manejar la solicitud GET (cargar datos iniciales)
        conn = conectar_db()
        if not conn:
            flash("Error al conectar a la base de datos.", "error")
            return render_template('validador.html', json_files=[], procesos=[])

        cursor = conn.cursor()
        try:
            cursor.execute("SELECT NombrePlantilla FROM [dbo].[PlantillasValidacion] WHERE EstadoPlantilla = 'Activo'")
            json_files = [row.NombrePlantilla for row in cursor.fetchall()]

            cursor.execute("SELECT idProcesoAdmin, nombreProcesoAdmin FROM [dbo].[ProcesosAdministrativos] WHERE estadoProcesoAdmin IN ('Activo', 'Inactivo')")
            procesos = cursor.fetchall()
        except pyodbc.Error as e:
            flash(f"Error al obtener los archivos JSON o procesos: {str(e)}", "error")
            json_files = []
            procesos = []
        finally:
            cursor.close()
            conn.close()

        return render_template('validador.html', json_files=json_files, procesos=procesos)

    elif request.method == 'POST':
        # Lógica para manejar la solicitud POST (validación de archivos)
        if 'file_excel' not in request.files or 'jsonSelect' not in request.form:
            flash("No file part", "error")
            return redirect(url_for("validador"))

        file_excel = request.files['file_excel']
        jsonSelect = request.form['jsonSelect']

        # Verifica si los archivos tienen nombre
        if file_excel.filename == '' or jsonSelect == '':
            flash("Por favor seleccione ambos archivos", "error")
            return redirect(url_for("validador"))

        if file_excel and jsonSelect:
            # Guarda el archivo Excel subido
            excel_path = os.path.join(app.config['UPLOAD_FOLDER'], file_excel.filename)
            file_excel.save(excel_path)

            # Obtiene la ruta del JSON desde la base de datos
            conn = conectar_db()
            cursor = conn.cursor()

            cursor.execute("SELECT idPlantillasValidacion, RutaJSON FROM dbo.PlantillasValidacion WHERE NombrePlantilla = ?", jsonSelect)
            row = cursor.fetchone()

            if row is None:
                flash("Error: No se encontró la plantilla JSON en la base de datos.", "error")
                return redirect(url_for("validador"))

            id_plantilla_validacion = row[0]  # idPlantillasValidacion
            ruta_json = row[1]  # RutaJSON

            # Ahora ruta_json es una cadena y se puede usar sin problemas
            resultado = validar_excel_con_cerberus(excel_path, ruta_json)
            flash(resultado['message'])

            if resultado['status'] == 'success':
                # Copia el archivo validado a la carpeta de validados
                validated_excel_path = os.path.join(app.config['VALIDATED_FOLDER'], file_excel.filename)
                shutil.copy(excel_path, validated_excel_path)

                # Guardar en la base de datos dbo.Validaciones
                conn = conectar_db()
                cursor = conn.cursor()

                id_proceso_admin = request.form.get("processSelect")
                # Validar si el usuario seleccionó un proceso válido
                if not id_proceso_admin:
                    flash("Error: No se seleccionó un proceso válido.", "error")
                    return redirect(url_for("validador"))
                try:
                    id_proceso_admin = int(id_proceso_admin)  # Convertir a entero
                except ValueError:
                    flash("Error: El proceso seleccionado no es válido.", "error")
                    return redirect(url_for("validador"))
                nombre_archivo = file_excel.filename[:50]
                cursor.execute("""
                    INSERT INTO dbo.Validaciones (idProcesoAdmin, idUsuario, FechaValidacion, idEstado, idPlantillasValidacion, nombreArchivo) 
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (id_proceso_admin, 1, datetime.now(), 1, id_plantilla_validacion, nombre_archivo)) 
                conn.commit()
                conn.close()

                flash(f"Archivo validado y guardado: {validated_excel_path}", "success")
            else:
                # Enviar reporte de errores por correo
                errores_detectados = resultado.get("errores", [])
                destinatario = "hectord.godoy@urosario.edu.co"  # Cambia esto al correo corporativo
                enviar_reporte_errores(errores_detectados, destinatario)
                flash("Se ha enviado un reporte de errores al correo corporativo.", "error")

            return redirect(url_for("validador"))
# Nueva ruta para cargar y guardar JSON
@app.route('/cargar_plantilla', methods=['GET', 'POST'])
def cargar_plantilla():
    conn = conectar_db()
    if not conn:
        flash("Error al conectar a la base de datos.", "error")
        return render_template('plantillas.html',procesos=[])
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT idProcesoAdmin, nombreProcesoAdmin FROM [dbo].[ProcesosAdministrativos] WHERE estadoProcesoAdmin IN ('Activo', 'Inactivo')")
        procesos = cursor.fetchall()
    except pyodbc.Error as e:
        flash(f"Error al obtener los archivos JSON o procesos: {str(e)}", "error")
        procesos = []
    finally:
        cursor.close()
        conn.close()

    if request.method == 'POST':
        # Verifica si se envió un archivo JSON
        if 'file_json' not in request.files:
            flash('No se seleccionó ningún archivo JSON.', "error")
            return redirect(url_for('cargar_plantilla'))
        
        file_json = request.files['file_json']
        
        # Verifica si el archivo tiene un nombre
        if file_json.filename == '':
            flash('Por favor seleccione un archivo JSON.', "error")
            return redirect(url_for('cargar_plantilla'))
        
        if 'processSelect' not in request.form:
            flash('Por favor seleccione un proceso administrativo.', "error")
            return redirect(url_for('cargar_plantilla'))
        idProcesoAdmin = request.form['processSelect']
        if file_json:
            # Guarda el archivo JSON subido
            json_path = os.path.join(app.config['UPLOAD_FOLDER'], file_json.filename)
            file_json.save(json_path)
            
            # Guardar el archivo JSON en la base de datos
            mensaje = subir_json(json_path,idProcesoAdmin)
            flash(mensaje)
            return redirect(url_for('cargar_plantilla'))
    
    # Renderiza la plantilla de json_handler
    return render_template('plantillas.html',procesos=procesos)

@app.route('/api/json_files', methods=['GET'])
def get_json_files():
    proceso_id = request.args.get('proceso_id')
    if not proceso_id:
        return jsonify({"error": "ID del proceso no proporcionado"}), 400

    conn = conectar_db()
    if not conn:
        return jsonify({"error": "Error al conectar a la base de datos"}), 500

    cursor = conn.cursor()
    try:
        # Consulta para obtener los JSON asociados al proceso seleccionado
        cursor.execute("""
            SELECT NombrePlantilla 
            FROM dbo.PlantillasValidacion 
            WHERE idProcesoAdmin = ? AND EstadoPlantilla = 'Activo'
        """, proceso_id)
        json_files = [{"NombrePlantilla": row.NombrePlantilla} for row in cursor.fetchall()]
        return jsonify(json_files)
    except pyodbc.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
    
@app.route('/obtener_fechas_json', methods=['GET'])
def obtener_fechas_json_route():
    nombre_plantilla = request.args.get('nombre_plantilla')
    if not nombre_plantilla:
        return jsonify({"error": "Nombre de plantilla no proporcionado"}), 400

    fechas = obtener_fechas_json(nombre_plantilla)
    return jsonify({"fechas": fechas})

# Determina la ruta base (la carpeta donde se encuentra este archivo)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# Define las carpetas relativas para guardar archivos
UPLOAD_FOLDER = os.path.join(BASE_DIR, "Plantillas.json", "Entrada")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "Plantillas.json", "Salida")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)




# ---------------------------------------------------
# Ruta: Página para elegir el archivo Excel (modal)
# ---------------------------------------------------
@app.route('/crear_plantilla')
def index():
    html_template = """
  <!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Validador de Archivo Excel</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    :root {
      --azul-oscuro: #1e3a8a;
      --rojo-primario: #e11d48;
      --rojo-oscuro: #b30000;
      --rojo-bootstrap: #dc3545;
    }
    
    body {
        background: linear-gradient(135deg, var(--azul-oscuro), var(--rojo-primario));
        color: #fff;
        margin: 0;
        padding: 0;
        display: flex;
        flex-direction: column;
        min-height: 100vh;
    }
    
    .btn-primary {
        background-color: var(--azul-oscuro);
        border-color: var(--azul-oscuro);
    }
    
    .btn-primary:hover {
        background-color: var(--rojo-primario);
        border-color: var(--rojo-primario);
    }
    
    .titulo-rojo {
        background-color: var(--rojo-bootstrap);
        color: white;
        padding: 12px;
        border-radius: 8px;
        width: 100%;
        text-align: center;
        margin-bottom: 25px;
        font-size: 1.25rem;
    }
    
    .file-upload-container {
        background-color: white;
        padding: 25px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .main-content {
        flex: 1;
        display: flex;
        flex-direction: column;
        justify-content: center;
        padding: 20px 0;
    }
    
    header {
        background-color: var(--rojo-bootstrap);
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    footer {
        background-color: var(--rojo-oscuro);
        color: white;
        padding: 15px 0;
        margin-top: auto;
    }
    
    .logo-header {
        height: 70px;
        transition: transform 0.3s;
    }
    
    .logo-header:hover {
        transform: scale(1.05);
    }
    
    #nombreArchivo {
        min-height: 24px;
        margin-top: 8px;
    }
    
    .form-control:focus {
        border-color: var(--azul-oscuro);
        box-shadow: 0 0 0 0.25rem rgba(30, 58, 138, 0.25);
    }
  </style>
</head>
<body>
    <header class="text-white py-3">
        <div class="container d-flex justify-content-between align-items-center">
            <img src="{{ url_for('static', filename='logoBlanco.png') }}" alt="Logo Universidad del Rosario" class="logo-header">
            
        </div>
    </header>

    <main class="main-content">
        <div class="container">
            <div class="row justify-content-center">
                <div class="col-lg-6 col-md-8">
                    <div class="titulo-rojo">Seleccionar Archivo Excel</div>
                    
                    <div class="file-upload-container">
                        <form method="POST" action="/upload_excel" enctype="multipart/form-data">
                            <div class="mb-4">
                                <label for="fileInput" class="form-label fw-bold">Seleccionar archivo</label>
                                <input type="file" name="file" id="fileInput" class="form-control form-control-lg" 
                                       accept=".xlsx, .xls" onchange="mostrarNombreArchivo(this)" required>
                                <div id="nombreArchivo" class="form-text text-muted">Sin archivos seleccionados</div>
                            </div>
                            <button type="submit" class="btn btn-primary btn-lg w-100 py-2">
                                Subir y Continuar
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </main>

    <footer class="text-center py-3">
        <div class="container">
            <p class="mb-0">© 2025 Universidad del Rosario. Todos los derechos reservados.</p>
        </div>
    </footer>

    <script>
        function mostrarNombreArchivo(input) {
            const nombreArchivo = document.getElementById('nombreArchivo');
            if (input.files && input.files[0]) {
                nombreArchivo.textContent = "Archivo seleccionado: " + input.files[0].name;
                nombreArchivo.classList.remove('text-muted');
                nombreArchivo.classList.add('text-success', 'fw-bold');
            } else {
                nombreArchivo.textContent = "Sin archivos seleccionados";
                nombreArchivo.classList.remove('text-success', 'fw-bold');
                nombreArchivo.classList.add('text-muted');
            }
        }
    </script>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>

    """
    return render_template_string(html_template)
# Definimos la variable global
uploaded_excel = None

@app.route('/upload_excel', methods=["POST"])
def upload_excel():
    if "file" not in request.files:
        return "No se envió archivo", 400
    file = request.files["file"]
    if file.filename == "":
        return "Nombre de archivo vacío", 400
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    # Guardamos la ruta del Excel en la sesión
    session["uploaded_excel"] = filepath
    print("Archivo subido en:", filepath)  # Para depuración
    return redirect(url_for('mostrar_tabla'))

# Ruta: Mostrar la tabla editable del Excel (plantilla)
@app.route('/mostrar_tabla')
def mostrar_tabla():
    uploaded_excel = session.get("uploaded_excel")
    if not uploaded_excel or not os.path.exists(uploaded_excel):
        return "No se ha subido ningún archivo Excel.", 400

    # Cargar el Excel y elegir la hoja ("Clientes" o la primera)
    xls = pd.ExcelFile(uploaded_excel)
    if "Clientes" in xls.sheet_names:
        df = pd.read_excel(uploaded_excel, sheet_name="Clientes")
    else:
        df = pd.read_excel(uploaded_excel, sheet_name=xls.sheet_names[0])
    
    # Convertir columnas de fecha a texto con formato dd/mm/yyyy
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.strftime('%d/%m/%Y')
    
    # Transponer para obtener los encabezados como índice y crear DataFrame
    df_transpuesto = df.T
    df_campos = pd.DataFrame(df_transpuesto.index, columns=["Nombre"])
    # Añadir tres columnas vacías para configurar opciones (Type, Required y Regex)
    df_campos["1"] = ""
    df_campos["2"] = ""
    df_campos["3"] = ""
    rows = df_campos.to_dict(orient='records')
    original_json = json.dumps(rows, ensure_ascii=False)
    
    nombre_archivo = os.path.basename(uploaded_excel)
    
    html_template = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
       <meta charset="UTF-8">
       <meta name="viewport" content="width=device-width, initial-scale=1">
       <title>Editar Plantilla</title>
       <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
    :root {
      --azul-oscuro: #1e3a8a;
      --rojo-primario: #e11d48;
      --rojo-oscuro: #b30000;
      --rojo-bootstrap: #dc3545;
      --rojo-claro: #ffcccc;
    }
    
    body {
        background: linear-gradient(135deg, var(--azul-oscuro), var(--rojo-primario));
        color: #fff;
        margin: 0;
        padding: 0;
        display: flex;
        flex-direction: column;
        min-height: 100vh;
    }
    
    .btn-primary {
        background-color: var(--azul-oscuro);
        border-color: var(--azul-oscuro);
    }
    
    .btn-primary:hover {
        background-color: var(--rojo-primario);
        border-color: var(--rojo-primario);
    }
    
    header {
        background-color: var(--rojo-bootstrap);
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    footer {
        background-color: var(--rojo-oscuro);
        color: white;
        padding: 15px 0;
        margin-top: auto;
    }
    
    .logo-header {
        height: 70px;
        transition: transform 0.3s;
    }
    
    .logo-header:hover {
        transform: scale(1.05);
    }
    
    /* Estilos para la tabla */
    #editableTable {
        border: 2px solid #000 !important;
        background-color: transparent;
        margin: 20px auto;
    }
    
    #editableTable th, 
    #editableTable td {
        border: 1px solid #000 !important;
        background-color: var(--rojo-claro);
        color: #000;
    }
    
    #editableTable th {
        background-color: var(--rojo-bootstrap);
        color: white;
        font-weight: bold;
    }
    
    #editableTable select {
        background-color: white;
        border: 1px solid #000;
    }
    
    .texto-blanco {
        color: white !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
    }
    
    .header-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 0;
    }
    
    .main-content {
        padding: 20px;
    }
   </style>
    </head>
    <body>
    <body>
    <!-- Encabezado con logo -->
    <header class="text-white">
        <div class="container header-content">
            <img src="{{ url_for('static', filename='logoBlanco.png') }}" alt="Logo Universidad del Rosario" class="logo-header">
           
        </div>
    </header>

        <main class="container my-4">
        <div class="table-container">
            <div class="info-archivo texto-negro">
                <h1 class="texto-negro">Archivo Seleccionado: {{ nombre_archivo }}</h1>
                <p class="texto-negro">Ruta Del Archivo Excel: {{ uploaded_excel }}</p>
            </div>
            
            <table id="editableTable" class="table">
                <thead>
                    <tr>
                 <th>Nombre</th>
                 <th>Type</th>
                 <th>Required</th>
                 <th>Regex</th>
               </tr>
             </thead>
             <tbody>
               {% for row in rows %}
                 <tr>
                   <td>{{ row["Nombre"] }}</td>
                   <td>
                     <select class="form-select">
                       <option value="string">string</option>
                       <option value="date">date</option>
                       <option value="number">number</option>
                       <option value="integer">integer</option>
                     </select>
                   </td>
                   <td>
                     <select class="form-select">
                       <option value="obligatorio">obligatorio</option>
                       <option value="opcional">opcional</option>
                     </select>
                   </td>
                   <td>
                     <select class="form-select">
                       <option value="FormatoFechaDiaMesAño">FormatoFechaDiaMesAño</option>
                       <option value="FormatoCorreoElectronico">FormatoCorreoElectronico</option>
                       <option value="FormatoNumeroEntero">FormatoNumeroEntero</option>
                     </select>
                   </td>
                 </tr>
               {% endfor %}
             </tbody>
          </table>
         </div>
          <div class="text-center mt-4">
              <button id="cargarBtn" class="btn btn-primary">Cargar Plantilla</button>
          </div>
        </main> 
       
           <footer class="text-center py-3">
        <div class="container">
            <p class="mb-0">© 2025 Universidad del Rosario. Todos los derechos reservados.</p>
        </div>
    </footer>

       
       <script>
    var originalData = {{ original_json|safe }};
    
    function getEditedData() {
        var edited = [];
        var table = document.getElementById("editableTable");
        var rows = table.querySelector("tbody").querySelectorAll("tr");
        rows.forEach(function(row) {
            var cells = row.querySelectorAll("td");
            var config = {
                "Nombre": cells[0].innerText.trim(),
                "1": cells[1].querySelector("select").value,
                "2": cells[2].querySelector("select").value,
                "3": cells[3].querySelector("select").value
            };
            edited.push(config);
        });
        return edited;
    }
    
    document.getElementById("cargarBtn").addEventListener("click", function() {
        var editedData = getEditedData();
        var payload = { "editado": editedData };
        
        fetch("/guardar_plantilla", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        })
        .then(response => response.json())
        .then(result => {
            if(result.success) {
                alert("Plantilla guardada exitosamente.");
                window.location.href = result.descarga_editado;
            } else {
                // Muestra el mensaje de error completo en una alerta
                alert(result.error);
                console.log("Detalles del error:", result);
            }
        })
        .catch(error => {
            console.error("Error:", error);
            alert("Error al enviar los datos al servidor.");
        });
    });
</script>
       <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>

    """
    return render_template_string(html_template, rows=rows, original_json=original_json, nombre_archivo=nombre_archivo, uploaded_excel=uploaded_excel)

# Ruta: Guardar el JSON editado y permitir su descarga (y guardar en la BD)
@app.route('/guardar_plantilla', methods=["POST"])
def guardar_plantilla():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No se recibieron datos"}), 400

        editado = data.get("editado")
        if not editado:
            return jsonify({"success": False, "error": "No se proporcionaron datos editados"}), 400

        uploaded_excel = data.get("uploaded_excel") or session.get("uploaded_excel")
        if not uploaded_excel or not os.path.exists(uploaded_excel):
            return jsonify({"success": False, "error": "Archivo Excel no encontrado"}), 400

        # Procesar Excel
        xls = pd.ExcelFile(uploaded_excel)
        sheet = "Clientes" if "Clientes" in xls.sheet_names else xls.sheet_names[0]
        df_full = pd.read_excel(uploaded_excel, sheet_name=sheet)
        for col in df_full.columns:
            if pd.api.types.is_datetime64_any_dtype(df_full[col]):
                df_full[col] = df_full[col].dt.strftime('%d/%m/%Y')

        # Validaciones
        validation_errors = []
        conn = conectar_db()
        try:
            cursor = conn.cursor()
            for config in editado:
                header = config.get("Nombre")
                option = config.get("3")
                if not header or not option:
                    validation_errors.append("Configuración incompleta")
                    continue

                cursor.execute("""
                    SELECT Expresion_Regular
                    FROM dbo.ExpresionesRegulares
                    WHERE nombre_ExpresionRegular = ? 
                    AND estado_ExpresionRegular = 'activo'
                """, (option,))
                result = cursor.fetchone()
                if result:
                    try:
                        regex = result[0].replace("\\\\", "\\")
                        re.compile(regex)
                        config["ExpresionRegex"] = regex
                        if header in df_full.columns:
                            col_values = df_full[header].dropna().astype(str)
                            for idx, value in col_values.items():
                                if not re.fullmatch(regex, value):
                                    validation_errors.append(f"Fila {idx+2}: Valor '{value}' no cumple el formato")
                    except re.error as e:
                        validation_errors.append(f"Regex inválido para {option}: {str(e)}")
                else:
                    config["ExpresionRegex"] = ""
            if validation_errors:
                return jsonify({
                    "success": False,
                    "error": "Errores de validación",
                    "details": validation_errors
                }), 400

            # Guardar JSON en archivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_base = os.path.splitext(os.path.basename(uploaded_excel))[0]
            nombre_archivo = f"{nombre_base}_{timestamp}.json"
            ruta_archivo = os.path.join(OUTPUT_FOLDER, nombre_archivo)
            with open(ruta_archivo, "w", encoding="utf-8") as f:
                json.dump(editado, f, ensure_ascii=False, indent=2)

            # Recuperar idProcesoAdmin enviado; si no se envía, usar 0
            id_proceso = data.get("idProcesoAdmin")
            if not id_proceso:
                id_proceso = 0

            usuario = session.get('user', 'default_user')
            
            # Insertar incluyendo idProcesoAdmin
            cursor.execute("""
                INSERT INTO dbo.PlantillasValidacion 
                (idProcesoAdmin, NombrePlantilla, ContenidoJSON, RutaJSON, 
                 FechaCarga, FechaUltimaModificacion, UsuarioCargue, EstadoPlantilla)
                VALUES (?, ?, ?, ?, GETDATE(), GETDATE(), ?, ?)
            """, (
                id_proceso,
                nombre_archivo,
                json.dumps(editado, ensure_ascii=False),
                ruta_archivo,
                usuario,
                'activo'
            ))
            conn.commit()
            return jsonify({
                "success": True,
                "message": "Plantilla guardada correctamente",
                "download_url": url_for('descargar', filename=nombre_archivo)
            })
        except Exception as e:
            conn.rollback()
            return jsonify({"success": False, "error": f"Error en base de datos: {str(e)}"}), 500
        finally:
            cursor.close()
            conn.close()
    except Exception as e:
        return jsonify({"success": False, "error": f"Error interno: {str(e)}"}), 500

# Ruta: Descargar el JSON editado
@app.route('/descargar/<filename>')
def descargar(filename):
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)