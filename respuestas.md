# Ejercicio 7 – Respuestas teóricas

## a. ¿Cómo se establece la comunicación en TCP?

TCP está **orientado a conexión**: antes de enviar datos, cliente y servidor establecen una conexión mediante el **saludo de tres vías (three-way handshake)**:

1. **SYN**: el cliente envía un segmento con el flag SYN y su número de secuencia inicial (ISN).
2. **SYN + ACK**: el servidor responde con SYN (su propio ISN) y ACK (confirma el ISN del cliente + 1).
3. **ACK**: el cliente confirma el ISN del servidor + 1. La conexión queda **ESTABLISHED**.

En el código esto ocurre así:
- El servidor hace `bind()` → `listen()` y queda esperando en `accept()`.
- El cliente llama a `connect()`, que es lo que dispara el handshake.
- Cuando el handshake termina, `accept()` devuelve un socket nuevo para ese cliente.

La conexión se cierra con un intercambio de **FIN / ACK** en ambos sentidos (`close()`).

En Packet Tracer se ve en modo Simulación al abrir una página web desde el cliente: aparecen los segmentos SYN, SYN+ACK y ACK antes del HTTP (ver `guia_packet_tracer.md`).

## b. ¿Qué diferencia existe entre connect() y sendto()?

| `connect()` (TCP) | `sendto()` (UDP) |
|---|---|
| Establece una conexión con el servidor (handshake de 3 vías) **antes** de enviar datos. | No establece conexión: envía **directamente** un datagrama. |
| Se llama una sola vez; después se usa `send()`/`recv()` sin indicar destino. | Hay que indicar la dirección `(ip, puerto)` del destino **en cada envío**. |
| Si el servidor no está, falla de inmediato (`ConnectionRefusedError`). | No falla aunque no haya nadie escuchando: el datagrama sale igual. |

En UDP también se puede llamar a `connect()`, pero no hay handshake. Solo fija un destino por defecto en el socket.

## c. ¿Qué función cumplen bind(), listen() y accept()?

- **`bind((ip, puerto))`**: asocia el socket a una dirección IP y un puerto local. Así el servidor queda en un puerto conocido (5000 en TCP, 5001 en UDP) al que los clientes pueden dirigirse. Se usa tanto en TCP como en UDP.
- **`listen(n)`**: (solo TCP) pone el socket en modo **escucha** pasiva. `n` es el tamaño de la cola de conexiones pendientes que todavía no fueron aceptadas.
- **`accept()`**: (solo TCP) bloquea hasta que un cliente completa el handshake.
  - Devuelve un **socket nuevo** dedicado a esa conexión, más la dirección del cliente.
  - El socket original sigue escuchando nuevas conexiones.

## d. ¿Qué diferencia existe entre recv()/send() y recvfrom()/sendto()?

- **`send()` / `recv()`**: se usan en sockets **conectados** (TCP). No llevan dirección, porque el socket ya sabe con quién está conectado.
  - TCP es un **flujo de bytes**: no se respetan los límites de mensaje. Un `recv()` puede traer parte de un envío, o varios juntos.
  - `recv()` devuelve `b""` cuando el otro extremo cerró la conexión.
- **`sendto(datos, dirección)` / `recvfrom()`**: se usan en sockets **sin conexión** (UDP).
  - `sendto()` indica el destino en cada envío.
  - `recvfrom()` devuelve los datos **y la dirección de quien los envió**. Por eso el servidor UDP sabe a quién responder.
  - Cada llamada envía o recibe **un datagrama completo**, así que los límites del mensaje se respetan.

## e. ¿Qué ocurre si el servidor TCP no está disponible?

- **El host existe pero no hay ningún programa escuchando en el puerto**: el sistema operativo responde al SYN con un segmento **RST**. `connect()` falla de inmediato con `ConnectionRefusedError`.
  - Nuestro cliente lo captura y muestra: *"el servidor no está disponible (conexión rechazada)"*.
- **El host no existe o está apagado**: el SYN no recibe respuesta. TCP lo retransmite varias veces y finalmente `connect()` falla por **timeout**.
- En ningún caso se envían datos: sin conexión establecida, TCP no transmite nada.

## f. ¿Qué ocurre si el servidor UDP no está disponible?

- `sendto()` **no da error**: UDP no verifica que el destino exista, simplemente envía el datagrama. El dato se pierde.
- El cliente no se entera del problema hasta que espera la respuesta con `recvfrom()`. Por eso hay que usar `settimeout()`; sin él, el cliente quedaría bloqueado para siempre.
  - Nuestro cliente espera 3 segundos y muestra *"Sin respuesta…"*.
- Si el host existe pero el puerto está cerrado, puede volver un mensaje **ICMP "Port Unreachable"**. En Windows aparece como `ConnectionResetError` (WinError 10054) en `recvfrom()`.
  - Lo capturamos y mostramos *"no hay ningún servidor en ese puerto"*. Es lo que ocurrió en nuestras pruebas en localhost.
- Es responsabilidad de la **aplicación** detectar y manejar la pérdida (timeouts, reintentos).

## g. ¿Qué características de confiabilidad ofrece TCP que UDP no ofrece?

| Característica | TCP | UDP |
|---|---|---|
| Conexión previa (handshake) | Sí | No |
| Confirmación de recepción (ACK) | Sí | No |
| Retransmisión de segmentos perdidos | Sí | No |
| Entrega en orden (números de secuencia) | Sí | No |
| Detección y descarte de duplicados | Sí | No |
| Control de flujo (ventana deslizante) | Sí | No |
| Control de congestión | Sí | No |
| Detección de errores (checksum) | Sí (obligatorio) | Sí (opcional en IPv4); los datagramas con error se descartan sin aviso |

UDP es más liviano: tiene una cabecera de 8 bytes (TCP tiene 20 como mínimo), no necesita handshake y tiene menor latencia. Por eso conviene en DNS, streaming, VoIP y juegos, donde la velocidad importa más que la entrega perfecta.

Una consecuencia en este TP: con UDP, si se pierde un datagrama, el cliente se queda sin respuesta. Por eso nuestro cliente UDP necesita un **timeout**, mientras que el cliente TCP no.
