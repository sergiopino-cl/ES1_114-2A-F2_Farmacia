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
    def precio_venta(self) -> int: 
        return self._precio_venta

    @precio_venta.setter
    def precio_venta(self, value):
        try:
            val_int = int(value)
            if val_int < 0:
                raise ValueError("El precio de venta debe ser positivo")
            self._precio_venta = val_int
        except (ValueError, TypeError):
            raise TypeError(f"Precio de venta inválido: '{value}'. Debe ser un número entero.")

    @property
    def precio_compra_usd(self) -> float:
        return self._precio_compra_usd

    @precio_compra_usd.setter
    def precio_compra_usd(self, valor):
        try:
            val_float = float(valor)
            if val_float < 0:
                raise ValueError("El precio en USD no puede ser negativo.")
            self._precio_compra_usd = val_float
        except (ValueError, TypeError):
            raise TypeError(f"Precio USD inválido: '{valor}'. Debe ser un número decimal.")
        
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
    def stock(self) -> int:
        return self._stock

    @stock.setter
    def stock(self, valor):
        try:
            val_stock = int(valor)
            if val_stock < 0:
                raise ValueError("El stock no puede ser menor a cero.")
            self._stock = val_stock
        except (ValueError, TypeError):
            raise TypeError(f"Stock inválido: '{valor}'. Debe ser un entero.")
    
    def __str__(self):
        receta = "Requiere Receta" if self._restringido else "Venta Libre"
        return f"[{self._codigo}] {self._nombre} - ${self._precio_venta} CLP ({receta})"