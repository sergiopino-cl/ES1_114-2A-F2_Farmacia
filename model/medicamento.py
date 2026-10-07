class Medicamento:
    def __init__(self, nombre: str, precio_venta: int, precio_compra_usd: float, 
                 precio_compra_peso: int, fecha_ultima_compra: str, restringido: bool, stock: int = 0, codigo: int = None ):
        self._codigo = codigo  # Es opcional al instanciar porque SQLite lo genera automáticamente (INTEGER PRIMARY KEY)
        self._nombre = nombre
        self._precio_venta = precio_venta
        self._precio_compra_usd = precio_compra_usd
        self._precio_compra_peso = precio_compra_peso
        self._fecha_ultima_compra = fecha_ultima_compra
        self._stock = stock
        self._restringido = restringido
        

    # Getters y Setters
    @property
    def codigo(self):
        return self._codigo

    @codigo.setter
    def codigo(self, value):
        self._codigo = value

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, value):
        self._nombre = value

    @property
    def precio_venta(self):
        return self._precio_venta

    @precio_venta.setter
    def precio_venta(self, value):
        self._precio_venta = int(value)

    @property
    def precio_compra_usd(self):
        return self._precio_compra_usd

    @precio_compra_usd.setter
    def precio_compra_usd(self, value):
        self._precio_compra_usd = float(value)

    @property
    def precio_compra_peso(self):
        return self._precio_compra_peso

    @precio_compra_peso.setter
    def precio_compra_peso(self, value):
        self._precio_compra_peso = int(value)

    @property
    def fecha_ultima_compra(self):
        return self._fecha_ultima_compra

    @fecha_ultima_compra.setter
    def fecha_ultima_compra(self, value):
        self._fecha_ultima_compra = value

    @property
    def restringido(self):
        return self._restringido

    @restringido.setter
    def restringido(self, value):
        self._restringido = bool(value)

    @property
    def stock(self):
        return self._stock

    @stock.setter
    def stock(self, value):
        self._stock = int(value)

    def __str__(self):
        receta = "Requiere Receta" if self._restringido else "Venta Libre"
        return f"[{self._codigo}] {self._nombre} - ${self._precio_venta} CLP ({receta})"