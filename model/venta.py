from datetime import date
from typing import List, Optional
from model.cliente import Cliente
from model.receta_medica import RecetaMedica
from model.detalle_venta import DetalleVenta

class Venta:
    def __init__(self, fecha: str, cliente: Cliente, vendedor_rut: str, 
                 receta_medica: Optional[RecetaMedica] = None, id_venta: Optional[int] = None):
        self._id = id_venta
        self._fecha = fecha
        self._cliente = cliente
        self._vendedor_rut = vendedor_rut
        self._receta_medica = receta_medica
        self._detalles: List[DetalleVenta] = []

    @property
    def id(self):
        return self._id

    @property
    def fecha(self):
        return self._fecha

    @property
    def cliente(self):
        return self._cliente

    @property
    def vendedor_rut(self):
        return self._vendedor_rut

    @property
    def receta_medica(self):
        return self._receta_medica

    @property
    def detalles(self):
        return self._detalles

    def agregar_detalle(self, detalle: DetalleVenta):
        self._detalles.append(detalle)

    def calcular_total(self, tasa_dolar: float = 1.0) -> float:
        total = 0.0
        for detalle in self._detalles:
            # Si el medicamento es importado, el precio se calcula según la tasa del dólar
            if getattr(detalle.medicamento, 'es_importado', False):
                precio = detalle.medicamento.precio_base_usd * tasa_dolar
            else:
                precio = detalle.precio_unitario
            total += detalle.cantidad * precio
        return total

    def validar_venta(self) -> bool:
        if not self._detalles:
            return False
        if not self._cliente or not self._cliente.validar_rut():
            return False
        # Si algún medicamento en el detalle es "Controlado", exige receta válida
        for d in self._detalles:
            if getattr(d.medicamento, 'restringido', False):
                if not self._receta_medica or not self._receta_medica.es_valida():
                    return False
        return True