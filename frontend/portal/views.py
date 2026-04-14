import requests
import json
from django.shortcuts import render, redirect

FLASK_URL = 'http://127.0.0.1:5000'

def login_view(request):
    error = None
    if request.method == 'POST':
        usuario = request.POST.get('usuario')
        contrasenia = request.POST.get('contrasenia')
        try:
            response = requests.post(f'{FLASK_URL}/login', json={
                'usuario': usuario,
                'contrasenia': contrasenia
            })
            if response.status_code == 200:
                data = response.json()
                request.session['usuario'] = usuario
                request.session['rol'] = data['rol']
                request.session['nombre'] = data['nombre']
                if 'id' in data:
                    request.session['id'] = data['id']
                if data['rol'] == 'admin':
                    return redirect('admin_panel')
                elif data['rol'] == 'tutor':
                    return redirect('tutor_panel')
                else:
                    return redirect('estudiante_panel')
            else:
                error = 'Usuario o contraseña incorrectos'
        except:
            error = 'No se puede conectar con el servidor'
    return render(request, 'login.html', {'error': error})


def logout_view(request):
    request.session.flush()
    return redirect('login')


def admin_panel(request):
    if request.session.get('rol') != 'admin':
        return redirect('login')
    salida = None
    if request.method == 'POST':
        xml_data = request.POST.get('xml_content')
        try:
            response = requests.post(
                f'{FLASK_URL}/cargar-configuracion',
                data=xml_data.encode('utf-8'),
                headers={'Content-Type': 'application/xml'}
            )
            salida = response.text
        except:
            salida = 'Error conectando con el servidor'
    return render(request, 'admin_panel.html', {'salida': salida})


def ver_usuarios(request):
    if request.session.get('rol') != 'admin':
        return redirect('login')
    usuarios = []
    try:
        response = requests.get(f'{FLASK_URL}/usuarios')
        usuarios = response.json()
    except:
        pass
    return render(request, 'ver_usuarios.html', {'usuarios': usuarios})


def tutor_panel(request):
    if request.session.get('rol') != 'tutor':
        return redirect('login')
    return render(request, 'tutor_panel.html')


def horarios(request):
    if request.session.get('rol') != 'tutor':
        return redirect('login')

    tutor_id = request.session.get('id')
    mensaje = None
    horarios_tabla = {}

    if request.method == 'POST':
        xml_data = request.POST.get('xml_content')
        if xml_data:
            try:
                response = requests.post(
                    f'{FLASK_URL}/horarios/{tutor_id}',
                    data=xml_data.encode('utf-8'),
                    headers={'Content-Type': 'application/xml'}
                )
                if response.status_code in (200, 201):
                    mensaje = '✅ Horarios cargados correctamente'
                    request.session['xml_horarios'] = xml_data
                else:
                    mensaje = f'❌ Error al guardar: {response.text[:150]}'
            except Exception as e:
                mensaje = f'❌ Error conectando con Flask: {str(e)}'

    try:
        response = requests.get(f'{FLASK_URL}/horarios/{tutor_id}')
        if response.status_code == 200:
            data = response.json()
            cursos = data.get('cursos', [])
            horarios_dict = data.get('horarios', {})

            for codigo in cursos:
                nombre_curso = f"{codigo} - Curso {codigo}"
                curso_horarios = horarios_dict.get(codigo, {}) if isinstance(horarios_dict, dict) else {}
                horarios_tabla[nombre_curso] = {
                    'lunes':     curso_horarios.get('LUNES', ''),
                    'martes':    curso_horarios.get('MARTES', ''),
                    'miercoles': curso_horarios.get('MIERCOLES', ''),
                    'jueves':    curso_horarios.get('JUEVES', ''),
                    'viernes':   curso_horarios.get('VIERNES', ''),
                }

            if not horarios_tabla:
                mensaje = (mensaje or 'No se encontraron horarios para este tutor.')
        else:
            mensaje = mensaje or f'Error al obtener horarios (código {response.status_code})'
    except Exception as e:
        mensaje = mensaje or f'Error al consultar horarios: {str(e)}'

    return render(request, 'horarios.html', {
        'mensaje': mensaje,
        'horarios': horarios_tabla,
        'xml_cargado': request.session.get('xml_horarios', '')
    })


def notas(request):
    if request.session.get('rol') != 'tutor':
        return redirect('login')
    tutor_id = request.session.get('id')
    mensaje = None
    if request.method == 'POST':
        xml_data = request.POST.get('xml_content')
        try:
            requests.post(
                f'{FLASK_URL}/notas/{tutor_id}',
                data=xml_data.encode('utf-8'),
                headers={'Content-Type': 'application/xml'}
            )
            mensaje = 'Notas cargadas correctamente'
        except:
            mensaje = 'Error conectando con el servidor'
    return render(request, 'notas.html', {'mensaje': mensaje})


def reporte_notas(request):
    if request.session.get('rol') != 'tutor':
        return redirect('login')
    tutor_id = request.session.get('id')
    imagen = None
    error = None
    cursos = []
    notas_json = '[]'
    actividades = []

    try:
        tutor_response = requests.get(f'{FLASK_URL}/horarios/{tutor_id}')
        if tutor_response.status_code == 200:
            data = tutor_response.json()
            for codigo in data.get('cursos', []):
                cursos.append((codigo, f"{codigo}"))
    except:
        error = 'Error conectando con el servidor'

    if request.method == 'POST':
        codigo = request.POST.get('codigo_curso')
        try:
            response = requests.get(f'{FLASK_URL}/reporte-graphviz/{codigo}')
            if response.status_code == 200:
                imagen = response.json().get('imagen')
            else:
                error = 'No hay notas cargadas para este curso'

            notas_response = requests.get(f'{FLASK_URL}/notas/curso/{codigo}')
            if notas_response.status_code == 200:
                notas_data = notas_response.json().get('notas', [])
                notas_json = json.dumps(notas_data)
                actividades = sorted(list(set([n['fila'] for n in notas_data])))
        except Exception as e:
            error = f'Error generando reporte: {str(e)}'

    return render(request, 'reporte_notas.html', {
        'imagen': imagen,
        'error': error,
        'cursos': cursos,
        'notas_json': notas_json,
        'actividades': actividades,
    })


def estudiante_panel(request):
    if request.session.get('rol') != 'estudiante':
        return redirect('login')
    carnet = request.session.get('id')
    mis_notas = {}
    try:
        response = requests.get(f'{FLASK_URL}/mis-notas/{carnet}')
        mis_notas = response.json()
    except:
        pass
    return render(request, 'estudiante_panel.html', {'notas': mis_notas})