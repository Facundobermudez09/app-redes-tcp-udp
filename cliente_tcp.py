"""Cliente TCP: envía la clave y luego textos para convertir a formato Frase.

Uso:  py cliente_tcp.py [ip_servidor]
"""
import socket
import sys

from comun import (CMD_SALIR, CODIFICACION, HOST_SERVIDOR, PUERTO_TCP,
                   RESP_OK, TAM_BUFFER)


def main():
    host = sys.argv[1] if len(sys.argv) > 1 else HOST_SERVIDOR

    # SOCK_STREAM = TCP
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # connect() realiza el handshake de 3 vías (SYN, SYN+ACK, ACK)
        cliente.connect((host, PUERTO_TCP))
    except ConnectionRefusedError:
        print(f"[TCP] No se pudo conectar: el servidor {host}:{PUERTO_TCP} "
              "no está disponible (conexión rechazada).")
        cliente.close()
        return
    except (TimeoutError, OSError) as e:
        print(f"[TCP] No se pudo conectar con {host}:{PUERTO_TCP}: {e}")
        cliente.close()
        return

    print(f"[TCP] Conectado a {host}:{PUERTO_TCP}")

    with cliente:
        # 1) Autenticación
        clave = input("Ingrese la clave: ")
        cliente.sendall(clave.encode(CODIFICACION))
        respuesta = cliente.recv(TAM_BUFFER).decode(CODIFICACION)
        if respuesta != RESP_OK:
            print("[TCP] Clave incorrecta. Acceso denegado.")
            return
        print("[TCP] Clave correcta. Escriba un texto ('salir' para terminar).")

        # 2) Envío de textos
        while True:
            texto = input("> ")
            if not texto.strip():
                continue
            # send()/recv() no llevan dirección: el socket ya está conectado
            cliente.sendall(texto.encode(CODIFICACION))
            if texto.strip().lower() == CMD_SALIR:
                break
            datos = cliente.recv(TAM_BUFFER)
            if not datos:
                print("[TCP] El servidor cerró la conexión.")
                break
            print("Servidor:", datos.decode(CODIFICACION))

    print("[TCP] Conexión cerrada.")


if __name__ == "__main__":
    main()
