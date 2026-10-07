class Vendedor:
    def __init__(self, rut: str, nombre: str, esfarmaceutico: bool):
        self._rut = rut
        self._nombre = nombre
        self._esfarmaceutico = esfarmaceutico

    @property
    def rut(self):
        return self._rut

    @rut.setter
    def rut(self, value):
        self._rut = value

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, value):
        self._nombre = value

    @property
    def esfarmaceutico(self):
        return self._esfarmaceutico

    @esfarmaceutico.setter
    def esfarmaceutico(self, value):
        self._esfarmaceutico = bool(value)

    def __str__(self):
        tipo = "Farmacéutico" if self._esfarmaceutico else "Vendedor General"
        return f"{self._nombre} ({tipo}) - RUT: {self._rut}"