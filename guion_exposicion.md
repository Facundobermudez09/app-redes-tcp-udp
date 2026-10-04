# Guion de la exposición – Ejercicio 7

**Duración estimada:** 12–15 minutos más preguntas.

**Roles:** el guion está dividido en 3 partes. Si son más o menos integrantes, repartan las partes como les quede cómodo.

- 🗣️ = lo que se **dice** (no hace falta decirlo de memoria palabra por palabra, pero sí la idea).
- 🖱️ = lo que se **hace** en la compu.

| # | Parte | Quién | Tiempo |
|---|---|---|---|
| 0 | Preparación antes de empezar | Todos | antes |
| 1 | Introducción y consigna | Integrante 1 | 1–2 min |
| 2 | El código: estructura y protocolo | Integrante 1 | 2–3 min |
| 3 | Demo TCP | Integrante 2 | 2–3 min |
| 4 | Demo UDP y comparación | Integrante 2 | 2–3 min |
| 5 | Packet Tracer | Integrante 3 | 3–4 min |
| 6 | Conclusión | Integrante 3 | 1 min |
| 7 | Preguntas | Todos | — |

---

## 0. Preparación (antes de que les toque)

- [ ] Abrir **4 terminales** en la carpeta del proyecto y ubicarlas en pantalla:
  - arriba a la izquierda: servidor TCP;
  - arriba a la derecha: cliente TCP;
  - abajo a la izquierda: servidor UDP;
  - abajo a la derecha: cliente UDP.
- [ ] Probar que `py --version` funcione en la compu que se va a usar.
- [ ] **No** dejar servidores abiertos de antes. Si aparece `WinError 10048`, hay uno abierto: cerrarlo con `Ctrl+C`.
- [ ] Abrir `ejercicio7_tcp_udp.pkt` en Packet Tracer y dejarlo en modo **Realtime**.
- [ ] Hacer un `ping` desde la PC al servidor en Packet Tracer, para que ARP ya esté resuelto y la simulación sea más limpia.
- [ ] Tener abierto un editor con `servidor_tcp.py` y `servidor_udp.py` por si piden ver el código.
- [ ] Agrandar la letra de las terminales (`Ctrl` + rueda del mouse) para que se lea desde lejos.

---

## 1. Introducción y consigna (Integrante 1)

🗣️
> "Buenas. Nosotros hicimos el ejercicio 7: una aplicación cliente/servidor en Python, en dos versiones, una sobre **TCP** y otra sobre **UDP**, usando la **API de sockets**.
>
> El funcionamiento es simple: el cliente le envía un texto al servidor y el servidor se lo devuelve en **formato Frase**, es decir, con la primera letra de cada palabra en mayúscula. Por ejemplo, 'programación de redes con python' vuelve como 'Programación De Redes Con Python'.
>
> Además tiene **acceso con clave**: lo primero que hace el cliente es enviar una clave, y si no coincide, el servidor no procesa nada.
>
> La idea de hacerlo dos veces es poder comparar cómo trabaja cada protocolo de la capa de transporte: TCP, que es orientado a conexión y confiable, y UDP, que no tiene conexión y no garantiza la entrega."

---

## 2. El código: estructura y protocolo (Integrante 1)

🖱️ Mostrar la carpeta o el repositorio con los archivos.

🗣️
> "El proyecto tiene cinco archivos. `comun.py` tiene lo compartido: la clave, los puertos —5000 para TCP y 5001 para UDP— y la función `formato_frase`, que separa el texto en palabras y pone en mayúscula la primera letra de cada una. Después hay un servidor y un cliente para TCP, y un servidor y un cliente para UDP.
>
> Por encima de TCP y UDP definimos **nuestro propio protocolo de aplicación**, que es muy simple:
> 1. El primer mensaje del cliente es la clave.
> 2. El servidor responde `OK` o `ERROR`. Si es `ERROR`, no se ejecuta nada más.
> 3. Si es `OK`, el cliente puede mandar todos los textos que quiera, y cada uno vuelve en formato Frase.
> 4. Con la palabra `salir` se termina."

🖱️ Mostrar `servidor_tcp.py`, función `main()`.

🗣️
> "En el **servidor TCP** se ve la secuencia típica:
> - se crea el socket con `SOCK_STREAM`, que es TCP;
> - `bind` lo asocia al puerto 5000;
> - `listen` lo pone en modo escucha, con una cola de hasta 5 conexiones;
> - `accept` se queda esperando hasta que un cliente completa el handshake, y devuelve un **socket nuevo** dedicado a ese cliente.
>
> El cliente TCP hace `connect`, que es lo que dispara el **handshake de tres vías**: SYN, SYN+ACK y ACK. Después usa `send` y `recv`, que no llevan dirección porque el socket ya está conectado."

