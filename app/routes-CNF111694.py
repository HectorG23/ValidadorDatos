from flask import render_template, request, redirect, url_for, flash, jsonify
from app.app import app
import pyodbc
from app.json_handler import conectar_db, obtener_nombres_json, subir_json
from app.validations import validar_excel_con_cerberus
from app.json_handler import obtener_fechas_json
import shutil
import os

@app.route('/')
def principal():
    conn = conectar_db()
    if not conn:
        flash("Error al conectar a la base de datos.")
        return render_template('index.html', json_files=[])

    cursor = conn.cursor()
    try:
        cursor.execute("SELECT NombrePlantilla FROM [dbo].[PlantillasValidacion] WHERE EstadoPlantilla = 'Activo'")
        json_files = [row.NombrePlantilla for row in cursor.fetchall()]
    except pyodbc.Error as e:
        flash(f"Error al obtener los archivos JSON: {str(e)}")
        json_files = []
    finally:
        cursor.close()
        conn.close()
    # Renderiza la plantilla principal y pasa la lista de archivos JSON
    return render_template('index.html', json_files=json_files)

@app.route('/validador', methods=['POST'])
def validador():
    # Verifica si los archivos están en la solicitud
    if 'file_excel' not in request.files or 'jsonSelect' not in request.form:
        flash('No file part', "error")
        return redirect(url_for('principal'))
    
    file_excel = request.files['file_excel']
    jsonSelect = request.form['jsonSelect']
    
    # Verifica si los archivos tienen nombre
    if file_excel.filename == '' or jsonSelect == '':
        flash('Por favor seleccione ambos archivos', "error")
        return redirect(url_for('principal'))
    
    if file_excel and jsonSelect:
        # Guarda el archivo Excel subido
        excel_path = os.path.join(app.config['UPLOAD_FOLDER'], file_excel.filename)
        file_excel.save(excel_path)
        
        # Obtén la ruta del archivo JSON desde la base de datos
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT RutaJSON FROM [dbo].[PlantillasValidacion] WHERE NombrePlantilla = ?", jsonSelect)
        json_path = cursor.fetchone().RutaJSON
        cursor.close()
        conn.close()
        
        # Valida el archivo Excel con el archivo JSON usando la función del proyecto
        resultado = validar_excel_con_cerberus(excel_path, json_path)
        
        flash(resultado['message'])  # Muestra el mensaje de resultado
        
        if resultado['status'] == 'success':
            # Copia el archivo validado a la carpeta de validados
            validated_excel_path = os.path.join(app.config['VALIDATED_FOLDER'], file_excel.filename)
            shutil.copy(excel_path, validated_excel_path)
            flash(f'Archivo validado y copiado a {validated_excel_path}', "success")
        
        return redirect(url_for('principal'))

# Nueva ruta para cargar y guardar JSON
@app.route('/cargar_plantilla', methods=['GET', 'POST'])
def cargar_plantilla():
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
        
        if file_json:
            # Guarda el archivo JSON subido
            json_path = os.path.join(app.config['UPLOAD_FOLDER'], file_json.filename)
            file_json.save(json_path)
            
            # Guardar el archivo JSON en la base de datos
            mensaje = subir_json(json_path)
            flash(mensaje)
            return redirect(url_for('cargar_plantilla'))
    
    # Renderiza la plantilla de json_handler
    return render_template('plantillas.html')

@app.route('/api/json_files', methods=['GET'])
def get_json_files():
    try:
        json_files = obtener_nombres_json()
        return jsonify(json_files)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/obtener_fechas_json', methods=['GET'])
def obtener_fechas_json_route():
    nombre_plantilla = request.args.get('nombre_plantilla')
    if not nombre_plantilla:
        return jsonify({"error": "Nombre de plantilla no proporcionado"}), 400

    fechas = obtener_fechas_json(nombre_plantilla)
    return jsonify({"fechas": fechas})    