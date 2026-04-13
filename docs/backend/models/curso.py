class Curso:
    def __init__(self, codigo, nombre):
        self.codigo = codigo
        self.nombre = nombre
        self.tutor_id = None
        self.estudiantes = []
        self.matriz_notas = None  # MatrizDispersa

    def asignar_tutor(self, tutor_id):
        self.tutor_id = tutor_id

    def agregar_estudiante(self, carnet):
        if carnet not in self.estudiantes:
            self.estudiantes.append(carnet)

    def to_dict(self):
        return {
            'codigo': self.codigo,
            'nombre': self.nombre,
            'tutor_id': self.tutor_id,
            'estudiantes': self.estudiantes
        }