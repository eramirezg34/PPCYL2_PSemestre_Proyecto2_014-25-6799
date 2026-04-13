from flask import Flask, request, jsonify
import sys
import os

# Agregar backend al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.xml_service import (
    procesar_xml_configuracion,
    procesar_horarios,
    procesar_notas,
    obtener_db
)

app = Flask(__name__)

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


# ── TUTOR ──────────────────────────────────────────
@app.route('/horarios/<tutor_id>', methods=['POST'])
def cargar_horarios(tutor_id):
    xml_string = request.data.decode('utf-8')
    procesar_horarios(xml_string, tutor_id)
    return jsonify({'mensaje': 'Horarios cargados correctamente'}), 200

@app.route('/horarios/<tutor_id>', methods=['GET'])
def ver_horarios(tutor_id):
    db = obtener_db()
    if tutor_id not in db['tutores']:
        return jsonify({'error': 'Tutor no encontrado'}), 404
    tutor = db['tutores'][tutor_id]
    return jsonify({
        'cursos': tutor.cursos,
        'horarios': tutor.horarios
    }), 200

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


if __name__ == '__main__':
    app.run(debug=True, port=5000)