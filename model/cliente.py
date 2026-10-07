from model.persona import Persona

class Cliente(Persona):
    """
    Representa a un cliente que adquiere productos en la farmacia.
    Hereda atributos comunes (rut, nombre) y validaciones de la clase base Persona.
    """
    def __init__(self, rut: str, nombre: str):
        super().__init__(rut, nombre)

    def __str__(self) -> str:
        return f"Cliente: {self.nombre} (RUT: {self.rut})"