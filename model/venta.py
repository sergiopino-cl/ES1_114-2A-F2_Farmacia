from datetime import date
from typing import List, Optional, Union
from model.cliente import Cliente
from model.vendedor import Vendedor
from model.receta_medica import RecetaMedica
from model.detalle_venta import DetalleVenta

class Venta:
    """
    Representa una transacción de venta en la farmacia.
    Aplica principios de Programación Orientada a Objetos Segura:
    encapsulamiento de atributos, inmutabilidad de listas expuestas
    y validación estricta de las reglas de negocio farmacéuticas.
    """
    def __init__(self, fecha: str, cliente: Cliente, 
                 vendedor: Optional[Union[Vendedor, str]] = None, 
                 receta_medica: Optional[RecetaMedica] = None, 
                 id_venta: Optional[int] = None,
                 vendedor_rut: Optional[str] = None):
        self._id = id_venta
        self._fecha = str(fecha).strip() if fecha else str(date.today())
        self._cliente = cliente
        self._receta_medica = receta_medica
        self._detalles: List[DetalleVenta] = []

        # Soporte tanto para objeto Vendedor como para vendedor_rut (compatibilidad)
        self._vendedor: Optional[Vendedor] = None
        self._vendedor_rut: str = ""

        if isinstance(vendedor, Vendedor):
            self._vendedor = vendedor
            self._vendedor_rut = vendedor.rut
        elif isinstance(vendedor, str):
            self._vendedor_rut = vendedor.strip()
        elif vendedor_rut:
            self._vendedor_rut = str(vendedor_rut).strip()

    @property
    def id(self) -> Optional[int]:
        return self._id

    @id.setter
    def id(self, valor: int) -> None:
        if valor is not None and valor <= 0:
            raise ValueError("El ID de la venta debe ser un entero positivo.")
        self._id = valor

    @property
    def fecha(self) -> str:
        return self._fecha

    @fecha.setter
    def fecha(self, valor: str) -> None:
        if not valor or not str(valor).strip():
            raise ValueError("La fecha de venta no puede estar vacía.")
        self._fecha = str(valor).strip()

    @property
    def cliente(self) -> Cliente:
        return self._cliente

    @cliente.setter
    def cliente(self, nuevo_cliente: Cliente) -> None:
        if nuevo_cliente is None:
            raise ValueError("El cliente no puede ser nulo.")
        self._cliente = nuevo_cliente

    @property
    def vendedor(self) -> Optional[Vendedor]:
        return self._vendedor

    @vendedor.setter
    def vendedor(self, vend: Optional[Vendedor]) -> None:
        self._vendedor = vend
        if vend is not None:
            self._vendedor_rut = vend.rut

    @property
    def vendedor_rut(self) -> str:
        if self._vendedor:
            return self._vendedor.rut
        return self._vendedor_rut

    @vendedor_rut.setter
    def vendedor_rut(self, rut: str) -> None:
        self._vendedor_rut = str(rut).strip() if rut else ""

    @property
    def receta_medica(self) -> Optional[RecetaMedica]:
        return self._receta_medica

    @receta_medica.setter
    def receta_medica(self, receta: Optional[RecetaMedica]) -> None:
        self._receta_medica = receta

    @property
    def detalles(self) -> List[DetalleVenta]:
        # Retorna una copia defensiva para proteger el encapsulamiento interno
        return list(self._detalles)

    def agregar_detalle(self, detalle: DetalleVenta) -> None:
        """Agrega un ítem de detalle a la venta."""
        if not isinstance(detalle, DetalleVenta):
            raise TypeError("El detalle debe ser una instancia de DetalleVenta.")
        self._detalles.append(detalle)

    def calcular_total(self, tasa_dolar: float = 1.0) -> float:
        """
        Calcula el total de la venta sumando los subtotales de cada detalle.
        Delega el cálculo a cada DetalleVenta preservando el encapsulamiento.
        """
        return sum(d.calcular_subtotal() for d in self._detalles)

    def verificar_reglas(self) -> tuple[bool, str]:
        """
        Verifica exhaustivamente las reglas de negocio de la venta:
        1. Debe haber productos en el detalle.
        2. El cliente debe tener RUT admisible.
        3. Debe haber un vendedor asignado.
        4. Si algún medicamento es controlado:
           a) Se exige receta médica válida.
           b) Si se conoce la entidad Vendedor, debe ser Químico Farmacéutico.
        """
        if not self._detalles:
            return False, "La venta debe contener al menos un medicamento en el carrito."

        if not self._cliente or not self._cliente.validar_rut():
            return False, "El cliente no cuenta con un RUT válido."

        if not self.vendedor_rut:
            return False, "Debe seleccionar un vendedor para registrar la venta."

        tiene_restringidos = any(getattr(d.medicamento, 'restringido', False) for d in self._detalles)
        if tiene_restringidos:
            if not self._receta_medica or not self._receta_medica.es_valida():
                return False, "La venta contiene medicamentos controlados y requiere una receta médica válida registrada."
            if self._vendedor is not None and not self._vendedor.esfarmaceutico:
                return False, "El vendedor seleccionado no es Químico Farmacéutico. Solo un Químico Farmacéutico puede autorizar la venta de medicamentos controlados."

        return True, ""

    def validar_venta(self) -> bool:
        """Valida si la venta cumple con todas las restricciones de negocio."""
        valido, _ = self.verificar_reglas()
        return valido

    def __str__(self) -> str:
        folio = f"#{self._id}" if self._id else "(Pendiente)"
        return f"Venta {folio} - Fecha: {self._fecha} - Cliente: {self._cliente.nombre} - Total: ${self.calcular_total():,.0f} CLP"