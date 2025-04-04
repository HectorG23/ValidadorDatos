from flask import Flask, request, jsonify, render_template_string
import pyodbc
import os
from config import Config  # Importamos la configuración centralizada

app = Flask(__name__)
app.config.from_object(Config)  # Cargamos la configuración

# Configuración de la base de datos usando la clase Config
def get_db_connection():
    try:
        conn_str = f"DRIVER={Config.DB_CONFIG['driver']};" \
                   f"SERVER={Config.DB_CONFIG['server']};" \
                   f"DATABASE={Config.DB_CONFIG['database']};" \
                   f"Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
        
        # Conexión usando autenticación integrada de Windows (para desarrollo local)
        conn = pyodbc.connect(conn_str, autocommit=True)
        
        return conn
    except Exception as e:
        print(f"Error al conectar a la base de datos: {str(e)}")
        return None

# Plantilla HTML completa con JavaScript integrado
HTML_TEMPLATE = r"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CRUD Expresiones Regulares</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css" rel="stylesheet">
    <style>
        .action-buttons { white-space: nowrap; }
        .table-responsive { overflow-x: auto; }
        code { color: #d63384; background-color: #f8f9fa; padding: 2px 4px; border-radius: 4px; }
        .badge { font-size: 0.9em; padding: 5px 10px; }
    </style>
</head>
<body>
    <div class="container mt-5">
        <h1 class="mb-4">Administración de Expresiones Regulares</h1>
        
        <!-- Formulario para crear/editar -->
        <div class="card mb-4">
            <div class="card-header bg-primary text-white">
                <h5 id="form-title">Nueva Expresión</h5>
            </div>
            <div class="card-body">
                <form id="expression-form">
                    <input type="hidden" id="expression-id">
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Nombre</label>
                            <input type="text" class="form-control" id="nombre" required 
                                   placeholder="Ej: FormatoFechaDDMMYYYY">
                        </div>
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Estado</label>
                            <select class="form-select" id="estado" required>
                                <option value="activo">Activo</option>
                                <option value="inactivo">Inactivo</option>
                            </select>
                        </div>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Descripción</label>
                        <input type="text" class="form-control" id="descripcion" required 
                               placeholder="Ej: Valida fechas en formato DD/MM/YYYY">
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Expresión Regular</label>
                        <input type="text" class="form-control" id="expresion" required 
                               placeholder="Ej: ^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/\d{4}$">
                        <small class="text-muted">Ejemplo para fechas: ^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/\d{4}$</small>
                    </div>
                    <div class="d-flex justify-content-between">
                        <button type="submit" class="btn btn-primary">
                            <i class="bi bi-save"></i> Guardar
                        </button>
                        <button type="button" class="btn btn-secondary" id="cancel-edit" style="display:none;">
                            <i class="bi bi-x-circle"></i> Cancelar
                        </button>
                    </div>
                </form>
            </div>
        </div>

        <!-- Tabla de expresiones -->
        <div class="card">
            <div class="card-header bg-dark text-white">
                <h5>Listado de Expresiones</h5>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-striped table-hover">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Nombre</th>
                                <th>Descripción</th>
                                <th>Expresión</th>
                                <th>Estado</th>
                                <th>Acciones</th>
                            </tr>
                        </thead>
                        <tbody id="expressions-table">
                            <!-- Los datos se cargarán aquí con JavaScript -->
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <!-- Scripts de Bootstrap y Font Awesome -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    
    <!-- JavaScript para manejar el CRUD -->
    <script>
        // Cargar expresiones al iniciar
        document.addEventListener('DOMContentLoaded', function() {
            loadExpressions();
            
            // Manejar envío del formulario
            document.getElementById('expression-form').addEventListener('submit', function(e) {
                e.preventDefault();
                saveExpression();
            });
            
            // Manejar cancelar edición
            document.getElementById('cancel-edit').addEventListener('click', resetForm);
        });

        // Función para cargar todas las expresiones
        function loadExpressions() {
            fetch('/api/expresiones')
                .then(response => {
                    if (!response.ok) throw new Error('Error al cargar datos');
                    return response.json();
                })
                .then(data => {
                    const table = document.getElementById('expressions-table');
                    table.innerHTML = '';
                    
                    if (data.length === 0) {
                        table.innerHTML = `
                            <tr>
                                <td colspan="6" class="text-center text-muted py-4">
                                    No hay expresiones regulares registradas
                                </td>
                            </tr>`;
                        return;
                    }
                    
                    data.forEach(expr => {
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td>${expr.id_ExpressionRegular}</td>
                            <td>${expr.nombre_ExpressionRegular}</td>
                            <td>${expr.description_ExpressionRegular}</td>
                            <td><code>${expr.expression_Regular}</code></td>
                            <td>
                                <span class="badge ${expr.estado_ExpressionRegular === 'activo' ? 'bg-success' : 'bg-secondary'}">
                                    ${expr.estado_ExpressionRegular}
                                </span>
                            </td>
                            <td class="action-buttons">
                                <button class="btn btn-sm btn-warning me-2" onclick="editExpression(${expr.id_ExpressionRegular})">
                                    <i class="bi bi-pencil"></i> Editar
                                </button>
                                <button class="btn btn-sm btn-danger" onclick="deleteExpression(${expr.id_ExpressionRegular})">
                                    <i class="bi bi-trash"></i> Eliminar
                                </button>
                            </td>
                        `;
                        table.appendChild(row);
                    });
                })
                .catch(error => {
                    console.error('Error:', error);
                    showAlert('Error al cargar las expresiones: ' + error.message, 'danger');
                });
        }

        // Función para guardar o actualizar una expresión
        function saveExpression() {
            const id = document.getElementById('expression-id').value;
            const url = id ? `/api/expresiones/${id}` : '/api/expresiones';
            const method = id ? 'PUT' : 'POST';
            
            const data = {
                nombre: document.getElementById('nombre').value,
                descripcion: document.getElementById('descripcion').value,
                expresion: document.getElementById('expresion').value,
                estado: document.getElementById('estado').value
            };

            // Validación simple
            if (!data.nombre || !data.expresion) {
                showAlert('Nombre y Expresión son campos requeridos', 'warning');
                return;
            }

            fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            })
            .then(response => {
                if (!response.ok) throw new Error(response.statusText);
                return response.json();
            })
            .then(() => {
                resetForm();
                loadExpressions();
                showAlert('Operación realizada con éxito', 'success');
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('Error al guardar: ' + error.message, 'danger');
            });
        }

        // Función para editar una expresión
        function editExpression(id) {
            fetch(`/api/expresiones/${id}`)
                .then(response => {
                    if (!response.ok) throw new Error('Expresión no encontrada');
                    return response.json();
                })
                .then(data => {
                    // Llenar el formulario con los datos
                    document.getElementById('expression-id').value = data.id_ExpressionRegular;
                    document.getElementById('nombre').value = data.nombre_ExpressionRegular;
                    document.getElementById('descripcion').value = data.description_ExpressionRegular;
                    document.getElementById('expresion').value = data.expression_Regular;
                    document.getElementById('estado').value = data.estado_ExpressionRegular;
                    
                    // Actualizar UI
                    document.getElementById('form-title').textContent = 'Editar Expresión';
                    document.getElementById('cancel-edit').style.display = 'inline-block';
                    document.getElementById('nombre').focus();
                })
                .catch(error => {
                    console.error('Error:', error);
                    showAlert('Error al cargar expresión: ' + error.message, 'danger');
                });
        }

        // Función para eliminar una expresión
        function deleteExpression(id) {
            if (confirm('¿Estás seguro de eliminar esta expresión regular?')) {
                fetch(`/api/expresiones/${id}`, {
                    method: 'DELETE'
                })
                .then(response => {
                    if (!response.ok) throw new Error('Error al eliminar');
                    return response.json();
                })
                .then(() => {
                    loadExpressions();
                    showAlert('Expresión eliminada correctamente', 'success');
                })
                .catch(error => {
                    console.error('Error:', error);
                    showAlert('Error al eliminar: ' + error.message, 'danger');
                });
            }
        }

        // Función para resetear el formulario
        function resetForm() {
            document.getElementById('expression-form').reset();
            document.getElementById('expression-id').value = '';
            document.getElementById('form-title').textContent = 'Nueva Expresión';
            document.getElementById('cancel-edit').style.display = 'none';
        }

        // Función para mostrar alertas
        function showAlert(message, type) {
            const alertDiv = document.createElement('div');
            alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 end-0 m-3`;
            alertDiv.style.zIndex = '1000';
            alertDiv.role = 'alert';
            alertDiv.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            `;
            
            document.body.appendChild(alertDiv);
            
            // Eliminar la alerta después de 5 segundos
            setTimeout(() => {
                alertDiv.remove();
            }, 5000);
        }
    </script>
</body>
</html>
"""

# Rutas de la API
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/expresiones', methods=['GET', 'POST'])
def handle_expressions():
    if request.method == 'GET':
        try:
            conn = get_db_connection()
            if not conn:
                return jsonify({"error": "No se pudo conectar a la base de datos"}), 500
                
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM [dbo].[ExpresionesRegulares]")
            columns = [column[0] for column in cursor.description]
            result = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return jsonify(result)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            if conn:
                conn.close()
    elif request.method == 'POST':
        try:
            data = request.get_json()
            if not data or 'nombre' not in data or 'expresion' not in data:
                return jsonify({"error": "Datos incompletos"}), 400

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO [dbo].[ExpresionesRegulares] 
                (nombre_ExpressionRegular, description_ExpressionRegular, expression_Regular, estado_ExpressionRegular)
                VALUES (?, ?, ?, ?)
            """, data['nombre'], data.get('descripcion', ''), data['expresion'], data.get('estado', 'activo'))
            conn.commit()
            return jsonify({
                "message": "Expresión creada exitosamente", 
                "id": cursor.execute("SELECT SCOPE_IDENTITY()").fetchval()
            }), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            conn.close()

@app.route('/api/expresiones/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def handle_single_expression(id):
    if request.method == 'GET':
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM [dbo].[ExpresionesRegulares] WHERE id_ExpressionRegular = ?", id)
            row = cursor.fetchone()
            if row:
                columns = [column[0] for column in cursor.description]
                return jsonify(dict(zip(columns, row)))
            return jsonify({"error": "Expresión no encontrada"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            conn.close()
    
    elif request.method == 'PUT':
        try:
            data = request.get_json()
            if not data or 'nombre' not in data or 'expresion' not in data:
                return jsonify({"error": "Datos incompletos"}), 400

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE [dbo].[ExpresionesRegulares] 
                SET nombre_ExpressionRegular = ?,
                    description_ExpressionRegular = ?,
                    expression_Regular = ?,
                    estado_ExpressionRegular = ?
                WHERE id_ExpressionRegular = ?
            """, data['nombre'], data.get('descripcion', ''), data['expresion'], data.get('estado', 'activo'), id)
            
            if cursor.rowcount == 0:
                return jsonify({"error": "Expresión no encontrada"}), 404
                
            conn.commit()
            return jsonify({"message": "Expresión actualizada exitosamente"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            conn.close()
    
    elif request.method == 'DELETE':
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM [dbo].[ExpresionesRegulares] WHERE id_ExpressionRegular = ?", id)
            
            if cursor.rowcount == 0:
                return jsonify({"error": "Expresión no encontrada"}), 404
                
            conn.commit()
            return jsonify({"message": "Expresión eliminada exitosamente"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)