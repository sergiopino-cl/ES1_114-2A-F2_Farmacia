class Persona:
    """
    Clase base abstracta/padre para representar a cualquier persona dentro del sistema.
    Aplica principios de Programación Orientada a Objetos Segura:
    encapsulamiento de atributos comunes (RUT y nombre) y validaciones de integridad.
    """
    def __init__(self, rut: str, nombre: str):
        self._rut = ""
        self._nombre = ""
        # Usamos los setters para asegurar que las validaciones se apliquen en la instanciación
        self.rut = rut
        self.nombre = nombre

    @property
    def rut(self) -> str:
        return self._rut

    @rut.setter
    def rut(self, valor: str) -> None:
        if not valor or not isinstance(valor, str):
            raise ValueError("El RUT no puede estar vacío y debe ser texto.")
        valor_limpio = valor.strip()
        if len(valor_limpio) < 3:
            raise ValueError("Debe ingresar un RUT válido (mínimo 3 caracteres).")
        self._rut = valor_limpio

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not valor or not isinstance(valor, str):
            raise ValueError("El nombre no puede estar vacío y debe ser texto.")
        valor_limpio = valor.strip()
        if len(valor_limpio) < 2:
            raise ValueError("Debe ingresar un nombre válido (al menos 2 caracteres).")
        self._nombre = valor_limpio

    def validar_rut(self) -> bool:
        """
        Valida que el RUT tenga una longitud mínima y formato general admisible.
        Permite formatos como '12.345.678-9', '12345678-9' o '1-9'.
        """
        if not self._rut:
            return False
        limpio = self._rut.replace(".", "").replace("-", "").strip()
        return len(limpio) >= 2

    def __str__(self) -> str:
        return f"{self._nombre} (RUT: {self._rut})"