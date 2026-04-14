from flask import Flask, request, jsonify
import sys
import os
import xml.etree.ElementTree as ET
from collections import defaultdict

# Agregar backend al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from services.xml_service import (
    procesar_xml_configuracion,
    procesar_notas,
    obtener_db
)

app = Flask(__name__)

# Almacenamiento temporal de horarios por tutor (mientras no uses base de datos persistente)
horarios_por_tutor = defaultdict(dict)

# ── LOGIN ──────────────────────────────────────────
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    usuario = data.get('usuario')
    contrasenia = data.get('contrasenia')
    db = obtener_db()
    if usuario == 'AdminPPCYL2' and contrasenia == 'AdminPPCYL2771':
        return jsonify({'rol': 'admin', 'nombre': 'Administrador'}), 200
    if usuario in db['tutores']:
        t = db['tutores'][usuario]
        if t.contrasenia == contrasenia:
            return jsonify({'rol': 'tutor', 'nombre': t.nombre, 'id': usuario}), 200
    if usuario in db['estudiantes']:
        e = db['estudiantes'][usuario]
        if e.contrasenia == contrasenia:
            return jsonify({'rol': 'estudiante', 'nombre': e.nombre, 'id': usuario}), 200
    return jsonify({'error': 'Credenciales incorrectas'}), 401

# ── ADMIN ──────────────────────────────────────────
@app.route('/cargar-configuracion', methods=['POST'])
def cargar_configuracion():
    xml_string = request.data.decode('utf-8')
    salida = procesar_xml_configuracion(xml_string)
    return salida, 200, {'Content-Type': 'application/xml'}

@app.route('/usuarios', methods=['GET'])
def ver_usuarios():
    db = obtener_db()
    usuarios = []
    for id, t in db['tutores'].items():
        usuarios.append({'id': id, 'nombre': t.nombre, 'rol': 'tutor'})
    for id, e in db['estudiantes'].items():
        usuarios.append({'id': id, 'nombre': e.nombre, 'rol': 'estudiante'})
    return jsonify(usuarios), 200

# ── TUTOR - HORARIOS (CORREGIDO) ─────────────────────
@app.route('/horarios/<tutor_id>', methods=['POST', 'GET'])
def manejar_horarios(tutor_id):
    if request.method == 'POST':
        try:
            xml_string = request.data.decode('utf-8')
            if not xml_string:
                return jsonify({"error": "No se recibió XML"}), 400

            root = ET.fromstring(xml_string)
            tutor_horarios = {}

            for curso_elem in root.findall('curso'):
                codigo = curso_elem.get('codigo')
                if not codigo:
                    continue

                # Obtener día
                dia_elem = curso_elem.find('dia')
                dia = dia_elem.text.strip().upper() if dia_elem is not None and dia_elem.text else None

                # Obtener todo el texto dentro del <curso>
                texto_completo = ''.join(curso_elem.itertext()).strip()

                # Extraer HorarioI y HorarioF
                if 'HorarioI:' in texto_completo and 'HorarioF:' in texto_completo:
                    try:
                        # Extraer hora inicio
                        parte_inicio = texto_completo.split('HorarioI:')[1]
                        inicio = parte_inicio.split('HorarioF:')[0].strip()
                        
                        # Extraer hora fin
                        fin = texto_completo.split('HorarioF:')[1].strip()

                        if dia and inicio and fin:
                            if codigo not in tutor_horarios:
                                tutor_horarios[codigo] = {}
                            tutor_horarios[codigo][dia] = f"{inicio} - {fin}"
                    except:
                        continue

            # Guardar en memoria
            horarios_por_tutor[tutor_id] = tutor_horarios

            return jsonify({'mensaje': 'Horarios cargados correctamente'}), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # GET: Devolver horarios al Django
    elif request.method == 'GET':
        tutor_data = horarios_por_tutor.get(tutor_id, {})

        horarios_formateados = {}
        for codigo, dias_dict in tutor_data.items():
            horarios_formateados[codigo] = {
                'LUNES':     dias_dict.get('LUNES', ''),
                'MARTES':    dias_dict.get('MARTES', ''),
                'MIERCOLES': dias_dict.get('MIERCOLES', ''),
                'JUEVES':    dias_dict.get('JUEVES', ''),
                'VIERNES':   dias_dict.get('VIERNES', '')
            }

        return jsonify({
            'cursos': list(tutor_data.keys()),
            'horarios': horarios_formateados
        }), 200