🖱️ Mostrar `servidor_udp.py`.

🗣️
> "En **UDP** cambia bastante. El servidor hace `bind` pero **no hay `listen` ni `accept`**, porque no existen las conexiones. Recibe con `recvfrom`, que devuelve el mensaje **y la dirección de quien lo mandó**, y responde con `sendto` a esa dirección.
>
> Como no hay conexión, el servidor no tiene forma de saber 'quién ya puso la clave'. Por eso guardamos en un conjunto llamado `autenticados` las direcciones IP y puerto que enviaron la clave correcta. Si llega un mensaje de una dirección que no está en el conjunto, se interpreta como un intento de clave."

---

## 3. Demo TCP (Integrante 2)

🖱️ Terminal del servidor TCP: `py servidor_tcp.py`

🗣️
> "Primero levantamos el servidor TCP. Queda esperando en el `accept`."

🖱️ Terminal del cliente TCP: `py cliente_tcp.py`. Clave: `redes2026`. Texto: `programación de redes con python`.

🗣️
> "Al ejecutar el cliente, el `connect` establece la conexión, y en el servidor aparece 'Conexión aceptada' con la IP y el puerto del cliente. Ese puerto lo eligió el sistema operativo: el cliente no hace `bind`.
>
> Ponemos la clave correcta, el servidor responde OK, y ahora mandamos el texto… y vuelve en formato Frase. En la terminal del servidor se ve lo que recibió y lo que devolvió."

🖱️ Escribir `salir`. Ejecutar el cliente de nuevo con la clave `1234`.

🗣️
> "Si ponemos una clave incorrecta, el servidor responde ERROR y cierra la conexión sin procesar nada."

🖱️ En la terminal del servidor TCP, `Ctrl+C`. Ejecutar `py cliente_tcp.py` otra vez.

🗣️
> "Ahora apagamos el servidor y probamos conectarnos. **El error aparece al instante, antes de pedir la clave**: 'conexión rechazada'. Cuando llega el SYN a un puerto donde nadie escucha, el sistema operativo responde con un segmento **RST**, y `connect` falla. Esto responde la **pregunta e**."

---

## 4. Demo UDP y comparación (Integrante 2)

🖱️ Terminal del servidor UDP: `py servidor_udp.py`. Terminal del cliente UDP: `py cliente_udp.py`, clave correcta, un texto, `salir`.

🗣️
> "En UDP, desde afuera funciona igual: clave, texto, respuesta. Pero por dentro no hubo ningún handshake: el primer datagrama que salió ya fue la clave."

🖱️ `Ctrl+C` en el servidor UDP. Ejecutar `py cliente_udp.py` y poner la clave.

🗣️
> "Ahora la diferencia importante. Apagamos el servidor UDP y ejecutamos el cliente. **Nos deja escribir la clave y la envía sin ningún error**, porque `sendto` no verifica si hay alguien del otro lado. Recién al esperar la respuesta nos damos cuenta del problema. Por eso el cliente UDP tiene un **timeout de 3 segundos**: sin él quedaría esperando para siempre.
>
> En la misma PC, Windows además recibe un mensaje ICMP 'puerto inalcanzable' y lo informa como error. Entre dos PCs, normalmente lo que se ve es el timeout. Esto responde la **pregunta f**."

> Si la demo se hace entre dos computadoras, en el paso anterior va a aparecer "Sin respuesta después de 3 s" en lugar del mensaje de ICMP. Las dos cosas son correctas.

🗣️ (cierre de la comparación, **pregunta g**)
> "Resumiendo: TCP establece una conexión, confirma cada segmento con ACK, retransmite lo que se pierde, entrega en orden y tiene control de flujo y de congestión. UDP no tiene nada de eso: es más liviano y rápido, pero la aplicación tiene que encargarse de los problemas. Nuestro propio código lo muestra: el cliente TCP no necesita timeout, y el UDP sí."

---

## 5. Packet Tracer (Integrante 3)

🗣️
> "Packet Tracer no puede ejecutar el módulo `socket` estándar de Python. Por eso usamos Packet Tracer para mostrar **qué pasa en la red** con los mismos protocolos de transporte. Usamos dos servicios que funcionan igual que nuestra aplicación: **HTTP, que va sobre TCP, y DNS, que va sobre UDP**."

