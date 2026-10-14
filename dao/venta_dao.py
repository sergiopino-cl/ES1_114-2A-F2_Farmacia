import pandas as pd
from dao.dao import DAO
from model.venta import Venta

class VentaDAO(DAO):
    """
    Data Access Object (DAO) para la gestión segura y persistencia
    de Ventas, Detalles de Venta, Clientes y Recetas Médicas en SQLite.
    Hereda de la clase base DAO y aplica principios de POO Segura.
    """
    def __init__(self, conexion):
        super().__init__(conexion)
        self.ultimo_error: str = ""

    def crear_tablas(self):
        """Crea las tablas de venta, detalle_venta, cliente y receta_medica si no existen."""
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS cliente (
                    rut TEXT PRIMARY KEY,
                    nombre TEXT NOT NULL
                );
            """)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS receta_medica (
                    numero_receta TEXT PRIMARY KEY,
                    fecha_emision TEXT NOT NULL
                );
            """)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS venta (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha TEXT NOT NULL,
                    cliente_rut TEXT NOT NULL,
                    vendedor_rut TEXT NOT NULL,
                    numero_receta TEXT,
                    total REAL NOT NULL,
                    FOREIGN KEY (cliente_rut) REFERENCES cliente(rut),
                    FOREIGN KEY (vendedor_rut) REFERENCES vendedor(rut),
                    FOREIGN KEY (numero_receta) REFERENCES receta_medica(numero_receta)
                );
            """)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS detalle_venta (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    venta_id INTEGER NOT NULL,
                    medicamento_id INTEGER NOT NULL,
                    cantidad INTEGER NOT NULL,
                    precio_unitario REAL NOT NULL,
                    subtotal REAL NOT NULL,
                    FOREIGN KEY (venta_id) REFERENCES venta(id),
                    FOREIGN KEY (medicamento_id) REFERENCES medicamento(codigo)
                );
            """)
            self.conexion.commit()
        except Exception as e:
            print(f"Error al crear las tablas de Venta: {e}")

    def guardar_venta(self, venta: Venta, tasa_dolar: float = 1.0) -> bool:
        """
        Guarda la venta de forma atómica (transaccional).
        1. Valida que exista stock suficiente para cada medicamento solicitado.
        2. Registra o actualiza al cliente.
        3. Registra la receta médica si aplica.
        4. Inserta el encabezado de venta y sincroniza el ID con el objeto Venta.
        5. Inserta los detalles de venta.
        6. Descuenta el stock físico de cada medicamento vendido.
        Si alguna operación falla, revierte la transacción íntegramente (Rollback).
        """
        self.ultimo_error = ""
        try:
            # 1. Validación preventiva de Stock en la Base de Datos
            for d in venta.detalles:
                self.cursor.execute("SELECT stock, nombre FROM medicamento WHERE codigo = ?;", (d.medicamento.codigo,))
                fila = self.cursor.fetchone()
                if not fila:
                    self.conexion.rollback()
                    self.ultimo_error = f"El medicamento '{d.medicamento.nombre}' (código {d.medicamento.codigo}) no existe en el inventario."
                    return False
                
                stock_disponible, nombre_med = fila[0], fila[1]
                if stock_disponible < d.cantidad:
                    self.conexion.rollback()
                    self.ultimo_error = f"Stock insuficiente para '{nombre_med}'. Disponible: {stock_disponible}, solicitado: {d.cantidad}."
                    return False

            # 2. Registrar o Actualizar Cliente
            self.cursor.execute("SELECT rut FROM cliente WHERE rut = ?;", (venta.cliente.rut,))
            if self.cursor.fetchone():
                self.cursor.execute("""
                    UPDATE cliente SET nombre = ? WHERE rut = ?;
                """, (venta.cliente.nombre, venta.cliente.rut))
            else:
                self.cursor.execute("""
                    INSERT INTO cliente (rut, nombre) VALUES (?, ?);
                """, (venta.cliente.rut, venta.cliente.nombre))

            # 3. Registrar Receta Médica si aplica
            num_receta = None
            if venta.receta_medica:
                num_receta = venta.receta_medica.numero_receta
                self.cursor.execute("""
                    INSERT OR REPLACE INTO receta_medica (numero_receta, fecha_emision) VALUES (?, ?);
                """, (num_receta, venta.receta_medica.fecha_emision))

            total_venta = venta.calcular_total(tasa_dolar)

            # 4. Registrar Encabezado de Venta
            self.cursor.execute("""
                INSERT INTO venta (fecha, cliente_rut, vendedor_rut, numero_receta, total)
                VALUES (?, ?, ?, ?, ?);
            """, (venta.fecha, venta.cliente.rut, venta.vendedor_rut, num_receta, total_venta))
            
            venta_id = self.cursor.lastrowid
            venta.id = venta_id  # Sincronizamos el ID autogenerado con la instancia de dominio

            # 5. Registrar Detalles de Venta y Descontar Stock
            for d in venta.detalles:
                subtotal = d.calcular_subtotal()
                self.cursor.execute("""
                    INSERT INTO detalle_venta (venta_id, medicamento_id, cantidad, precio_unitario, subtotal)
                    VALUES (?, ?, ?, ?, ?);
                """, (venta_id, d.medicamento.codigo, d.cantidad, d.precio_unitario, subtotal))

                # Descuento seguro de stock
                self.cursor.execute("""
                    UPDATE medicamento
                    SET stock = stock - ?
                    WHERE codigo = ?;
                """, (d.cantidad, d.medicamento.codigo))

            self.conexion.commit()
            return True

        except Exception as e:
            self.conexion.rollback()
            self.ultimo_error = f"Error en transacción de venta: {str(e)}"
            print(f"Error al registrar la venta: {e}")
            return False

    def obtener_todas(self) -> pd.DataFrame:
        """
        Retorna el historial completo de ventas enriquecido con información
        del cliente, vendedor y receta médica como DataFrame de Pandas.
        """
        try:
            query = """
                SELECT 
                    v.id AS id_venta,
                    v.fecha,
                    v.cliente_rut,
                    COALESCE(c.nombre, 'Sin nombre') AS cliente_nombre,
                    v.vendedor_rut,
                    COALESCE(vend.nombre, 'Desconocido') AS vendedor_nombre,
                    COALESCE(vend.esfarmaceutico, 0) AS esfarmaceutico,
                    v.numero_receta,
                    rm.fecha_emision AS fecha_receta,
                    v.total
                FROM venta v
                LEFT JOIN cliente c ON v.cliente_rut = c.rut
                LEFT JOIN vendedor vend ON v.vendedor_rut = vend.rut
                LEFT JOIN receta_medica rm ON v.numero_receta = rm.numero_receta
                ORDER BY v.id DESC;
            """
            return pd.read_sql_query(query, self.conexion)
        except Exception as e:
            print(f"Error al obtener ventas: {e}")
            return pd.DataFrame()

    def obtener_por_id(self, venta_id: int):
        """Retorna los datos de cabecera de una venta específica por su ID."""
        try:
            query = """
                SELECT 
                    v.id AS id_venta,
                    v.fecha,
                    v.cliente_rut,
                    c.nombre AS cliente_nombre,
                    v.vendedor_rut,
                    vend.nombre AS vendedor_nombre,
                    vend.esfarmaceutico,
                    v.numero_receta,
                    rm.fecha_emision AS fecha_receta,
                    v.total
                FROM venta v
                LEFT JOIN cliente c ON v.cliente_rut = c.rut
                LEFT JOIN vendedor vend ON v.vendedor_rut = vend.rut
                LEFT JOIN receta_medica rm ON v.numero_receta = rm.numero_receta
                WHERE v.id = ?;
            """
            self.cursor.execute(query, (venta_id,))
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Error al buscar venta #{venta_id}: {e}")
            return None

    def obtener_detalles_por_venta(self, venta_id: int) -> pd.DataFrame:
        """
        Retorna todas las líneas de detalle de una venta específica,
        incluyendo el nombre del producto y si requiere receta.
        """
        try:
            query = """
                SELECT 
                    dv.id AS id_detalle,
                    dv.medicamento_id AS codigo_medicamento,
                    COALESCE(m.nombre, 'Medicamento Eliminado') AS nombre_medicamento,
                    COALESCE(m.restringido, 0) AS restringido,
                    dv.cantidad,
                    dv.precio_unitario,
                    dv.subtotal
                FROM detalle_venta dv
                LEFT JOIN medicamento m ON dv.medicamento_id = m.codigo
                WHERE dv.venta_id = ?
                ORDER BY dv.id ASC;
            """
            return pd.read_sql_query(query, self.conexion, params=(venta_id,))
        except Exception as e:
            print(f"Error al obtener detalles de la venta #{venta_id}: {e}")
            return pd.DataFrame()