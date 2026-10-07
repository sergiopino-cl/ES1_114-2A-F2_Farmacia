class Cliente:
    def __init__(self, rut: str, nombre: str):
        self._rut = rut
        self._nombre = nombre

    @property
    def rut(self):
        return self._rut

    @property
    def nombre(self):
        return self._nombre

    def validar_rut(self) -> bool:
        return bool(self._rut and len(self._rut) >= 8)