# ── NOTAS ──────────────────────────────────────────
@app.route('/notas/<tutor_id>', methods=['POST'])
def cargar_notas(tutor_id):
    xml_string = request.data.decode('utf-8')
    exito = procesar_notas(xml_string, tutor_id)
    if exito:
        return jsonify({'mensaje': 'Notas cargadas correctamente'}), 200
    return jsonify({'error': 'Error al cargar notas'}), 400

@app.route('/notas/curso/<codigo>', methods=['GET'])
def ver_notas_curso(codigo):
    db = obtener_db()
    if codigo not in db['cursos']:
        return jsonify({'error': 'Curso no encontrado'}), 404
    curso = db['cursos'][codigo]
    if not curso.matriz_notas:
        return jsonify({'notas': []}), 200
    return jsonify({'notas': curso.matriz_notas.obtener_todos()}), 200

# ── ESTUDIANTE ─────────────────────────────────────
@app.route('/mis-notas/<carnet>', methods=['GET'])
def mis_notas(carnet):
    db = obtener_db()
    if carnet not in db['estudiantes']:
        return jsonify({'error': 'Estudiante no encontrado'}), 404
    estudiante = db['estudiantes'][carnet]
    resultado = {}
    for codigo in estudiante.cursos:
        if codigo in db['cursos']:
            curso = db['cursos'][codigo]
            if curso.matriz_notas:
                notas = curso.matriz_notas.obtener_todos()
                resultado[codigo] = notas
    return jsonify(resultado), 200

# ── GRAPHVIZ ───────────────────────────────────────
@app.route('/reporte-graphviz/<codigo>', methods=['GET'])
def reporte_graphviz(codigo):
    db = obtener_db()
    if codigo not in db['cursos']:
        return jsonify({'error': 'Curso no encontrado'}), 404
   
    curso = db['cursos'][codigo]
    if not curso.matriz_notas:
        return jsonify({'error': 'No hay notas cargadas'}), 404
    matriz = curso.matriz_notas
   
    dot_code = 'digraph {\n'
    dot_code += ' rankdir=LR\n'
    dot_code += ' node [shape=box style=filled]\n'
    dot_code += ' "RESUMEN NOTAS" [fillcolor=lightyellow]\n'
   
    for idx, carnet in matriz.nombres_columnas.items():
        dot_code += f' "{carnet}" [fillcolor=lightblue]\n'
        dot_code += f' "RESUMEN NOTAS" -> "{carnet}"\n'
   
    for idx_fila, actividad in matriz.nombres_filas.items():
        dot_code += f' "{actividad}" [fillcolor=orange]\n'
        for idx_col, carnet in matriz.nombres_columnas.items():
            valor = matriz.obtener(idx_fila, idx_col)
            if valor is not None:
                dot_code += f' "{actividad}" -> "{carnet}" [label="{valor}"]\n'
   
    dot_code += '}'

    try:
        import subprocess
        import base64
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            tmp_path = tmp.name
       
        process = subprocess.run(
            ['dot', '-Tpng', '-o', tmp_path],
            input=dot_code.encode(),
            capture_output=True
        )
       
        with open(tmp_path, 'rb') as f:
            img_data = base64.b64encode(f.read()).decode()
       
        os.unlink(tmp_path)
        return jsonify({'imagen': img_data}), 200
   
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)