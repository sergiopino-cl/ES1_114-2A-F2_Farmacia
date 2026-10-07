import requests

class MiIndicador:
    BASE_URL ="https://mindicador.cl/api/"

    def __init__(self, timeout=5):
        self.__timeout=timeout

    def obtener_valor(self, codigo, fecha=None):
        url= self.BASE_URL + codigo
        if fecha:
            url += f"/{fecha}"
            
        respuesta = requests.get(url, timeout=self.__timeout)
        respuesta.raise_for_status()
        datos = respuesta.json()

        # Si se consulta por fecha específica, el JSON trae la estructura de ese día
        # Si se consulta general (ej: "dolar"), la serie trae la lista de valores recientes
        if "serie" in datos and len(datos["serie"]) > 0:
            return float(datos["serie"][0]["valor"])
        elif "serie" in datos and len(datos["serie"]) == 0:
            return None
        else:
            return float(datos.get("valor", 0))
