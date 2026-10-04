"""Servidor UDP: pide una clave y devuelve el texto recibido en formato Frase.

Como UDP no tiene conexión, el servidor recuerda qué direcciones (ip, puerto)
ya enviaron la clave correcta.

Uso:  py servidor_udp.py
"""
import socket

from comun import (CLAVE, CMD_SALIR, CODIFICACION, HOST_ESCUCHA, PUERTO_UDP,
                   RESP_ERROR, RESP_OK, TAM_BUFFER, formato_frase)

# Cada cuántos segundos "despierta" recvfrom() para poder atender Ctrl+C
INTERVALO = 1


def main():
    # SOCK_DGRAM = UDP
    servidor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    servidor.bind((HOST_ESCUCHA, PUERTO_UDP))  # en UDP no hay listen() ni accept()
    servidor.settimeout(INTERVALO)             # para que Ctrl+C funcione en Windows
    print(f"[UDP] Servidor escuchando en el puerto {PUERTO_UDP}... (Ctrl+C para terminar)")

    autenticados = set()  # direcciones (ip, puerto) que ya enviaron la clave

    try:
        while True:
            try:
                # recvfrom() devuelve los datos Y la dirección de quien los envió
                datos, direccion = servidor.recvfrom(TAM_BUFFER)
            except socket.timeout:
                continue  # no llegó nada en 1 s: se vuelve a esperar
            except ConnectionResetError:
                # En Windows, un ICMP "port unreachable" de un cliente que ya
                # cerró aparece aquí como error. Se ignora y se sigue.
                continue

            texto = datos.decode(CODIFICACION).strip()

            if direccion not in autenticados:
                # Primer datagrama de esta dirección: se interpreta como la clave
                if texto == CLAVE:
                    autenticados.add(direccion)
                    print(f"[UDP] {direccion} -> clave correcta.")
                    servidor.sendto(RESP_OK.encode(CODIFICACION), direccion)
                else:
                    print(f"[UDP] {direccion} -> clave incorrecta. No se procesa.")
                    servidor.sendto(RESP_ERROR.encode(CODIFICACION), direccion)
                continue

            if texto.lower() == CMD_SALIR:
                autenticados.discard(direccion)
                print(f"[UDP] {direccion} pidió salir.")
                continue

            respuesta = formato_frase(texto)
            print(f"[UDP] {direccion} recibido: {texto!r} -> enviado: {respuesta!r}")
            # sendto() necesita la dirección de destino en cada envío
            servidor.sendto(respuesta.encode(CODIFICACION), direccion)
    except KeyboardInterrupt:
        print("\n[UDP] Servidor detenido.")
    finally:
        servidor.close()


if __name__ == "__main__":
    main()
