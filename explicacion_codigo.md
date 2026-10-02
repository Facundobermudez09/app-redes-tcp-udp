# Explicación del código, línea por línea

Este documento explica cada archivo del proyecto para que cualquiera del grupo pueda defenderlo en la exposición. Los números de línea (**L14**, **L42–43**) coinciden con los de los archivos `.py`.

Orden recomendado de lectura:

1. [Conceptos previos](#conceptos-previos)
2. [`comun.py`](#1-comunpy): configuración y la función de formato
3. [`servidor_tcp.py`](#2-servidor_tcppy)
4. [`cliente_tcp.py`](#3-cliente_tcppy)
5. [`servidor_udp.py`](#4-servidor_udppy)
6. [`cliente_udp.py`](#5-cliente_udppy)
7. [Comparación TCP vs UDP en nuestro código](#6-comparación-tcp-vs-udp-en-nuestro-código)
8. [Preguntas que nos pueden hacer](#7-preguntas-que-nos-pueden-hacer)

---

## Conceptos previos

| Concepto | Qué significa |
|---|---|
| **Socket** | Un "enchufe" de red: el punto por donde un programa envía y recibe datos. Se identifica por **IP + puerto**. |
| `socket.AF_INET` | Familia de direcciones **IPv4** (direcciones del tipo `192.168.1.10`). |
| `socket.SOCK_STREAM` | Tipo de socket **TCP**: flujo de bytes, con conexión y confiable. |
| `socket.SOCK_DGRAM` | Tipo de socket **UDP**: datagramas independientes, sin conexión. |
| **Puerto** | Número (0–65535) que identifica a qué programa van los datos dentro de una PC. Usamos 5000 (TCP) y 5001 (UDP). |
| `str` vs `bytes` | Por la red solo viajan **bytes**. `texto.encode("utf-8")` convierte texto en bytes; `datos.decode("utf-8")` hace lo contrario. |
| **Bloqueante** | `accept()`, `recv()`, `recvfrom()` e `input()` **detienen el programa** hasta que llega algo. Por eso el servidor "se queda esperando". |
| `127.0.0.1` | *localhost*: la propia PC. Sirve para probar cliente y servidor en la misma máquina. |
| `0.0.0.0` | En un servidor significa "escuchar en **todas** las interfaces de red de la PC" (Wi-Fi, cable, localhost). |

---

## 1. `comun.py`

Contiene lo que comparten los 4 programas. Si se quiere cambiar la clave o un puerto, se cambia **solo acá**.

```python
1  """Configuración y funciones compartidas por los clientes y servidores TCP/UDP."""
```
- **L1**: *docstring* del módulo, un texto que describe el archivo. No ejecuta nada.

```python
3  # Clave que el servidor exige antes de procesar cualquier texto
4  CLAVE = "redes2026"
```
- **L4**: la clave del sistema. Los servidores comparan contra este valor. En Python, los nombres en MAYÚSCULAS indican **constantes**: valores que no se modifican durante la ejecución.

```python
6  # IP del servidor por defecto (localhost). Se puede cambiar por argumento:
7  #   py cliente_tcp.py 192.168.1.10
8  HOST_SERVIDOR = "127.0.0.1"
```
- **L8**: IP a la que se conectan los **clientes** si no se indica otra. `127.0.0.1` es la misma PC.

```python
10 # "0.0.0.0" = el servidor escucha en todas las interfaces de la PC
11 HOST_ESCUCHA = "0.0.0.0"
```
- **L11**: IP que usan los **servidores** en `bind()`. Con `0.0.0.0` aceptan conexiones desde la misma PC y desde otras PCs de la red.

```python
13 PUERTO_TCP = 5000
14 PUERTO_UDP = 5001
```
- **L13–14**: puertos de cada servidor. Se usan puertos mayores a 1023 porque los menores (*well-known*, como el 80 de HTTP) están reservados.

```python
16 TAM_BUFFER = 1024
17 CODIFICACION = "utf-8"  # necesario para letras con tilde (programación)
```
- **L16**: cantidad máxima de bytes que se leen en cada `recv()` / `recvfrom()`.
- **L17**: codificación del texto. UTF-8 representa tildes y ñ; con ASCII, "programación" daría error.

```python
19 # Respuestas del protocolo de autenticación
20 RESP_OK = "OK"
21 RESP_ERROR = "ERROR"
22 CMD_SALIR = "salir"
```
- **L20–22**: las "palabras" de **nuestro protocolo de aplicación**:
  - el servidor responde `OK` o `ERROR` a la clave;
  - el cliente manda `salir` para terminar.

  Cliente y servidor tienen que usar las mismas, por eso están en este archivo común.

```python
25 def formato_frase(texto):
26     """Devuelve el texto con la primera letra de cada palabra en mayúscula.
...
30     """
31     palabras = texto.split()
32     return " ".join(p[:1].upper() + p[1:].lower() for p in palabras)
```
- **L25**: define la función que hace la transformación pedida por el enunciado.
- **L31**: `split()` separa el texto en una lista de palabras, usando los espacios. Ejemplo: `"hola  mundo"` → `["hola", "mundo"]`. También descarta los espacios repetidos.
- **L32**, de adentro hacia afuera:
  - `p[:1]` es la **primera letra** de la palabra `p`, y `.upper()` la pasa a mayúscula.
  - `p[1:]` es **el resto** de la palabra, y `.lower()` lo pasa a minúscula. Así `"MUNDO"` queda `"Mundo"`.
  - `for p in palabras` repite eso para cada palabra.
  - `" ".join(...)` vuelve a unir las palabras con un espacio.
- **¿Por qué no `texto.title()`?** Porque `title()` también pone mayúscula después de un apóstrofo: `"don't"` → `"Don'T"`.

---

## 2. `servidor_tcp.py`

```python
5  import socket
7  from comun import (CLAVE, CMD_SALIR, CODIFICACION, HOST_ESCUCHA, PUERTO_TCP,
8                     RESP_ERROR, RESP_OK, TAM_BUFFER, formato_frase)
```
- **L5**: importa el módulo `socket`, la **API de sockets** de Python.
- **L7–8**: trae de `comun.py` las constantes y la función que usa este archivo.

### Función `atender_cliente` (L11–37): qué hace el servidor con UN cliente

```python
11 def atender_cliente(conexion, direccion):
```
- **L11**: recibe dos parámetros:
  - `conexion`: el socket **exclusivo** de ese cliente, que devolvió `accept()`;
  - `direccion`: la tupla `(ip, puerto)` del cliente.

```python
14     clave = conexion.recv(TAM_BUFFER).decode(CODIFICACION).strip()
```
- **L14**: lee el **primer mensaje**, que por protocolo es la clave. Se hacen tres cosas encadenadas:
  1. `recv(1024)`: espera y recibe hasta 1024 bytes.
  2. `.decode("utf-8")`: convierte los bytes en texto.
  3. `.strip()`: quita espacios y saltos de línea en los extremos.

```python
15     if clave != CLAVE:
16         print(f"[TCP] {direccion} -> clave incorrecta. Se cierra la conexión.")
17         conexion.sendall(RESP_ERROR.encode(CODIFICACION))
18         return  # no se ejecuta el programa
```
- **L15**: compara la clave recibida con la correcta.
- **L16**: muestra en la consola del servidor qué pasó. La `f` antes de las comillas permite meter variables entre `{}`.
- **L17**: le avisa al cliente con `ERROR`. Se usa `sendall()` y no `send()` porque `sendall()` garantiza que se manden **todos** los bytes.
- **L18**: `return` sale de la función **sin procesar ningún texto**. Esto cumple la consigna: "si no coincide, no debe ejecutar el programa". Después, el `with` de `main()` cierra la conexión.

```python
20     print(f"[TCP] {direccion} -> clave correcta.")
21     conexion.sendall(RESP_OK.encode(CODIFICACION))
```
- **L20–21**: la clave es correcta, así que lo registra y responde `OK`.

```python
24     while True:
25         datos = conexion.recv(TAM_BUFFER)
26         if not datos:  # recv() devuelve b"" cuando el cliente cerró la conexión
27             print(f"[TCP] {direccion} cerró la conexión.")
28             break
```
- **L24**: bucle infinito: el servidor sigue atendiendo textos hasta que algo lo corte.
- **L25**: espera el siguiente mensaje del cliente.
- **L26–28**: si `recv()` devuelve **bytes vacíos** (`b""`), el cliente cerró la conexión TCP (envió FIN). Entonces se sale del bucle con `break`. Esto es propio de TCP: en UDP no existe "el otro cerró".

```python
30         texto = datos.decode(CODIFICACION)
31         if texto.strip().lower() == CMD_SALIR:
32             print(f"[TCP] {direccion} pidió salir.")
33             break
```
- **L30**: bytes → texto.
- **L31–33**: si el cliente escribió `salir`, sin importar mayúsculas ni espacios, se termina la atención.

```python
35         respuesta = formato_frase(texto)
36         print(f"[TCP] {direccion} recibido: {texto!r} -> enviado: {respuesta!r}")
37         conexion.sendall(respuesta.encode(CODIFICACION))
```
- **L35**: aplica la transformación: `"hola mundo"` → `"Hola Mundo"`.
- **L36**: muestra lo recibido y lo enviado. `!r` muestra el texto entre comillas, así se ven los espacios.
- **L37**: devuelve la respuesta al cliente, convertida a bytes.

### Función `main` (L40–63): preparar el servidor y aceptar clientes

```python
42     servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
```
- **L42**: crea el socket: IPv4 (`AF_INET`) + TCP (`SOCK_STREAM`).

```python
43     servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
```
- **L43**: opción `SO_REUSEADDR`: permite volver a abrir el servidor en el mismo puerto apenas se cierra. Sin esto, a veces el sistema operativo mantiene el puerto ocupado unos segundos y da el error "Address already in use".

```python
45     servidor.bind((HOST_ESCUCHA, PUERTO_TCP))  # asocia el socket a IP:puerto
```
- **L45**: **`bind()`** asocia el socket a la IP `0.0.0.0` y al puerto `5000`. A partir de acá, el sistema operativo sabe que lo que llegue al puerto 5000 es para este programa. Recibe **una tupla** `(ip, puerto)`, por eso lleva doble paréntesis.

```python
46     servidor.listen(5)                         # lo pone en modo escucha (cola de 5)
```
- **L46**: **`listen(5)`** convierte el socket en un socket **pasivo** que acepta conexiones entrantes. El `5` es el tamaño de la **cola**: cuántos clientes pueden quedar esperando mientras el servidor atiende a otro.

```python
47     print(f"[TCP] Servidor escuchando en el puerto {PUERTO_TCP}... (Ctrl+C para terminar)")
```
- **L47**: mensaje informativo.

```python
49     try:
50         while True:
53             conexion, direccion = servidor.accept()
54             print(f"[TCP] Conexión aceptada desde {direccion}")
```
- **L49**: `try` para poder capturar `Ctrl+C` (L60) y cerrar ordenadamente.
- **L50**: el servidor atiende clientes indefinidamente, uno detrás de otro.
- **L53**: **`accept()`** se **bloquea** hasta que un cliente completa el **handshake de 3 vías** (SYN, SYN+ACK, ACK). Devuelve dos cosas:
  - `conexion`: un **socket nuevo**, dedicado solo a ese cliente;
  - `direccion`: la IP y el puerto del cliente.

  El socket `servidor` original sigue escuchando.
- **L54**: registra la conexión.

```python
55             with conexion:
56                 try:
57                     atender_cliente(conexion, direccion)
58                 except ConnectionError as e:
59                     print(f"[TCP] Se perdió la conexión con {direccion}: {e}")
```
- **L55**: `with` garantiza que `conexion.close()` se ejecute al terminar, aunque haya errores. Ese cierre envía el FIN de TCP.
- **L57**: atiende al cliente.
- **L58–59**: si el cliente se desconecta de golpe (por ejemplo, cierra la ventana), se produce un `ConnectionError`. Se informa y el servidor **sigue funcionando** para el próximo cliente.

```python
60     except KeyboardInterrupt:
61         print("\n[TCP] Servidor detenido.")
62     finally:
63         servidor.close()
```
- **L60–61**: `Ctrl+C` genera `KeyboardInterrupt`. Se captura para mostrar un mensaje en vez de un error feo.
- **L62–63**: `finally` se ejecuta siempre: libera el puerto 5000.

```python
66 if __name__ == "__main__":
67     main()
```
- **L66–67**: ejecuta `main()` solo si el archivo se ejecuta directamente (`py servidor_tcp.py`) y no si se importa desde otro archivo. Es una convención de Python.

> **Importante para explicar:** como `atender_cliente()` se ejecuta dentro del mismo bucle que `accept()`, el servidor TCP **atiende a un cliente por vez**. Si otro cliente se conecta mientras tanto, queda esperando en la cola de `listen(5)`.

---

## 3. `cliente_tcp.py`

```python
5  import socket
6  import sys
8  from comun import (CMD_SALIR, CODIFICACION, HOST_SERVIDOR, PUERTO_TCP,
9                     RESP_OK, TAM_BUFFER)
```
- **L6**: `sys` sirve para leer los argumentos de la línea de comandos (la IP del servidor).

```python
13     host = sys.argv[1] if len(sys.argv) > 1 else HOST_SERVIDOR
```
- **L13**: `sys.argv` es la lista de lo que se escribió en la terminal. Con `py cliente_tcp.py 192.168.0.15`:
  - `sys.argv[0]` vale `"cliente_tcp.py"`;
  - `sys.argv[1]` vale `"192.168.0.15"`.

  Si se pasó una IP se usa esa; si no, `127.0.0.1`.

```python
16     cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
```
- **L16**: crea un socket TCP IPv4. El cliente **no hace `bind()`**: el sistema operativo le asigna un puerto libre automáticamente (*puerto efímero*, por ejemplo 57492).

```python
17     try:
19         cliente.connect((host, PUERTO_TCP))
```
- **L19**: **`connect()`** inicia el **handshake de 3 vías** con el servidor. Si sale bien, la conexión queda establecida y el servidor sale de su `accept()`.

```python
20     except ConnectionRefusedError:
21         print(f"[TCP] No se pudo conectar: el servidor {host}:{PUERTO_TCP} "
22               "no está disponible (conexión rechazada).")
23         cliente.close()
24         return
```
- **L20–24**: **pregunta e.** Si en esa IP no hay nadie escuchando en el puerto 5000, el sistema operativo del servidor responde con un segmento **RST** y Python lanza `ConnectionRefusedError`. Se muestra un mensaje claro y se termina.

```python
25     except (TimeoutError, OSError) as e:
26         print(f"[TCP] No se pudo conectar con {host}:{PUERTO_TCP}: {e}")
27         cliente.close()
28         return
```
- **L25–28**: otros errores de conexión. Por ejemplo:
  - la IP no existe o está apagada: el SYN no recibe respuesta y se agota el tiempo (*timeout*);
  - un firewall bloquea la conexión.

```python
30     print(f"[TCP] Conectado a {host}:{PUERTO_TCP}")
32     with cliente:
```
- **L32**: `with` asegura que el socket se cierre al final (envía FIN).

```python
34         clave = input("Ingrese la clave: ")
35         cliente.sendall(clave.encode(CODIFICACION))
36         respuesta = cliente.recv(TAM_BUFFER).decode(CODIFICACION)
```
- **L34**: pide la clave al usuario.
- **L35**: la envía, convertida en bytes. **No lleva dirección**: el socket ya está conectado, el destino es implícito.
- **L36**: espera la respuesta del servidor, `OK` o `ERROR`.

```python
37         if respuesta != RESP_OK:
38             print("[TCP] Clave incorrecta. Acceso denegado.")
39             return
40         print("[TCP] Clave correcta. Escriba un texto ('salir' para terminar).")
```
- **L37–39**: si no es `OK`, termina. El `return` dentro del `with` igual cierra el socket.

```python
43         while True:
44             texto = input("> ")
45             if not texto.strip():
46                 continue
```
- **L43–44**: bucle para enviar varios textos. `input("> ")` espera que el usuario escriba.
- **L45–46**: si escribió algo vacío o solo espacios, no lo envía (`continue` vuelve al inicio del bucle).

```python
48             cliente.sendall(texto.encode(CODIFICACION))
49             if texto.strip().lower() == CMD_SALIR:
50                 break
```
- **L48**: envía el texto.
- **L49–50**: si era `salir`, ya se le avisó al servidor; se sale del bucle sin esperar respuesta.

```python
51             datos = cliente.recv(TAM_BUFFER)
52             if not datos:
53                 print("[TCP] El servidor cerró la conexión.")
54                 break
55             print("Servidor:", datos.decode(CODIFICACION))
```
- **L51**: espera el texto convertido.
- **L52–54**: si llegan bytes vacíos, el servidor cerró la conexión (por ejemplo, porque lo detuvieron).
- **L55**: muestra la respuesta, ya en formato Frase.

```python
57     print("[TCP] Conexión cerrada.")
```
- **L57**: al salir del `with`, el socket ya se cerró.

---

## 4. `servidor_udp.py`

```python
16     servidor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
```
- **L16**: crea un socket **UDP** (`SOCK_DGRAM`).

```python
17     servidor.bind((HOST_ESCUCHA, PUERTO_UDP))  # en UDP no hay listen() ni accept()
```
- **L17**: **`bind()`** al puerto 5001, igual que en TCP. La diferencia: **no hay `listen()` ni `accept()`**, porque en UDP **no existen las conexiones**. El servidor directamente queda listo para recibir datagramas de cualquiera.

```python
20     autenticados = set()  # direcciones (ip, puerto) que ya enviaron la clave
```
- **L20**: un **conjunto** (`set`) vacío donde se guardan las direcciones de los clientes que ya pusieron la clave correcta.
  - **¿Por qué hace falta?** En TCP, cada cliente tiene su propio socket de conexión, así que "el que pasó la clave" es ese socket.
  - En UDP todos los mensajes llegan **al mismo socket**, mezclados. La única forma de saber quién es quién es mirar la dirección `(ip, puerto)` de origen de cada datagrama.

```python
22     try:
23         while True:
24             try:
26                 datos, direccion = servidor.recvfrom(TAM_BUFFER)
```
- **L26**: **`recvfrom()`** espera un datagrama y devuelve **dos cosas**:
  - los datos;
  - la **dirección de quien lo mandó**.

  Esa dirección es la que se usa para responder. Es la gran diferencia con `recv()`.

```python
27             except ConnectionResetError:
30                 continue
```
- **L27–30**: particularidad de **Windows**. Si el servidor le respondió a un cliente que ya cerró, llega un mensaje ICMP "port unreachable". Windows lo informa como error en el siguiente `recvfrom()`. Se ignora y se sigue escuchando; si no, el servidor se cerraría.

```python
32             texto = datos.decode(CODIFICACION).strip()
```
- **L32**: bytes → texto, sin espacios en los extremos.

```python
34             if direccion not in autenticados:
36                 if texto == CLAVE:
37                     autenticados.add(direccion)
38                     print(f"[UDP] {direccion} -> clave correcta.")
39                     servidor.sendto(RESP_OK.encode(CODIFICACION), direccion)
40                 else:
41                     print(f"[UDP] {direccion} -> clave incorrecta. No se procesa.")
42                     servidor.sendto(RESP_ERROR.encode(CODIFICACION), direccion)
43                 continue
```
- **L34**: si esta dirección **todavía no está autenticada**, el datagrama se interpreta como un intento de clave.
- **L36–39**: clave correcta. Se agrega la dirección al conjunto y se responde `OK` con **`sendto()`**, indicando a quién.
- **L40–42**: clave incorrecta. Se responde `ERROR` y **no se procesa** el texto.
- **L43**: `continue` vuelve a esperar el próximo datagrama.

```python
45             if texto.lower() == CMD_SALIR:
46                 autenticados.discard(direccion)
47                 print(f"[UDP] {direccion} pidió salir.")
48                 continue
```
- **L45–48**: si un cliente autenticado manda `salir`, se lo borra del conjunto. Si vuelve a escribir, tendrá que poner la clave otra vez.

```python
50             respuesta = formato_frase(texto)
51             print(f"[UDP] {direccion} recibido: {texto!r} -> enviado: {respuesta!r}")
53             servidor.sendto(respuesta.encode(CODIFICACION), direccion)
```
- **L50**: transforma el texto.
- **L53**: lo devuelve con **`sendto()`**: en UDP **cada envío lleva la dirección de destino**, porque el socket no está conectado a nadie.

```python
54     except KeyboardInterrupt:
55         print("\n[UDP] Servidor detenido.")
56     finally:
57         servidor.close()
```
- **L54–57**: igual que en TCP: `Ctrl+C` detiene el servidor y se libera el puerto.

> **Importante para explicar:** el servidor UDP **atiende a varios clientes a la vez**, porque cada datagrama se procesa por separado y no hay conexiones que lo "ocupen".

---

## 5. `cliente_udp.py`

```python
11 TIEMPO_ESPERA = 3  # segundos que se espera una respuesta antes de rendirse
```
- **L11**: cuántos segundos espera el cliente una respuesta. En UDP es **indispensable**: si el datagrama se pierde o el servidor no existe, nadie avisa, y sin límite el cliente esperaría para siempre.

### Función `enviar_y_esperar` (L14–28)

```python
14 def enviar_y_esperar(cliente, servidor, mensaje):
17     cliente.sendto(mensaje.encode(CODIFICACION), servidor)
```
- **L14**: función auxiliar que envía un mensaje y espera la respuesta. Se usa tanto para la clave como para los textos.
- **L17**: **`sendto(datos, (ip, puerto))`** envía un datagrama al servidor:
  - **no** hay handshake;
  - **no** se comprueba que el servidor exista;
  - el datagrama simplemente sale.

```python
18     try:
19         datos, _ = cliente.recvfrom(TAM_BUFFER)
20         return datos.decode(CODIFICACION)
```
- **L19**: espera la respuesta. `recvfrom()` devuelve `(datos, dirección)`. La dirección no se necesita, así que se descarta con `_` (convención de Python para "no me importa este valor").
- **L20**: devuelve el texto recibido.

```python
21     except socket.timeout:
22         print(f"[UDP] Sin respuesta después de {TIEMPO_ESPERA} s: "
23               "el servidor no está disponible o el datagrama se perdió.")
```
- **L21–23**: **pregunta f.** Pasaron 3 segundos sin respuesta. UDP no puede distinguir entre "el servidor no existe" y "el paquete se perdió".

```python
24     except ConnectionResetError:
26         print("[UDP] El host respondió que no hay ningún servidor en ese puerto "
27               "(ICMP port unreachable).")
28     return None
```
- **L24–27**: **pregunta f, otro caso.** La PC destino existe pero no tiene nada escuchando en el puerto 5001. Su sistema operativo responde con un **ICMP "port unreachable"** y Windows lo muestra como `ConnectionResetError`. Ocurre sobre todo al probar en la misma PC.
- **L28**: si hubo cualquiera de los dos errores, devuelve `None` (sin respuesta).

### Función `main` (L31–63)

```python
32     host = sys.argv[1] if len(sys.argv) > 1 else HOST_SERVIDOR
33     servidor = (host, PUERTO_UDP)
```
- **L32**: igual que en el cliente TCP: IP por argumento o `127.0.0.1`.
- **L33**: guarda la dirección del servidor como tupla, para pasarla en cada `sendto()`.

```python
36     cliente = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
37     cliente.settimeout(TIEMPO_ESPERA)
```
- **L36**: socket UDP. **No hay `connect()`**.
- **L37**: `settimeout(3)` hace que `recvfrom()` lance `socket.timeout` si en 3 segundos no llega nada.

```python
39     with cliente:
41         clave = input("Ingrese la clave: ")
42         respuesta = enviar_y_esperar(cliente, servidor, clave)
43         if respuesta is None:
44             return
45         if respuesta != RESP_OK:
46             print("[UDP] Clave incorrecta. Acceso denegado.")
47             return
48         print("[UDP] Clave correcta. Escriba un texto ('salir' para terminar).")
```
- **L41–42**: pide la clave y la envía. Fijate que **primero se escribe la clave y recién después se descubre si el servidor existe**. En TCP, en cambio, `connect()` falla antes de pedir nada.
- **L43–44**: si no hubo respuesta (servidor caído), termina.
- **L45–47**: si la respuesta no es `OK`, la clave era incorrecta.

```python
51         while True:
52             texto = input("> ")
53             if not texto.strip():
54                 continue
55             if texto.strip().lower() == CMD_SALIR:
56                 cliente.sendto(texto.encode(CODIFICACION), servidor)
57                 break
```
- **L51–54**: bucle de textos; ignora líneas vacías.
- **L55–57**: con `salir`, le avisa al servidor (para que lo saque de `autenticados`) y termina. No espera respuesta porque el servidor no contesta a `salir`.

```python
58             respuesta = enviar_y_esperar(cliente, servidor, texto)
59             if respuesta is None:
60                 break
61             print("Servidor:", respuesta)
```
- **L58**: envía el texto y espera la respuesta.
- **L59–60**: si el servidor dejó de responder en medio de la sesión, termina.
- **L61**: muestra el texto en formato Frase.

```python
63     print("[UDP] Cliente terminado.")
```
- **L63**: fin. No dice "conexión cerrada" porque en UDP **nunca hubo conexión**.

---

## 6. Comparación TCP vs UDP en nuestro código

| Paso | TCP | UDP |
|---|---|---|
| Crear socket | `socket(AF_INET, SOCK_STREAM)` | `socket(AF_INET, SOCK_DGRAM)` |
| Servidor: asociar puerto | `bind()` | `bind()` |
| Servidor: esperar clientes | `listen()` + `accept()` | — (no hay conexiones) |
| Cliente: iniciar | `connect()`, con handshake | — (directamente `sendto()`) |
| Enviar | `sendall(datos)`, sin dirección | `sendto(datos, dirección)` |
| Recibir | `recv()`, solo datos | `recvfrom()`, datos + dirección |
| ¿Cómo sabe el servidor quién pasó la clave? | Cada cliente tiene su propio socket de conexión | Conjunto `autenticados` con las direcciones `(ip, puerto)` |
| Servidor caído | `connect()` falla al instante (`ConnectionRefusedError`) | `sendto()` no falla; se detecta por timeout o ICMP |
| ¿Necesita timeout el cliente? | No: TCP detecta solo los problemas | Sí: `settimeout(3)` |
| Fin | `close()` envía FIN | `close()` solo libera el socket local |
| Clientes simultáneos | Uno por vez (los demás en cola) | Varios a la vez |

---

## 7. Preguntas que nos pueden hacer

- **¿Por qué `sendall()` y no `send()`?**
  - `send()` puede enviar solo una parte de los datos y devuelve cuántos bytes mandó.
  - `sendall()` repite el envío hasta mandar todo.
- **¿Por qué `encode()` y `decode()`?** Los sockets transmiten **bytes**, no texto. UTF-8 define cómo se convierten las letras, con tildes incluidas, en bytes.
- **¿Qué pasa si el texto tiene más de 1024 bytes?** `recv(1024)` leería solo una parte. Para este ejercicio alcanza; para textos largos habría que leer en un bucle o aumentar `TAM_BUFFER`.
- **¿La clave viaja segura?** No: viaja **en texto plano** y cualquiera que capture el tráfico (por ejemplo con Wireshark) la puede leer. En un sistema real se usaría TLS (cifrado).
- **¿Por qué el cliente no hace `bind()`?** No lo necesita: el sistema operativo le asigna un puerto efímero libre. El servidor sí, porque los clientes tienen que saber a qué puerto ir.
- **¿Cómo haría el servidor TCP para atender a varios a la vez?** Usando hilos (`threading`): un hilo por cada conexión que devuelve `accept()`.
- **¿Qué es `if __name__ == "__main__"`?** Hace que `main()` se ejecute solo cuando el archivo se ejecuta directamente, y no cuando otro archivo lo importa.
