from model.medicamento import Medicamento

class DetalleVenta:
    def __init__(self, medicamento: Medicamento, cantidad: int, precio_unitario: float):
        self._medicamento = medicamento
        self._cantidad = cantidad
        self._precio_unitario = precio_unitario

    @property
    def medicamento(self):
        return self._medicamento

    @property
    def cantidad(self):
        return self._cantidad

    @property
    def precio_unitario(self):
        return self._precio_unitario

    def calcular_subtotal(self) -> float:
        return self._cantidad * self._precio_unitario