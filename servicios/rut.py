# Calculo del digito verifi cador de RUT

def obtener_dv(rut):
  rut_limpio = "".join(filter(str.isdigit, str(rut)))[::-1]
  suma, multiplicador = 0, 2

  for digito in rut_limpio:
    suma += int(digito) * multiplicador
    multiplicador = 2 if multiplicador == 7 else multiplicador + 1

  resto = 11 - (suma % 11)
  if resto == 11:
    return "0"
  if resto == 10:
    return "K"
  return str(resto)