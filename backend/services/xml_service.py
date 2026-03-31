import xml.etree.ElementTree as ET
import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.usuario import Tutor, Estudiante, Administrador
from models.curso import Curso
from models.sparse_matrix import MatrizDispersa

# Base de datos en memoria
db = {
    'cursos': {},
    'tutores': {},
    'estudiantes': {},
    'admin': Administrador()
}

def procesar_xml_configuracion(xml_string):
    tutores_cargados = 0
    estudiantes_cargados = 0
    asig_tutores_correctas = 0
    asig_tutores_incorrectas = 0
    asig_estudiantes_correctas = 0
    asig_estudiantes_incorrectas = 0

    try:
        root = ET.fromstring(xml_string)

        # Cargar cursos
        for curso in root.find('cursos'):
            codigo = curso.get('codigo')
            nombre = curso.text.strip()
            db['cursos'][codigo] = Curso(codigo, nombre)

        # Cargar tutores
        for tutor in root.find('tutores'):
            registro = tutor.get('registro_personal')
            contrasenia = tutor.get('contrasenia')
            nombre = tutor.text.strip()
            db['tutores'][registro] = Tutor(registro, nombre, contrasenia)
            tutores_cargados += 1

        # Cargar estudiantes
        for estudiante in root.find('estudiantes'):
            carnet = estudiante.get('carnet')
            contrasenia = estudiante.get('contrasenia')
            nombre = estudiante.text.strip()
            db['estudiantes'][carnet] = Estudiante(carnet, nombre, contrasenia)
            estudiantes_cargados += 1

        # Procesar asignaciones
        asignaciones = root.find('asignaciones')

        # Asignaciones de tutores
        for tc in asignaciones.find('c_tutores'):
            codigo = tc.get('codigo')
            registro = tc.text.strip()
            if codigo in db['cursos'] and registro in db['tutores']:
                db['cursos'][codigo].asignar_tutor(registro)
                db['tutores'][registro].agregar_curso(codigo)
                asig_tutores_correctas += 1
            else:
                asig_tutores_incorrectas += 1

        # Asignaciones de estudiantes
        for ec in asignaciones.find('c_estudiante'):
            codigo = ec.get('codigo')
            carnet = ec.text.strip()
            if codigo in db['cursos'] and carnet in db['estudiantes']:
                db['cursos'][codigo].agregar_estudiante(carnet)
                db['estudiantes'][carnet].agregar_curso(codigo)
                asig_estudiantes_correctas += 1
            else:
                asig_estudiantes_incorrectas += 1

    except Exception as e:
        print(f"Error procesando XML: {e}")

    # Generar XML de salida
    salida = f'''<?xml version="1.0" encoding="UTF-8"?>
<configuraciones_aplicadas>
    <tutores_cargados>{tutores_cargados}</tutores_cargados>
    <estudiantes_cargados>{estudiantes_cargados}</estudiantes_cargados>
    <asignaciones>
        <tutores>
            <total>{asig_tutores_correctas + asig_tutores_incorrectas}</total>
            <correcto>{asig_tutores_correctas}</correcto>
            <incorrecto>{asig_tutores_incorrectas}</incorrecto>
        </tutores>
        <estudiantes>
            <total>{asig_estudiantes_correctas + asig_estudiantes_incorrectas}</total>
            <correcto>{asig_estudiantes_correctas}</correcto>
            <incorrecto>{asig_estudiantes_incorrectas}</incorrecto>
        </estudiantes>
    </asignaciones>
</configuraciones_aplicadas>'''

    return salida

def procesar_horarios(xml_string, tutor_id):
    try:
        root = ET.fromstring(xml_string)
        for curso in root.findall('curso'):
            codigo = curso.get('codigo')
            texto = curso.text.strip()
            # Extraer horario con expresión regular
            patron = r'HorarioI:\s*(\d{2}:\d{2})\s*HorarioF:\s*(\d{2}:\d{2})'
            match = re.search(patron, texto)
            if match and tutor_id in db['tutores']:
                hora_inicio = match.group(1)
                hora_fin = match.group(2)
                db['tutores'][tutor_id].agregar_horario(
                    codigo, hora_inicio, hora_fin
                )
    except Exception as e:
        print(f"Error procesando horarios: {e}")

def procesar_notas(xml_string, tutor_id):
    try:
        root = ET.fromstring(xml_string)
        codigo_curso = root.find('curso').get('codigo') if root.find('curso') is not None else None
        
        if not codigo_curso or codigo_curso not in db['cursos']:
            return False

        matriz = MatrizDispersa()
        actividades = {}
        carnets = {}
        idx_fila = 0
        idx_col = 0

        for actividad in root.find('notas').findall('actividad'):
            nombre = actividad.get('nombre')
            carnet = actividad.get('carnet')
            nota = int(actividad.text.strip())

            if nombre not in actividades:
                actividades[nombre] = idx_fila
                matriz.nombres_filas[idx_fila] = nombre
                idx_fila += 1

            if carnet not in carnets:
                carnets[carnet] = idx_col
                matriz.nombres_columnas[idx_col] = carnet
                idx_col += 1

            matriz.insertar(actividades[nombre], carnets[carnet], nota)

        db['cursos'][codigo_curso].matriz_notas = matriz
        return True

    except Exception as e:
        print(f"Error procesando notas: {e}")
        return False

def obtener_db():
    return db