🖱️ Mostrar la topología.

🗣️
> "La red tiene una PC cliente y un servidor que da servicio **web y DNS**. Están en **dos redes distintas**, cada una con su switch, unidas por un **router**. Así se ve que los segmentos TCP y los datagramas UDP atraviesan el router. El router trabaja en la capa de red, con IP; los puertos y el handshake solo les importan a los extremos."

🖱️ Pasar a **Simulation**. En **Edit Filters** dejar solo DNS, HTTP, TCP y UDP. En la PC: **Desktop → Web Browser** → escribir el nombre DNS del servidor → **Go**. Avanzar con **Capture/Forward**.

🗣️ (mientras avanza)
> "Primero sale la **consulta DNS**: un solo datagrama UDP, sin ningún aviso previo, que va de la PC al servidor pasando por el router. Vuelve la respuesta con la IP. Eso es UDP: mensaje y respuesta, nada más.
>
> Ahora la PC ya sabe la IP y abre la conexión TCP con el servidor web: vemos el **SYN**, el **SYN+ACK** y el **ACK**. Ese es el **handshake de tres vías**, lo mismo que hace nuestro `connect`. Recién después viaja el pedido HTTP con la página."

🖱️ Hacer clic en el sobre de un segmento TCP y abrir **PDU Details**.

🗣️
> "Si abrimos un segmento TCP, vemos los puertos de origen y destino, el **número de secuencia**, el **número de ACK**, los **flags** como SYN o ACK, y la **ventana**, que se usa para el control de flujo."

🖱️ Abrir el detalle de un datagrama UDP (DNS).

🗣️
> "En cambio, el datagrama UDP solo tiene puertos, longitud y checksum. **No tiene secuencia, ni ACK, ni ventana**: por eso UDP no puede garantizar la entrega ni el orden."

🖱️ Opcional: en el servidor, **Services → HTTP → Off** y repetir. Después **DNS → Off** y repetir.

🗣️ (opcional)
> "Si apagamos el servicio web, la conexión TCP no se puede establecer. Si apagamos el DNS, la consulta UDP sale igual pero nunca recibe respuesta, y el navegador no puede resolver el nombre. Es el mismo comportamiento que mostramos con nuestro programa."

---

## 6. Conclusión (Integrante 3)

🗣️
> "Como conclusión: con la misma aplicación pudimos ver en la práctica la diferencia entre los dos protocolos de transporte. Con **TCP**, la API nos obliga a establecer una conexión con `bind`, `listen`, `accept` y `connect`, y a cambio obtenemos confiabilidad: si el servidor no está, lo sabemos al instante. Con **UDP** solo usamos `bind`, `sendto` y `recvfrom`; es más simple y rápido, pero la aplicación tiene que resolver la autenticación por dirección y los timeouts.
>
> El código, las respuestas teóricas y el archivo de Packet Tracer están en nuestro repositorio de GitHub. Muchas gracias, ¿hay preguntas?"

---

## 7. Plan B si algo falla en vivo

| Problema | Qué hacer |
|---|---|
| `WinError 10048` al abrir un servidor | Ya hay otro abierto: cerrar todas las terminales y volver a abrir |
| `'py' no se reconoce` | Probar con `python`; si no, usar la notebook de otro integrante |
| La demo entre dos PCs no conecta | Hacerla en una sola PC con `127.0.0.1`: se explica igual |
| Packet Tracer no muestra el handshake | Hacer **Reset Simulation**, revisar los filtros (TCP activado) y repetir |
| Nervios / se olvidaron qué decir | Tener este guion abierto en el celular; las respuestas están en `respuestas.md` |

## 8. Preguntas probables

Las respuestas están en [`explicacion_codigo.md`](explicacion_codigo.md) (sección 7) y en [`respuestas.md`](respuestas.md).

- ¿Por qué el cliente no hace `bind()`?
- ¿Qué devuelve `accept()` y por qué es un socket nuevo?
- ¿Por qué `sendall` y no `send`?
- ¿Por qué hay que hacer `encode` y `decode`?
- ¿Cómo sabe el servidor UDP quién puso la clave?
- ¿Qué pasa si se conectan dos clientes TCP a la vez? ¿Y en UDP?
- ¿La clave viaja segura?
- ¿Por qué el cliente UDP necesita timeout y el TCP no?
- ¿Qué hace el router con los segmentos TCP? ¿Mira los puertos?
