class Vendedor: # definir clase vendedor
    def __init__(self, nombre: str, rut: str, esfarmaceutico: bool):
        self.__rut = rut
        self.__nombre = nombre
        self.__esfarmaceutico = esfarmaceutico

    @property
    def rut(self) -> str:
        return self.__rut

    @property
    def nombre(self) -> str:
        return self.__nombre

    @property
    def esfarmaceutico(self) -> bool:
        return self.__esfarmaceutico

    @rut.setter
    def rut(self, valor: str) -> None:
        if len(valor) < 7 or " " in valor:
            raise ValueError( "Debe ingresar un rut válido")
        self.__rut: str = valor

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if len(valor) < 7 or " " in valor:
            raise ValueError( "Debe ingresar un rut válido")
        self.__rut: str = valor