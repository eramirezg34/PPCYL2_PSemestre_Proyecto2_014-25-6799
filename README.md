# PPCYL2-AcadNet 

**Universidad Mariano Gálvez de Guatemala**  
**Facultad de Ingeniería Matemática y Ciencias Físicas**  
**Curso: Programación para la Ciencia y la Ingeniería II**  
**Ing. Carlos Alberto Arias López**

---

## Descripción

PPCYL2-AcadNet es una plataforma educativa web que conecta estudiantes con tutores especializados. Permite el seguimiento personalizado del aprendizaje, gestión de sesiones de tutoría y generación de estadísticas académicas.

---

## Arquitectura

El sistema utiliza arquitectura cliente-servidor con dos servicios:

- **Servicio 1 - Frontend:** Django (puerto 8000)
- **Servicio 2 - Backend:** Flask API REST (puerto 5000)

```
[Navegador] → [Django :8000] → HTTP → [Flask :5000] → [Archivos XML]
```

---

## Tecnologías Utilizadas

- **Python 3.14**
- **Flask 3.1.3** - Backend API REST
- **Django 6.0.3** - Frontend
- **Graphviz** - Generación de reportes visuales
- **ChartJS** - Gráficas interactivas
- **jsPDF + html2canvas** - Exportación a PDF

---

##  Estructura del Proyecto

```
PPCYL2_PSemestre_Proyecto2_014-25-6799/
├── backend/                  ← Flask API (puerto 5000)
│   ├── app.py               ← Endpoints REST
│   ├── models/
│   │   ├── sparse_matrix.py ← Matriz dispersa POO
│   │   ├── usuario.py       ← Clases Tutor, Estudiante, Admin
│   │   └── curso.py         ← Clase Curso
│   └── services/
│       └── xml_service.py   ← Procesamiento XML
├── frontend/                 ← Django (puerto 8000)
│   ├── manage.py
│   └── portal/
│       ├── views.py         ← Vistas Django
│       ├── urls.py          ← Rutas
│       └── templates/       ← HTMLs
└── docs/                     ← Documentación y XMLs de prueba
```

---

## Instalación

### Requisitos
- Python 3.14
- Git
- Graphviz (instalado en el sistema)

### Pasos

**1. Clonar el repositorio:**
```bash
git clone https://github.com/eramirezg34/PPCYL2_PSemestre_Proyecto2_014-25-6799.git
cd PPCYL2_PSemestre_Proyecto2_014-25-6799
```

**2. Instalar librerías:**
```bash
python -m pip install flask django requests graphviz plotly
```

**3. Correr el Backend (Terminal 1):**
```bash
cd backend
python app.py
```

**4. Correr el Frontend (Terminal 2):**
```bash
cd frontend
python manage.py migrate
python manage.py runserver
```

**5. Abrir en el navegador:**
```
http://127.0.0.1:8000
```

---

## Credenciales de Prueba

| Rol | Usuario | Contraseña |
|-----|---------|------------|
| Administrador | AdminPPCYL2 | AdminPPCYL2771 |
| Tutor | 1111 | 1234 |
| Estudiante | 1234 | 1234 |

> Los tutores y estudiantes se cargan mediante el XML de configuración.

---

## Endpoints de la API Flask

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | /login | Autenticación de usuarios |
| POST | /cargar-configuracion | Carga XML de configuración |
| GET | /usuarios | Lista todos los usuarios |
| POST | /horarios/\<tutor_id\> | Carga horarios del tutor |
| GET | /horarios/\<tutor_id\> | Obtiene horarios del tutor |
| POST | /notas/\<tutor_id\> | Carga notas de alumnos |
| GET | /notas/curso/\<codigo\> | Obtiene notas de un curso |
| GET | /mis-notas/\<carnet\> | Obtiene notas de un estudiante |
| GET | /reporte-graphviz/\<codigo\> | Genera reporte Graphviz |

---

##  Funcionalidades

### Módulo Administrador
- Carga de archivo XML de configuración
- Visualización de usuarios registrados
- Generación de XML de salida con estadísticas

### Módulo Tutor
- Gestión de horarios de tutoría
- Ingreso de notas mediante XML
- Reporte visual con Graphviz (matriz dispersa)
- Gráficas de promedio y TOP de notas
- Exportación a PDF

### Módulo Estudiante
- Consulta de notas por curso
- Visualización de estado (Aprobado/Regular/Reprobado)

---

##  Estructura de Datos

### Matriz Dispersa (POO)
La matriz dispersa almacena las notas de forma eficiente:
- **Filas:** Actividades (Tarea1, Tarea2, etc.)
- **Columnas:** Carnets de estudiantes
- Solo almacena valores existentes usando nodos enlazados

---

##  Formato XML de Entrada

```xml
<?xml version="1.0"?>
<configuraciones>
    <cursos>
        <curso codigo="770">Matematicas</curso>
    </cursos>
    <tutores>
        <tutor registro_personal="1111" contrasenia="1234">Juan Perez</tutor>
    </tutores>
    <estudiantes>
        <estudiante carnet="1234" contrasenia="1234">Carlos Garcia</estudiante>
    </estudiantes>
    <asignaciones>
        <c_tutores>
            <tutor_curso codigo="770">1111</tutor_curso>
        </c_tutores>
        <c_estudiante>
            <estudiante_curso codigo="770">1234</estudiante_curso>
        </c_estudiante>
    </asignaciones>
</configuraciones>
```

---

##  Formato XML de Salida

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuraciones_aplicadas>
    <tutores_cargados>2</tutores_cargados>
    <estudiantes_cargados>2</estudiantes_cargados>
    <asignaciones>
        <tutores>
            <total>3</total>
            <correcto>3</correcto>
            <incorrecto>0</incorrecto>
        </tutores>
        <estudiantes>
            <total>3</total>
            <correcto>3</correcto>
            <incorrecto>0</incorrecto>
        </estudiantes>
    </asignaciones>
</configuraciones_aplicadas>
```

---

##  Integrantes

| Nombre | Carnet | Rol |
|--------|--------|-----|
| Eduardo Ramírez | 014-25-6799 | Backend, Graphviz |
| Marco David Velásquez Godínez | 012-22-12100 | Gráficas, PDF |
| Aurora Mishell Marroquín Cordón | 010 22 1960 | Documentación PDF |

---

##  Entregas

- **Release 1:** Login, Admin, Tutor básico
- **Release 2:** Sistema completo con gráficas y reportes

---

##  Notas Importantes

- Los datos se guardan en memoria, se pierden al reiniciar Flask
- Siempre cargar el XML de configuración como Admin antes de probar
- El sistema puede ser consumido desde Postman en el puerto 5000
