import pandas as pd
from model.medicamento import Medicamento

class MedicamentoDAO:
    def __init__(self, conexion):
        self.conexion = conexion
        self.cursor = conexion.cursor()

    def crear_tabla(self):
        """Crea la tabla medicamento si no existe."""
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS medicamento (
                    codigo INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    precio_venta INTEGER NOT NULL,
                    precio_compra_usd REAL NOT NULL,
                    precio_compra_peso INTEGER NOT NULL,
                    fecha_ultima_compra TEXT NOT NULL,
                    restringido BOOLEAN NOT NULL,
                    stock INTEGER NOT NULL DEFAULT 0
                );
            """)
            self.conexion.commit()
        except Exception as e:
            print(f"Error al crear la tabla medicamento: {e}")

    def insertar(self, medicamento: Medicamento):
        """Inserta un objeto Medicamento en la base de datos."""
        try:
            self.cursor.execute("""
                INSERT INTO medicamento (
                    nombre, 
                    precio_venta, 
                    precio_compra_usd, 
                    precio_compra_peso, 
                    fecha_ultima_compra, 
                    restringido,
                    stock
                ) VALUES (?, ?, ?, ?, ?, ?, ?);
            """, (
                medicamento.nombre,
                medicamento.precio_venta,
                medicamento.precio_compra_usd,
                medicamento.precio_compra_peso,
                medicamento.fecha_ultima_compra,
                medicamento.restringido,
                medicamento.stock
            ))
            self.conexion.commit()
            return True
        except Exception as e:
            print(f"Error al insertar medicamento: {e}")
            return False

    def obtener_todos(self):
        """Retorna todos los medicamentos en formato DataFrame."""
        try:
            query = "SELECT * FROM medicamento;"
            return pd.read_sql_query(query, self.conexion)
        except Exception as e:
            print(f"Error al obtener medicamentos: {e}")
            return pd.DataFrame()

    def obtener_todos_objetos(self):
        """Retorna una lista de objetos Medicamento (no tuplas ni dataframes). para solucionar problema en la edición"""
        try:
            self.cursor.execute("SELECT * FROM medicamento;")
            filas = self.cursor.fetchall()
            medicamentos = []
            for row in filas:
                med = Medicamento(
                    codigo=row[0],
                    nombre=row[1],
                    precio_venta=row[2],
                    precio_compra_usd=row[3],
                    precio_compra_peso=row[4],
                    fecha_ultima_compra=row[5],
                    restringido=bool(row[6]),
                    stock=row[7]
                )
                medicamentos.append(med)
            return medicamentos
        except Exception as e:
            print(f"Error al obtener lista de objetos medicamento: {e}")
            return []

    def obtener_por_codigo(self, codigo: int):
        """Busca un medicamento específico por su código de clave primaria."""
        try:
            self.cursor.execute("SELECT * FROM medicamento WHERE codigo = ?;", (codigo,))
            return self.cursor.fetchone()
            if row:
                return Medicamento(
                    codigo=row[0],
                    nombre=row[1],
                    precio_venta=row[2],
                    precio_compra_usd=row[3],
                    precio_compra_peso=row[4],
                    fecha_ultima_compra=row[5],
                    restringido=bool(row[6]),
                    stock=row[7]
                )
            return None
        except Exception as e:
            print(f"Error al buscar medicamento: {e}")
            return None

    def actualizar(self, medicamento: Medicamento):
        """Actualiza un medicamento existente."""
        try:
            self.cursor.execute("""
                UPDATE medicamento 
                SET nombre = ?, 
                    precio_venta = ?, 
                    precio_compra_usd = ?, 
                    precio_compra_peso = ?, 
                    fecha_ultima_compra = ?, 
                    restringido = ?,
                    stock = ?
                WHERE codigo = ?;
            """, (
                medicamento.nombre,
                medicamento.precio_venta,
                medicamento.precio_compra_usd,
                medicamento.precio_compra_peso,
                medicamento.fecha_ultima_compra,
                medicamento.restringido,
                medicamento.stock,
                medicamento.codigo
            ))
            self.conexion.commit()
            return True
        except Exception as e:
            print(f"Error al actualizar medicamento: {e}")
            return False

    def eliminar(self, codigo: int):
        """Elimina un medicamento por su código."""
        try:
            self.cursor.execute("DELETE FROM medicamento WHERE codigo = ?;", (codigo,))
            self.conexion.commit()
            return True
        except Exception as e:
            print(f"Error al eliminar medicamento: {e}")
            return False