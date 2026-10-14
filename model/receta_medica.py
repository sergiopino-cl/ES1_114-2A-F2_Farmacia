from datetime import datetime

class RecetaMedica:
    """
    Representa una receta médica requerida para la venta de medicamentos controlados.
    Aplica encapsulamiento y validación defensiva de datos según principios de POO Segura.
    """
    def __init__(self, numero_receta: str, fecha_emision: str):
        self._numero_receta = ""
        self._fecha_emision = ""
        self.numero_receta = numero_receta
        self.fecha_emision = fecha_emision

    @property
    def numero_receta(self) -> str:
        return self._numero_receta

    @numero_receta.setter
    def numero_receta(self, valor: str) -> None:
        if valor is None or not str(valor).strip():
            raise ValueError("El número de receta médica no puede estar vacío.")
        self._numero_receta = str(valor).strip()

    @property
    def fecha_emision(self) -> str:
        return self._fecha_emision

    @fecha_emision.setter
    def fecha_emision(self, valor: str) -> None:
        if valor is None or not str(valor).strip():
            raise ValueError("La fecha de emisión no puede estar vacía.")
        self._fecha_emision = str(valor).strip()

    def validar_formato(self) -> bool:
        return bool(self._numero_receta and len(self._numero_receta.strip()) > 0)

    def es_valida(self) -> bool:
        return self.validar_formato()

    def __str__(self) -> str:
        return f"Receta N° {self._numero_receta} (Emisión: {self._fecha_emision})"