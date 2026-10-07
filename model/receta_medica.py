from datetime import datetime

class RecetaMedica:
    def __init__(self, numero_receta: str, fecha_emision: str):
        self._numero_receta = numero_receta
        self._fecha_emision = fecha_emision

    @property
    def numero_receta(self):
        return self._numero_receta

    @property
    def fecha_emision(self):
        return self._fecha_emision

    def validar_formato(self) -> bool:
        return len(self._numero_receta.strip()) > 0

    def es_valida(self) -> bool:
        return self.validar_formato()