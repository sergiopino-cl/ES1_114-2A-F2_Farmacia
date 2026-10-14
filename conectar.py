import sqlite3

def crear_conexion() -> sqlite3.Connection :
    conexion = sqlite3.connect("farmacia.db")
    conexion.execute("PRAGMA foreign_keys = ON")
    return conexion