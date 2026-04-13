class Nodo:
    def __init__(self, fila, columna, valor):
        self.fila = fila
        self.columna = columna
        self.valor = valor
        self.siguiente_fila = None
        self.siguiente_columna = None


class MatrizDispersa:
    def __init__(self):
        self.nodos = {}  # (fila, columna) -> Nodo
        self.nombres_filas = {}    # indice -> nombre actividad
        self.nombres_columnas = {} # indice -> carnet alumno

    def insertar(self, fila, columna, valor):
        if valor < 0 or valor > 100:
            return
        nodo = Nodo(fila, columna, valor)
        self.nodos[(fila, columna)] = nodo

    def obtener(self, fila, columna):
        nodo = self.nodos.get((fila, columna))
        return nodo.valor if nodo else None

    def obtener_todos(self):
        resultado = []
        for (fila, columna), nodo in self.nodos.items():
            resultado.append({
                'fila': self.nombres_filas.get(fila, str(fila)),
                'columna': self.nombres_columnas.get(columna, str(columna)),
                'valor': nodo.valor
            })
        return resultado