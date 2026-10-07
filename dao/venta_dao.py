import pandas as pd
from model.venta import Venta

class VentaDAO:
    def __init__(self, conexion):
        self.conexion = conexion
        self.cursor = conexion.cursor()

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
        """Guarda la venta completa con su cliente, receta y detalles mediante transacción."""
        try:
            # 1. Registrar/Asegurar Cliente
            self.cursor.execute("""
                INSERT OR REPLACE INTO cliente (rut, nombre) VALUES (?, ?);
            """, (venta.cliente.rut, venta.cliente.nombre))

            # 2. Registrar Receta si existe
            num_receta = None
            if venta.receta_medica:
                num_receta = venta.receta_medica.numero_receta
                self.cursor.execute("""
                    INSERT OR REPLACE INTO receta_medica (numero_receta, fecha_emision) VALUES (?, ?);
                """, (num_receta, venta.receta_medica.fecha_emision))

            total_venta = venta.calcular_total(tasa_dolar)

            # 3. Registrar Encabezado de Venta
            self.cursor.execute("""
                INSERT INTO venta (fecha, cliente_rut, vendedor_rut, numero_receta, total)
                VALUES (?, ?, ?, ?, ?);
            """, (venta.fecha, venta.cliente.rut, venta.vendedor_rut, num_receta, total_venta))
            
            venta_id = self.cursor.lastrowid

            # 4. Registrar Detalle de Venta
            for d in venta.detalles:
                subtotal = d.calcular_subtotal()
                self.cursor.execute("""
                    INSERT INTO detalle_venta (venta_id, medicamento_id, cantidad, precio_unitario, subtotal)
                    VALUES (?, ?, ?, ?, ?);
                """, (venta_id, d.medicamento.codigo, d.cantidad, d.precio_unitario, subtotal))

            self.conexion.commit()
            return True
        except Exception as e:
            self.conexion.rollback()
            print(f"Error al registrar la venta: {e}")
            return False

    def obtener_todas(self):
        """Retorna el historial de ventas como DataFrame."""
        try:
            query = """
                SELECT v.id, v.fecha, v.cliente_rut, c.nombre AS cliente_nombre, 
                       v.vendedor_rut, v.numero_receta, v.total
                FROM venta v
                JOIN cliente c ON v.cliente_rut = c.rut;
            """
            return pd.read_sql_query(query, self.conexion)
        except Exception as e:
            print(f"Error al obtener ventas: {e}")
            return pd.DataFrame()