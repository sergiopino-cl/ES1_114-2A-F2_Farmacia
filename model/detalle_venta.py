from model.medicamento import Medicamento

class DetalleVenta:
    """
    Representa una línea o ítem de detalle en una venta.
    Aplica principios de Programación Orientada a Objetos Segura:
    encapsulamiento y validación defensiva en cantidad y precio.
    """
    def __init__(self, medicamento: Medicamento, cantidad: int, precio_unitario: float):
        self._medicamento = None
        self._cantidad = 0
        self._precio_unitario = 0.0

        self.medicamento = medicamento
        self.cantidad = cantidad
        self.precio_unitario = precio_unitario

    @property
    def medicamento(self) -> Medicamento:
        return self._medicamento

    @medicamento.setter
    def medicamento(self, med: Medicamento) -> None:
        if med is None:
            raise ValueError("El medicamento no puede ser nulo en el detalle.")
        if not hasattr(med, 'codigo') or not hasattr(med, 'nombre'):
            raise TypeError("El medicamento proporcionado no es un objeto válido.")
        self._medicamento = med

    @property
    def cantidad(self) -> int:
        return self._cantidad

    @cantidad.setter
    def cantidad(self, valor: int) -> None:
        try:
            val_int = int(valor)
            if val_int <= 0:
                raise ValueError("La cantidad vendida debe ser mayor a cero.")
            self._cantidad = val_int
        except (ValueError, TypeError) as e:
            if isinstance(e, ValueError) and "mayor a cero" in str(e):
                raise
            raise TypeError(f"Cantidad inválida: '{valor}'. Debe ser un número entero.")

    @property
    def precio_unitario(self) -> float:
        return self._precio_unitario

    @precio_unitario.setter
    def precio_unitario(self, valor: float) -> None:
        try:
            val_float = float(valor)
            if val_float < 0:
                raise ValueError("El precio unitario no puede ser negativo.")
            self._precio_unitario = val_float
        except (ValueError, TypeError) as e:
            if isinstance(e, ValueError) and "negativo" in str(e):
                raise
            raise TypeError(f"Precio unitario inválido: '{valor}'. Debe ser numérico.")

    def calcular_subtotal(self) -> float:
        """Calcula el subtotal seguro de la línea de venta."""
        return float(round(self._cantidad * self._precio_unitario, 2))

    def __str__(self) -> str:
        nombre = getattr(self._medicamento, 'nombre', 'Desconocido')
        return f"{nombre} x{self._cantidad} @ ${self._precio_unitario:,.0f} = ${self.calcular_subtotal():,.0f}"