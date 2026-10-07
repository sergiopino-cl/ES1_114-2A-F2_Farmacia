class Persona: # definir clase vendedor
    def __init__(self, nombre: str, rut: str ): # rut con formato "1-9" o "12345678-K"
        self.__rut = rut
        self.__nombre = nombre

    @property
    def rut(self) -> str:
        return self.__rut

    @property
    def nombre(self) -> str:
        return self.__nombre

    @rut.setter
    def rut(self, valor: str) -> None:
        if len(valor) < 3 or " " in valor:
            raise ValueError( "Debe ingresar un rut válido")
        self.__rut: str = valor

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if len(valor) < 7 or " " in valor:
            raise ValueError( "Debe ingresar un nombre válido")
        self.__nombre: str = valor