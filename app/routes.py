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
def inicio_sesion():
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

@app.route('/validador', methods=['POST'])
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




# Variable global para almacenar la ruta completa del Excel subido
uploaded_excel = None

# Página inicial: se muestra un modal para elegir el archivo Excel
@app.route('/crear_plantilla')
def index():
    html_template = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>Seleccionar Archivo Excel</title>
      <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
      <script>
        function mostrarNombreArchivo(input) {
          var file = input.files[0];
          if (file) {
            document.getElementById('nombreArchivo').innerText = "Archivo seleccionado: " + file.name;
          } else {
            document.getElementById('nombreArchivo').innerText = "";
          }
        }
        document.addEventListener("DOMContentLoaded", function() {
          // Forzamos la apertura del modal
          var modal = new bootstrap.Modal(document.getElementById('modalSeleccionArchivo'));
          modal.show();
        });
      </script>
    </head>
    <body class="container my-5">
    
      <!-- Modal de selección de archivo -->
      <div class="modal fade show d-block" id="modalSeleccionArchivo" tabindex="-1" aria-hidden="false">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">Seleccionar Archivo Excel</h5>
            </div>
            <div class="modal-body">
              <form method="POST" action="/upload_excel" enctype="multipart/form-data">
                <input type="file" name="file" class="form-control mb-3" onchange="mostrarNombreArchivo(this)" required>
                <p id="nombreArchivo"></p>
                <button type="submit" class="btn btn-primary w-100">Subir y Continuar</button>
              </form>
            </div>
          </div>
        </div>
      </div>
      <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """
    return render_template_string(html_template)

# Ruta para subir el archivo Excel
@app.route('/upload_excel', methods=["POST"])
def upload_excel():
    global uploaded_excel
    if "file" not in request.files:
        return "No se envió archivo", 400
    file = request.files["file"]
    if file.filename == "":
        return "Nombre de archivo vacío", 400
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    uploaded_excel = filepath
    # Redirige a la siguiente página que muestra el contenido y la tabla editable
    return redirect(url_for('mostrar_tabla'))

# Página siguiente: se muestra el nombre, la ruta del Excel y se genera la tabla editable
@app.route('/mostrar_tabla')
def mostrar_tabla():
    global uploaded_excel
    if not uploaded_excel or not os.path.exists(uploaded_excel):
        return "No se ha subido ningún archivo Excel.", 400

    # Cargar el archivo Excel y determinar la hoja a usar
    xls = pd.ExcelFile(uploaded_excel)
    if "Clientes" in xls.sheet_names:
        df = pd.read_excel(uploaded_excel, sheet_name="Clientes")
    else:
        # Si no existe la hoja "Clientes", usamos la primera hoja
        df = pd.read_excel(uploaded_excel, sheet_name=xls.sheet_names[0])
    
    # Transponer para obtener los encabezados (nombres de campos) como índice
    df_transpuesto = df.T
    # Crear DataFrame con la columna "Nombre" a partir del índice
    df_campos = pd.DataFrame(df_transpuesto.index, columns=["Nombre"])
    # Añadir tres columnas vacías para opciones editables
    df_campos["1"] = ""
    df_campos["2"] = ""
    df_campos["3"] = ""
    rows = df_campos.to_dict(orient='records')
    original_json = json.dumps(rows, ensure_ascii=False)
    
    # Obtener el nombre y la ruta del archivo cargado (según se guardó en el servidor)
    nombre_archivo = os.path.basename(uploaded_excel)
    html_template = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
       <meta charset="UTF-8">
       <meta name="viewport" content="width=device-width, initial-scale=1">
       <title>Editar Plantilla</title>
       <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
       <div class="container my-5">
          <h1>Archivo Cargado: {{ nombre_archivo }}</h1>
          <p>Ruta completa: {{ uploaded_excel }}</p>
          <h2>Excel - Campos y Opciones</h2>
          <table id="editableTable" class="table table-bordered">
             <thead>
               <tr>
                 <th>Nombre</th>
                 <th>1</th>
                 <th>2</th>
                 <th>3</th>
               </tr>
             </thead>
             <tbody>
               {% for row in rows %}
                 <tr>
                   <!-- Columna 1: Nombre -->
                   <td>{{ row["Nombre"] }}</td>
                   
                   <!-- Columna 2: string/date/number/integer -->
                   <td>
                     <select class="form-select">
                       <option value="string">string</option>
                       <option value="date">date</option>
                       <option value="number">number</option>
                       <option value="integer">integer</option>
                     </select>
                   </td>
                   
                   <!-- Columna 3: obligatorio/opcional -->
                   <td>
                     <select class="form-select">
                       <option value="obligatorio">obligatorio</option>
                       <option value="opcional">opcional</option>
                     </select>
                   </td>
                   
                   <!-- Columna 4: FormatoFechaAñoMesDia, FormatoCorreoElectronico, FormatoNumeroEntero -->
                   <td>
                     <select class="form-select">
                       <option value="FormatoFechaAñoMesDia">FormatoFechaAñoMesDia</option>
                       <option value="FormatoCorreoElectronico">FormatoCorreoElectronico</option>
                       <option value="FormatoNumeroEntero">FormatoNumeroEntero</option>
                     </select>
                   </td>
                 </tr>
               {% endfor %}
             </tbody>
          </table>
          <div class="text-center mt-4">
              <button id="cargarBtn" class="btn btn-primary">Cargar Plantilla</button>
          </div>
       </div>
       
       <script>
         var originalData = {{ original_json|safe }};
         
         function getEditedData() {
           var edited = [];
           var table = document.getElementById("editableTable");
           var rows = table.getElementsByTagName("tbody")[0].getElementsByTagName("tr");
           
           for (var i = 0; i < rows.length; i++) {
             var cells = rows[i].getElementsByTagName("td");
             var rowData = {
               "Nombre": cells[0].innerText.trim(),
               "1": cells[1].querySelector("select").value,
               "2": cells[2].querySelector("select").value,
               // OJO: en la última columna, ahora tenemos un select (no un input number)
               "3": cells[3].querySelector("select").value
             };
             edited.push(rowData);
           }
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
               alert("Error: " + result.error);
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



# Guardar el JSON editado y permitir la descarga
@app.route('/guardar_plantilla', methods=["POST"])
def guardar_plantilla():
    try:
        data = request.get_json()
        editado = data.get("editado")  # Lista de diccionarios, cada uno con "Nombre", "1", "2" y "3"

        # Re-abrir el Excel completo para validar los datos reales
        xls = pd.ExcelFile(uploaded_excel)
        sheet = "Clientes" if "Clientes" in xls.sheet_names else xls.sheet_names[0]
        df_full = pd.read_excel(uploaded_excel, sheet_name=sheet)

        # Inicializamos un diccionario para acumular errores de validación
        validation_errors = {}

        # Para cada configuración (fila de la plantilla), se obtiene el regex y se valida la columna correspondiente
        for config in editado:
            header = config["Nombre"]  # Se espera que este valor coincida con un encabezado de df_full
            option = config["3"]  # Ej: "FormatoNumeroEntero", etc.

            # Consultar el regex correspondiente en la BD
            conn = conectar_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Expresion_Regular
                FROM dbo.ExpresionesRegulares
                WHERE nombre_ExpresionRegular = ?
                AND estado_ExpresionRegular = 'activo'
            """, option)

            result = cursor.fetchone()
            cursor.close()
            conn.close()

            if result:
                regex = result[0]

                # Normalizar expresión regular (eliminar escapes dobles si existen)
                regex = regex.replace("\\\\", "\\")

                # Validar que la expresión sea válida en Python
                try:
                    re.compile(regex)
                    config["ExpresionRegex"] = regex  # Se añade la expresión al JSON final
                except re.error as e:
                    return jsonify({
                        "success": False,
                        "error": f"Expresión inválida en la BD: {str(e)}",
                        "regex": regex
                    }), 400

                # Validar si el encabezado existe en el Excel completo
                if header in df_full.columns:
                    # Convertir todos los valores a cadena y eliminar NaN
                    col_values = df_full[header].dropna().astype(str)
                    for idx, value in col_values.items():
                        if not re.fullmatch(regex, value):
                            # Acumular error en esa columna
                            validation_errors.setdefault(header, []).append(
                                f"Fila {idx+2}: valor '{value}' no cumple la expresión {regex}"
                            )
                else:
                    validation_errors[header] = f"La columna '{header}' no se encontró en el Excel."
            else:
                # Si no se encontró la expresión, se asigna vacío (o se puede tratar como error)
                config["ExpresionRegex"] = ""

        # Si existen errores, se retorna el JSON con detalles
        if validation_errors:
            return jsonify({
                "success": False,
                "error": "Errores de validación",
                "details": validation_errors
            }), 400

        # Si todo es correcto, guardar el JSON final
        editado_filename = f"{os.path.splitext(os.path.basename(uploaded_excel))[0]}.json"
        full_path = os.path.join(OUTPUT_FOLDER, editado_filename)
        with open(full_path, "w", encoding="utf-8") as f:
            json.dump(editado, f, ensure_ascii=False, indent=2)

        return jsonify({
            "success": True,
            "descarga_editado": url_for('descargar', filename=editado_filename)
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Endpoint para descargar el JSON editado
@app.route('/descargar/<filename>')
def descargar(filename):
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)
