from dao.dao import DAO
from model.vendedor import Vendedor

import pandas as pd

class VendedorDAO(DAO):
    def __init__(self, conexion):
        self.conexion = conexion
        self.cursor = conexion.cursos()
    
    def crear_tabla(self):
        """Crea la tabla vendedor si no existe."""
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS vendedor (
                    rut TEXT PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    esfarmaceutico BOOLEAN 
                )
            """)
            self.conexion.commit()
        except Exception as e:
            print(f"Error al crear la tabla vendedor: {e}")

    def insertar(self, vendedor: Vendedor):
        """Inserta un nuevo vendedor en la base de datos."""
        try:
            self.cursor.execute("""
                INSERT INTO vendedor (rut, nombre, esfarmaceutico)
                VALUES (?, ?, ?);
            """, (vendedor.rut, vendedor.nombre, vendedor.esfarmaceutico))
            self.conexion.commit()
            return True
        except Exception as e:
            print(f"Error al insertar vendedor: {e}")
            return False

    def obtener_todos(self):
        """Retorna todos los vendedores en formato DataFrame de Pandas (ideal para Streamlit)."""
        try:
            query = "SELECT * FROM vendedor;"
            return pd.read_sql_query(query, self.conexion)
        except Exception as e:
            print(f"Error al obtener vendedores: {e}")
            return pd.DataFrame()

    def obtener_por_rut(self, rut):
        """Busca un vendedor específico por su RUT."""
        try:
            self.cursor.execute("SELECT * FROM vendedor WHERE rut = ?;", (rut,))
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Error al buscar vendedor: {e}")
            return None

    def actualizar(self, rut, nombre, esfarmaceutico):
        """Actualiza los datos de un vendedor existente."""
        try:
            self.cursor.execute("""
                UPDATE vendedor 
                SET nombre = ?, esfarmaceutico = ? 
                WHERE rut = ?;
            """, (nombre, esfarmaceutico, rut))
            self.conexion.commit()
            return True
        except Exception as e:
            print(f"Error al actualizar vendedor: {e}")
            return False

    def eliminar(self, rut):
        """Elimina un vendedor por su RUT."""
        try:
            self.cursor.execute("DELETE FROM vendedor WHERE rut = ?;", (rut,))
            self.conexion.commit()
            return True
        except Exception as e:
            print(f"Error al eliminar vendedor: {e}")
            return False