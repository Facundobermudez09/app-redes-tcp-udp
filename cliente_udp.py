"""Cliente UDP: envía la clave y luego textos para convertir a formato Frase.

Uso:  py cliente_udp.py [ip_servidor]
"""
import socket
import sys

from comun import (CMD_SALIR, CODIFICACION, HOST_SERVIDOR, PUERTO_UDP,
                   RESP_OK, TAM_BUFFER)

TIEMPO_ESPERA = 3  # segundos que se espera una respuesta antes de rendirse


def enviar_y_esperar(cliente, servidor, mensaje):
    """Envía un datagrama y espera la respuesta. Devuelve None si no llega."""
    # sendto() no establece conexión: solo envía el datagrama a esa dirección
    cliente.sendto(mensaje.encode(CODIFICACION), servidor)
    try:
        datos, _ = cliente.recvfrom(TAM_BUFFER)
        return datos.decode(CODIFICACION)
    except socket.timeout:
        print(f"[UDP] Sin respuesta después de {TIEMPO_ESPERA} s: "
              "el servidor no está disponible o el datagrama se perdió.")
    except ConnectionResetError:
        # En Windows: llegó un ICMP "port unreachable" (nadie escucha en ese puerto)
        print("[UDP] El host respondió que no hay ningún servidor en ese puerto "
              "(ICMP port unreachable).")
    return None


def main():
    host = sys.argv[1] if len(sys.argv) > 1 else HOST_SERVIDOR
    servidor = (host, PUERTO_UDP)

    # SOCK_DGRAM = UDP. No hay connect(): no existe handshake
    cliente = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    cliente.settimeout(TIEMPO_ESPERA)

    with cliente:
        # 1) Autenticación
        clave = input("Ingrese la clave: ")
        respuesta = enviar_y_esperar(cliente, servidor, clave)
        if respuesta is None:
            return
        if respuesta != RESP_OK:
            print("[UDP] Clave incorrecta. Acceso denegado.")
            return
        print("[UDP] Clave correcta. Escriba un texto ('salir' para terminar).")

        # 2) Envío de textos
        while True:
            texto = input("> ")
            if not texto.strip():
                continue
            if texto.strip().lower() == CMD_SALIR:
                cliente.sendto(texto.encode(CODIFICACION), servidor)
                break
            respuesta = enviar_y_esperar(cliente, servidor, texto)
            if respuesta is None:
                break
            print("Servidor:", respuesta)

    print("[UDP] Cliente terminado.")


if __name__ == "__main__":
    main()
