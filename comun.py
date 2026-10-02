"""Configuración y funciones compartidas por los clientes y servidores TCP/UDP."""

# Clave que el servidor exige antes de procesar cualquier texto
CLAVE = "redes2026"

# IP del servidor por defecto (localhost). Se puede cambiar por argumento:
#   py cliente_tcp.py 192.168.1.10
HOST_SERVIDOR = "127.0.0.1"

# "0.0.0.0" = el servidor escucha en todas las interfaces de la PC
HOST_ESCUCHA = "0.0.0.0"

PUERTO_TCP = 5000
PUERTO_UDP = 5001

TAM_BUFFER = 1024
CODIFICACION = "utf-8"  # necesario para letras con tilde (programación)

# Respuestas del protocolo de autenticación
RESP_OK = "OK"
RESP_ERROR = "ERROR"
CMD_SALIR = "salir"


def formato_frase(texto):
    """Devuelve el texto con la primera letra de cada palabra en mayúscula.

    >>> formato_frase("programación de redes con python")
    'Programación De Redes Con Python'
    """
    palabras = texto.split()
    return " ".join(p[:1].upper() + p[1:].lower() for p in palabras)
