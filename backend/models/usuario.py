class Usuario:
    def __init__(self, id, nombre, contrasenia, rol):
        self.id = id
        self.nombre = nombre
        self.contrasenia = contrasenia
        self.rol = rol  # 'admin', 'tutor', 'estudiante'

class Tutor(Usuario):
    def __init__(self, id, nombre, contrasenia):
        super().__init__(id, nombre, contrasenia, 'tutor')
        self.cursos = []      # lista de codigos de cursos asignados
        # horarios: {codigo_curso: {dia: "hora_inicio-hora_fin"}}
        self.horarios = {}

    def agregar_curso(self, codigo):
        if codigo not in self.cursos:
            self.cursos.append(codigo)

    def agregar_horario(self, codigo, hora_inicio, hora_fin, dia):
        if codigo in self.cursos:
            if codigo not in self.horarios:
                self.horarios[codigo] = {}
            self.horarios[codigo][dia] = f"{hora_inicio}-{hora_fin}"

class Estudiante(Usuario):
    def __init__(self, id, nombre, contrasenia):
        super().__init__(id, nombre, contrasenia, 'estudiante')
        self.cursos = []  # lista de codigos de cursos asignados

    def agregar_curso(self, codigo):
        if codigo not in self.cursos:
            self.cursos.append(codigo)

class Administrador(Usuario):
    def __init__(self):
        super().__init__(
            'admin',
            'Administrador',
            'AdminPPCYL2771',
            'admin'
        )
        self.username = 'AdminPPCYL2'
