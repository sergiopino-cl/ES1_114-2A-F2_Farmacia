from conectar import crear_conexion
from servicios.miindicador import MiIndicador
import sys

def menu():
    print("\n" + "="*30)
    print("   MANTENEDOR DE MEDICAMENTOS Y VENDEDORES")
    print("="*30)
    print("1. Crear un Vendedor")
    print("2. Listar vendedores")
    print("3. Buscar vendedor por tipo e ID")
    print("4. Actualizar una Marca")
    print("5. Eliminar una Marca")
    print("6. Cotizar Repuesto")
    print("7. Salir")
    print("="*30)
    return input("Seleccione una opción: ")

def main():
    try:
        conexion = crear_conexion()
        vendedor_dao = VendedorDAO(conexion)
        # Asegurarnos que la tabla exista antes de operar
        marca_dao.crear_tabla()
        conexion.commit()
    except Exception as e:
        print(f"Error al conectar con la base de datos: {e}")
        sys.exit(1)
