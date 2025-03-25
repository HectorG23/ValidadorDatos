import json
import pandas as pd
import cerberus
from datetime import datetime

def convertir_tipos(df, tipos_por_columna):
    df_convertido = df.copy()
    for columna, tipo in tipos_por_columna.items():
        if columna in df.columns:
            if tipo == 'numero':
                # Eliminar espacios y caracteres no numéricos
                df_convertido[columna] = df[columna].astype(str).str.strip().str.replace(r'\D', '', regex=True)
                df_convertido[columna] = pd.to_numeric(df_convertido[columna], errors='coerce')
            elif tipo == 'fecha':
                df_convertido[columna] = pd.to_datetime(df[columna], errors='coerce')
    return df_convertido

def validar_excel_con_cerberus(archivo_excel, archivo_schema):
    with open(archivo_schema, 'r', encoding='utf-8') as f:
        schema = json.load(f)

    excel = pd.ExcelFile(archivo_excel)
    errores = []

    for hoja, configuracion in schema['hojas'].items():
        if hoja in excel.sheet_names:
            df = excel.parse(hoja)
            
            # Eliminar filas completamente vacías
            df = df.dropna(how='all')
            
            # Mapeo de tipos de datos por columna
            tipos_por_columna = {campo: config.get('tipo', 'texto') 
                                for campo, config in configuracion.items()}
            
            # Convertir los datos según el tipo especificado
            df_convertido = convertir_tipos(df, tipos_por_columna)
            
            # Preparar reglas para Cerberus
            reglas = {}
            for campo, config in configuracion.items():
                if campo in df.columns:  # Solo crear reglas para columnas que existen
                    reglas[campo] = {}
                    tipo_dato = config.get('tipo', 'texto')
                    
                    # Configurar reglas según el tipo de dato
                    if tipo_dato == 'integer':
                        reglas[campo]['type'] = 'integer'
                        if 'min' in config:
                            reglas[campo]['min'] = config['min']
                        if 'max' in config:
                            reglas[campo]['max'] = config['max']
                    elif tipo_dato == 'string':
                        reglas[campo]['type'] = 'string'
                        if 'minlength' in config:
                            reglas[campo]['minlength'] = config['minlength']
                        if 'maxlength' in config:
                            reglas[campo]['maxlength'] = config['maxlength']
                        if 'regex' in config:
                            reglas[campo]['regex'] = config['regex']
                    elif tipo_dato == 'email':
                        reglas[campo]['type'] = 'string'
                        reglas[campo]['regex'] = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                    
                    # Configurar si es obligatorio o no
                    if 'required' in config:
                        reglas[campo]['required'] = config['required']
                    else:
                        # Por defecto, no requerir el campo
                        reglas[campo]['required'] = False
                        
                    # Permitir valores nulos si el campo no es obligatorio
                    if not reglas[campo].get('required', False):
                        reglas[campo]['nullable'] = True
                        
                    if 'allowed' in config:
                        reglas[campo]['allowed'] = config['allowed']
                    
                    # Guardar mensaje de error personalizado
                    reglas[campo]['error_message'] = config.get('error_message', f'Error en el campo {campo}')
            
            # Separar mensajes de error para Cerberus
            reglas_sin_error_message = {
                campo: {k: v for k, v in reglas[campo].items() if k != 'error_message'} 
                for campo in reglas
            }
            
            # Convertir a diccionarios para validación
            data = df_convertido.to_dict(orient='records')
            
            # Preparar validador
            v = cerberus.Validator(reglas_sin_error_message, allow_unknown=True)
            
            # Validar cada fila no vacía
            for i, fila in enumerate(data):
                # Verificar si la fila tiene al menos un valor no nulo
                if any(value is not None and pd.notna(value) for value in fila.values()):
                    # Solo validar campos que tienen datos
                    fila_a_validar = {k: v for k, v in fila.items() if pd.notna(v) and k in reglas}
                    
                    if not v.validate(fila_a_validar):
                        fila_errores = [
                            f"{campo}: {reglas[campo]['error_message']}" 
                            for campo in v.errors if campo in reglas
                        ]
                        if fila_errores:  # Solo agregar si hay errores
                            errores.append({
                                "hoja": hoja, 
                                "fila": i + 2,  # +2 por encabezado y índice 0
                                "errores": fila_errores
                            })

    # Preparar respuesta final
    if errores:
        mensaje = "Se encontraron errores:\n" + "\n".join([
            f"Hoja: {error['hoja']}, Fila: {error['fila']}, Errores: {', '.join(error['errores'])}" 
            for error in errores
        ])
        return {"status": "error", "message": mensaje}
    else:
        return {"status": "success", "message": "El archivo Excel es válido."}