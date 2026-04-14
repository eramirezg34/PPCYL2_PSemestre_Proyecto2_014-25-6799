class Nodo:
    def __init__(self, fila, columna, valor):
        self.fila = fila
        self.columna = columna
        self.valor = valor
        self.siguiente_fila = None
        self.siguiente_columna = None


class MatrizDispersa:
    def __init__(self):
        self.filas = {}      # fila -> primer nodo
        self.columnas = {}   # columna -> primer nodo
        self.nombres_filas = {}    # indice -> nombre actividad
        self.nombres_columnas = {} # indice -> carnet alumno

    def insertar(self, fila, columna, valor):
        # Ignorar notas fuera de rango
        if valor < 0 or valor > 100:
            return
        nodo = Nodo(fila, columna, valor)
        self.filas[fila] = nodo
        self.columnas[columna] = nodo

    def obtener(self, fila, columna):
        if fila in self.filas:
            nodo = self.filas[fila]
            if nodo.columna == columna:
                return nodo.valor
        return None

    def obtener_todos(self):
        resultado = []
        for fila, nodo in self.filas.items():
            resultado.append({
                'fila': fila,
                'columna': nodo.columna,
                'valor': nodo.valor
            })
        return resultado