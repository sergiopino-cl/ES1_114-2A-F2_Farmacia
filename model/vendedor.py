from model.persona import Persona

class Vendedor(Persona):
    """
    Representa a un vendedor en la farmacia.
    Hereda atributos comunes (rut, nombre) y métodos de la clase base Persona.
    Extiende la funcionalidad con la distinción de si es Químico Farmacéutico.
    """
    def __init__(self, rut: str, nombre: str, esfarmaceutico: bool = False):
        super().__init__(rut, nombre)
        self._esfarmaceutico = bool(esfarmaceutico)

    @property
    def esfarmaceutico(self) -> bool:
        return self._esfarmaceutico

    @esfarmaceutico.setter
    def esfarmaceutico(self, value: bool) -> None:
        self._esfarmaceutico = bool(value)

    def __str__(self) -> str:
        tipo = "Farmacéutico" if self._esfarmaceutico else "Vendedor General"
        return f"{self.nombre} ({tipo}) - RUT: {self.rut}"