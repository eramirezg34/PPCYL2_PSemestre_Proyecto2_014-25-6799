import requests
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
    horarios_data = {}
    if request.method == 'POST':
        xml_data = request.POST.get('xml_content')
        try:
            response = requests.post(
                f'{FLASK_URL}/horarios/{tutor_id}',
                data=xml_data.encode('utf-8'),
                headers={'Content-Type': 'application/xml'}
            )
            mensaje = 'Horarios cargados correctamente'
        except:
            mensaje = 'Error conectando con el servidor'
    try:
        response = requests.get(f'{FLASK_URL}/horarios/{tutor_id}')
        horarios_data = response.json()
    except:
        pass
    return render(request, 'horarios.html', {
        'mensaje': mensaje,
        'horarios': horarios_data
    })

def notas(request):
    if request.session.get('rol') != 'tutor':
        return redirect('login')
    tutor_id = request.session.get('id')
    mensaje = None
    if request.method == 'POST':
        xml_data = request.POST.get('xml_content')
        try:
            response = requests.post(
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
    return render(request, 'reporte_notas.html')

def estudiante_panel(request):
    if request.session.get('rol') != 'estudiante':
        return redirect('login')
    carnet = request.session.get('id')
    notas = {}
    try:
        response = requests.get(f'{FLASK_URL}/mis-notas/{carnet}')
        notas = response.json()
    except:
        pass
    return render(request, 'estudiante_panel.html', {'notas': notas})