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

## h. ¿Por qué TCP se considera orientado a conexión y UDP no?

**TCP es orientado a conexión** porque, antes de intercambiar datos, los dos extremos **establecen una conexión** y mantienen un **estado compartido** mientras dura:

1. **Establecimiento:** el handshake de 3 vías (SYN, SYN+ACK, ACK). En él se acuerdan los números de secuencia iniciales, el tamaño de ventana y opciones como el MSS.
2. **Mantenimiento del estado:** cada extremo recuerda en qué número de secuencia va, qué datos fueron confirmados (ACK) y cuáles hay que retransmitir. La conexión pasa por estados: `LISTEN`, `SYN-SENT`, `ESTABLISHED`, `FIN-WAIT`, `TIME-WAIT`, etc.
3. **Cierre ordenado:** se libera con un intercambio de FIN/ACK en cada sentido.
4. **Identificación:** una conexión se identifica por la cuádrupla **IP origen, puerto origen, IP destino, puerto destino**. Todos los segmentos de esa conexión pertenecen al mismo "canal" lógico, un flujo de bytes punto a punto.

**UDP no es orientado a conexión** porque:
- no hay handshake ni cierre;
- el emisor no guarda ningún estado sobre el receptor;
- cada **datagrama es independiente** y lleva la dirección de destino;
- el receptor no sabe si vendrán más datagramas ni de quién.

Por eso se dice que UDP ofrece un servicio de *"mejor esfuerzo"*: envía y se olvida.

**Cómo se ve en nuestro código:**

| | TCP | UDP |
|---|---|---|
| Establecer | `connect()` en el cliente, `listen()` + `accept()` en el servidor | No existe: directamente `sendto()` |
| Un socket por cliente | Sí: `accept()` crea uno nuevo para cada conexión | No: un único socket recibe datagramas de todos |
| Enviar y recibir | `send()` / `recv()`, sin dirección porque el socket ya está "atado" al otro extremo | `sendto()` / `recvfrom()`, con la dirección en cada datagrama |
| Saber quién puso la clave | Implícito: es esa conexión | Hay que recordarlo a mano: el conjunto `autenticados` con `(ip, puerto)` |
| Saber que el otro se fue | `recv()` devuelve `b""` (llegó un FIN) | Imposible: solo se nota porque no llegan más datos |

## i. ¿Qué información adicional puede observarse en una captura de Wireshark?

Wireshark captura los paquetes reales que pasan por una interfaz de red y muestra **todas las capas** de cada uno. Además de lo que muestra el programa (el texto enviado y recibido), se puede observar:

**Capa de enlace (Ethernet)**
- Direcciones **MAC** de origen y destino.
- Los mensajes **ARP** previos, para averiguar la MAC a partir de la IP.

**Capa de red (IP)**
- IP de origen y destino.
- **TTL** (tiempo de vida).
- Identificación, flags de fragmentación, longitud total y checksum del encabezado.

**Capa de transporte – TCP**
- **Puertos** de origen y destino. Se ve el **puerto efímero** que el sistema operativo le asignó al cliente.
- El **handshake de 3 vías** (SYN, SYN+ACK, ACK) y el **cierre** (FIN/ACK), o un **RST** cuando la conexión es rechazada (pregunta e).
- **Números de secuencia y de ACK**: cómo cada byte enviado es confirmado.
- **Flags** (SYN, ACK, FIN, RST, PSH).
- **Tamaño de ventana**, usado para el control de flujo.
- **Opciones** negociadas en el handshake: MSS, *window scale*, SACK.
- Análisis automático: **retransmisiones**, ACK duplicados, segmentos fuera de orden y **RTT** (tiempo de ida y vuelta).

**Capa de transporte – UDP**
- Solo **puertos, longitud y checksum**: se ve lo simple que es el encabezado (8 bytes) comparado con TCP.
- Cuando el servidor UDP está apagado, el mensaje **ICMP "Destination unreachable (Port unreachable)"** que devuelve el sistema operativo (pregunta f).

**Capa de aplicación (los datos)**
- El contenido del mensaje: el texto y **la clave `redes2026` en texto plano**. Esto demuestra que nuestra autenticación **no es segura**: cualquiera que capture el tráfico puede leer la clave. Para protegerla habría que cifrar la comunicación, por ejemplo con TLS.

**Tiempos y estadísticas**
- Marca de tiempo de cada paquete: cuánto tarda el servidor en responder.
- Cantidad de paquetes y bytes. Por ejemplo, para enviar una sola frase, TCP necesita varios segmentos más (handshake, ACKs, cierre) que UDP.
- Herramientas como *Follow TCP Stream* (reconstruye toda la conversación) y *Statistics → Flow Graph* (diagrama de la secuencia de paquetes).

**Cómo capturar nuestra aplicación**
- **En una sola PC (`127.0.0.1`):** el tráfico no pasa por la placa de red. Hay que capturar en la interfaz **"Adapter for loopback traffic capture"**, que se instala con Npcap junto con Wireshark.
- **Entre dos PCs:** se captura en la interfaz **Wi-Fi** o **Ethernet**.
- Filtros útiles:
  - `tcp.port == 5000`: nuestra app TCP.
  - `udp.port == 5001`: nuestra app UDP.
  - `tcp.flags.syn == 1`: solo los segmentos del handshake.
  - `icmp`: para ver el "port unreachable" de UDP.

**Comparación con Packet Tracer:** Packet Tracer **simula** los paquetes y muestra sus campos en *PDU Details*. Wireshark muestra el **tráfico real**, con valores reales: tiempos, números de secuencia, retransmisiones y las opciones que negocia el sistema operativo.
