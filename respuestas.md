# Ejercicio 7 – Respuestas teóricas

## a. ¿Cómo se establece la comunicación en TCP?

Mediante el **saludo de tres vías (three-way handshake)**:

1. **SYN**: el cliente pide conectarse y envía su número de secuencia inicial.
2. **SYN + ACK**: el servidor acepta, envía su número de secuencia y confirma el del cliente.
3. **ACK**: el cliente confirma. La conexión queda establecida.

En el código: el servidor hace `bind()` y `listen()`; el cliente llama a `connect()`, que inicia el handshake; el servidor obtiene la conexión con `accept()`. Se cierra con **FIN / ACK**.

## b. ¿Qué diferencia existe entre connect() y sendto()?

- **`connect()`** (TCP): establece una conexión (handshake) **antes** de enviar datos. Después se usa `send()`/`recv()` sin indicar el destino. Si el servidor no está, falla al instante.
- **`sendto()`** (UDP): envía un datagrama **directamente**, sin conexión, indicando la dirección `(ip, puerto)` **en cada envío**. No falla aunque no haya nadie escuchando.

## c. ¿Qué función cumplen bind(), listen() y accept()?

- **`bind()`**: asocia el socket a una IP y un **puerto** (5000 TCP / 5001 UDP), para que los clientes sepan dónde encontrar al servidor.
- **`listen()`**: (TCP) pone el socket en **modo escucha** y define la cola de conexiones pendientes.
- **`accept()`**: (TCP) espera una conexión y devuelve un **socket nuevo** para ese cliente. El original sigue escuchando.

## d. ¿Qué diferencia existe entre recv()/send() y recvfrom()/sendto()?

- **`send()` / `recv()`**: para sockets **conectados** (TCP). No llevan dirección porque el socket ya sabe con quién habla.
- **`sendto()` / `recvfrom()`**: para sockets **sin conexión** (UDP). `sendto()` indica el destino y `recvfrom()` devuelve los datos **y la dirección del emisor**. Así el servidor UDP sabe a quién responder.

## e. ¿Qué ocurre si el servidor TCP no está disponible?

- Si la PC existe pero nadie escucha en el puerto, responde con **RST** y `connect()` falla al instante (`ConnectionRefusedError`).
- Si la PC no existe o está apagada, el SYN no tiene respuesta y `connect()` falla por **timeout**.
- En ambos casos **no se envía ningún dato**.

## f. ¿Qué ocurre si el servidor UDP no está disponible?

- `sendto()` **no da error**: el datagrama se envía igual y **se pierde**.
- El cliente solo lo nota porque **no llega respuesta**. Por eso usa un **timeout** (`settimeout(3)`); sin él quedaría esperando para siempre.
- Si la PC existe, puede devolver un **ICMP "Port Unreachable"**. En Windows aparece como `ConnectionResetError`.

## g. ¿Qué características de confiabilidad ofrece TCP que UDP no ofrece?

| Característica | TCP | UDP |
|---|---|---|
| Conexión previa (handshake) | ✔ | ✘ |
| Confirmación de recepción (ACK) | ✔ | ✘ |
| Retransmisión de lo perdido | ✔ | ✘ |
| Entrega en orden | ✔ | ✘ |
| Descarte de duplicados | ✔ | ✘ |
| Control de flujo y de congestión | ✔ | ✘ |

A cambio, UDP es más liviano (encabezado de 8 bytes contra 20 de TCP) y más rápido. Por eso se usa en DNS, streaming, VoIP y juegos.

## h. ¿Por qué TCP se considera orientado a conexión y UDP no?

- **TCP** establece una conexión antes de enviar datos (handshake). Mientras dura, ambos extremos **mantienen un estado**: números de secuencia, datos confirmados y pendientes. Al final la **cierran** con FIN.
- **UDP** no establece ni cierra nada y no guarda estado: **cada datagrama es independiente** y lleva su dirección de destino.

En el código: en TCP cada cliente tiene su propio socket (`accept()`). En UDP un solo socket recibe a todos, por eso el servidor guarda a mano quién puso la clave (conjunto `autenticados`).

## i. ¿Qué información adicional puede observarse en una captura de Wireshark?

Wireshark muestra **todas las capas** de cada paquete real:

- **Enlace / red:** direcciones **MAC**, **IP**, TTL y los mensajes **ARP**.
- **TCP:**
  - **puertos**, incluido el efímero del cliente;
  - **handshake** (SYN, SYN+ACK, ACK), **FIN** o **RST**;
  - **números de secuencia y ACK**, **flags** y **ventana**;
  - retransmisiones y tiempos de ida y vuelta.
- **UDP:** solo puertos, longitud y checksum. Si el servidor está apagado, se ve el **ICMP "Port Unreachable"**.
- **Datos:** el texto enviado y **la clave en texto plano**. Esto demuestra que la autenticación no es segura sin cifrado (TLS).

Filtros útiles: `tcp.port == 5000` y `udp.port == 5001`. Para capturar en una sola PC (`127.0.0.1`) se usa la interfaz de **loopback** de Npcap.
