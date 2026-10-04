"""Servidor TCP: pide una clave y devuelve el texto recibido en formato Frase.

Uso:  py servidor_tcp.py
"""
import socket

from comun import (CLAVE, CMD_SALIR, CODIFICACION, HOST_ESCUCHA, PUERTO_TCP,
                   RESP_ERROR, RESP_OK, TAM_BUFFER, formato_frase)

# Cada cuántos segundos "despiertan" accept()/recv() para poder atender Ctrl+C
INTERVALO = 1


def recibir(conexion):
    """recv() que se puede interrumpir con Ctrl+C en Windows."""
    while True:
        try:
            return conexion.recv(TAM_BUFFER)
        except socket.timeout:
            continue  # no llegó nada en 1 s: se vuelve a esperar


def atender_cliente(conexion, direccion):
    """Atiende a un cliente ya conectado (la conexión TCP ya está establecida)."""
    # 1) Primer mensaje: la clave
    clave = recibir(conexion).decode(CODIFICACION).strip()
    if clave != CLAVE:
        print(f"[TCP] {direccion} -> clave incorrecta. Se cierra la conexión.")
        conexion.sendall(RESP_ERROR.encode(CODIFICACION))
        return  # no se ejecuta el programa

    print(f"[TCP] {direccion} -> clave correcta.")
    conexion.sendall(RESP_OK.encode(CODIFICACION))

    # 2) Bucle de trabajo: recibir texto, convertirlo y devolverlo
    while True:
        datos = recibir(conexion)
        if not datos:  # recv() devuelve b"" cuando el cliente cerró la conexión
            print(f"[TCP] {direccion} cerró la conexión.")
            break

        texto = datos.decode(CODIFICACION)
        if texto.strip().lower() == CMD_SALIR:
            print(f"[TCP] {direccion} pidió salir.")
            break

        respuesta = formato_frase(texto)
        print(f"[TCP] {direccion} recibido: {texto!r} -> enviado: {respuesta!r}")
        conexion.sendall(respuesta.encode(CODIFICACION))


def main():
    # SOCK_STREAM = TCP
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    servidor.bind((HOST_ESCUCHA, PUERTO_TCP))  # asocia el socket a IP:puerto
    servidor.listen(5)                         # lo pone en modo escucha (cola de 5)
    servidor.settimeout(INTERVALO)             # para que Ctrl+C funcione en Windows
    print(f"[TCP] Servidor escuchando en el puerto {PUERTO_TCP}... (Ctrl+C para terminar)")

    try:
        while True:
            # accept() bloquea hasta que termina el handshake de un cliente y
            # devuelve un socket NUEVO dedicado a esa conexión
            try:
                conexion, direccion = servidor.accept()
            except socket.timeout:
                continue  # ningún cliente en 1 s: se vuelve a esperar
            conexion.settimeout(INTERVALO)
            print(f"[TCP] Conexión aceptada desde {direccion}")
            with conexion:
                try:
                    atender_cliente(conexion, direccion)
                except ConnectionError as e:
                    print(f"[TCP] Se perdió la conexión con {direccion}: {e}")
    except KeyboardInterrupt:
        print("\n[TCP] Servidor detenido.")
    finally:
        servidor.close()


if __name__ == "__main__":
    main()
