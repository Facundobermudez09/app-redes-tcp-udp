# Guía para armar el archivo de Cisco Packet Tracer

Packet Tracer **no puede ejecutar** el módulo `socket` estándar de Python: su intérprete da `NotImplementedError: socket is not yet implemented`. Por eso:

- El **código** (`servidor_tcp.py`, `cliente_tcp.py`, etc.) se ejecuta en la PC real.
- En **Packet Tracer** se arma la misma red y se muestra en modo **Simulación** cómo viajan los segmentos TCP y los datagramas UDP.
  - Se usan servicios del servidor de PT: **HTTP**, que va sobre TCP, y **DNS**, que va sobre UDP.
  - Representan el mismo comportamiento de transporte que nuestras aplicaciones en los puertos 5000 (TCP) y 5001 (UDP).

Guardá el archivo como `ejercicio7_tcp_udp.pkt`.

---

## 1. Topología

```
 [PC-Cliente] ---- [Switch 2960] ---- [Servidor]
 192.168.1.20                          192.168.1.10
```

Dispositivos (barra inferior de PT):
- **End Devices** → 1 **PC** (renombrarla `PC-Cliente`) y 1 **Server** (renombrarlo `Servidor`).
- **Network Devices → Switches** → 1 **2960**.
- **Connections** → cable **Copper Straight-Through** (línea negra continua):
  - PC-Cliente `FastEthernet0` → Switch `Fa0/1`
  - Servidor `FastEthernet0` → Switch `Fa0/2`

Esperá a que las luces de los enlaces se pongan en verde.

## 2. Direccionamiento

| Dispositivo | IP | Máscara | Gateway | DNS |
|---|---|---|---|---|
| Servidor | 192.168.1.10 | 255.255.255.0 | — | — |
| PC-Cliente | 192.168.1.20 | 255.255.255.0 | — | 192.168.1.10 |

Cómo configurarlo:
- En cada equipo: clic → pestaña **Desktop** → **IP Configuration** → **Static**.
- En la PC-Cliente completá también **DNS Server = 192.168.1.10**.

Estas IP coinciden con las que usarías si ejecutaras el código en dos PCs reales:

```
En el servidor (192.168.1.10):   py servidor_tcp.py
En el cliente  (192.168.1.20):   py cliente_tcp.py 192.168.1.10
```

## 3. Servicios del servidor

En el Servidor, pestaña **Services**:
- **HTTP**: dejarlo en **On**. Viene activado y usa TCP, puerto 80.
- **DNS**: ponerlo en **On** y agregar un registro:
  - Name: `redes.local`
  - Type: `A Record`
  - Address: `192.168.1.10`
  - Clic en **Add**.
  - DNS usa UDP, puerto 53.

Opcional, para que la página muestre algo propio: en **HTTP → index.html → Edit**, cambiar el texto. Por ejemplo: `Ejercicio 7 - Programación De Redes Con Python`.

**Prueba de conectividad (modo Realtime):** PC-Cliente → Desktop → **Command Prompt** → `ping 192.168.1.10`. Tiene que responder.

## 4. Demostración en modo Simulación

1. Abajo a la derecha, pasá de **Realtime** a **Simulation** (o `Shift+S`).
2. En el panel *Simulation*: **Edit Filters**. Dejá marcados solo **TCP**, **UDP**, **DNS**, **HTTP** e **ICMP**. Así no se mezcla tráfico como STP o CDP.
3. En la PC-Cliente: **Desktop → Web Browser** → escribí `http://redes.local` → **Go**.
4. Avanzá paso a paso con **Capture / Forward** (o **Play**). En la lista de eventos vas a ver este orden:

| # | Qué se ve | Protocolo de transporte | Pregunta |
|---|---|---|---|
| 1 | Consulta DNS de la PC al servidor (`redes.local`?) | **UDP** puerto 53: se envía directamente, **sin handshake** | b, d, g |
| 2 | Respuesta DNS (192.168.1.10) | **UDP** | d |
| 3 | **SYN** de la PC al servidor, puerto 80 | **TCP** | a |
| 4 | **SYN + ACK** del servidor a la PC | **TCP** | a |
| 5 | **ACK** de la PC al servidor: conexión establecida | **TCP** | a |
| 6 | HTTP GET y la respuesta con la página, con sus ACK | **TCP** | g |
| 7 | **FIN / ACK**: cierre de la conexión | **TCP** | a |

5. Hacé clic en el sobre de cada evento y mirá la pestaña **Inbound/Outbound PDU Details**.
   - En los segmentos **TCP** aparecen:
     - **SOURCE PORT / DESTINATION PORT**
     - **SEQUENCE NUMBER / ACKNOWLEDGEMENT NUMBER**
     - **FLAGS**, que indican SYN, ACK o FIN
     - **WINDOW**, usada para el control de flujo
   - En los datagramas **UDP** solo hay puertos, longitud y checksum. **No hay** números de secuencia, ACK ni ventana. Esto sirve como evidencia para la pregunta **g**.

## 5. Servidor no disponible (preguntas e y f)

Volvé a Simulation, borrá los eventos (**Reset Simulation**) y probá:

- **TCP no disponible:** en el Servidor → Services → **HTTP: Off**.
  - Desde el navegador, abrí `http://192.168.1.10`. Usá la IP para no depender del DNS.
  - Observá el SYN y qué vuelve del servidor. El navegador muestra un error de conexión o *Request Timeout*.
  - Compará con nuestro `cliente_tcp.py`, que da *"conexión rechazada"* al instante.
- **UDP no disponible:** volvé a poner **HTTP: On** y poné **DNS: Off**.
  - Abrí `http://redes.local`. La consulta DNS (UDP) sale igual: UDP no verifica que haya alguien escuchando.
  - No recibe respuesta y el navegador termina mostrando *Host Name Unresolved*.
  - Es lo mismo que hace nuestro `cliente_udp.py`, que tiene que esperar un timeout.
- **Servidor apagado (opcional):** Servidor → pestaña **Physical** → botón de encendido.
  - Ahora ni siquiera se resuelve ARP: no hay quien responda, ni en TCP ni en UDP.

Anotá en el informe lo que muestra PT en cada caso. Algunas versiones de Packet Tracer muestran los mensajes de error con distinto texto.

## 6. Capturas sugeridas para el informe

1. Topología completa con las IP visibles. Usá *Place Note* (tecla `N`) para anotarlas sobre el dibujo.
2. Lista de eventos de la simulación con DNS (UDP) y SYN / SYN+ACK / ACK (TCP).
3. Detalle de un PDU **TCP** con los flags SYN y ACK y los números de secuencia.
4. Detalle de un PDU **UDP**, mostrando que no tiene esos campos.
5. Los casos de servidor no disponible.
6. Junto a las de PT, capturas de las terminales ejecutando el código en la PC: servidor y cliente TCP y UDP, con clave correcta e incorrecta.

## 7. Extensión opcional: dos redes con un router

Si el profe pide algo más completo, agregá un **Router 1941** entre dos switches:

| Dispositivo | Interfaz | IP | Máscara |
|---|---|---|---|
| Router | G0/0 (red cliente) | 192.168.1.1 | 255.255.255.0 |
| Router | G0/1 (red servidor) | 192.168.2.1 | 255.255.255.0 |
| PC-Cliente | Fa0 | 192.168.1.20 (gateway 192.168.1.1) | 255.255.255.0 |
| Servidor | Fa0 | 192.168.2.10 (gateway 192.168.2.1) | 255.255.255.0 |

En el router (CLI):

```
enable
configure terminal
interface g0/0
 ip address 192.168.1.1 255.255.255.0
 no shutdown
interface g0/1
 ip address 192.168.2.1 255.255.255.0
 no shutdown
end
```

Acordate de actualizar el DNS de la PC y el registro DNS a 192.168.2.10.

## 8. Subir el `.pkt` al repositorio

Cuando el archivo esté armado, guardalo como `ejercicio7_tcp_udp.pkt` y subilo de una de estas dos formas:

- **Desde la web de GitHub:** en el repositorio, **Add file → Upload files**. Arrastrá el `.pkt` y hacé clic en **Commit changes**.
- **Con Git**, desde la carpeta del proyecto:

  ```
  git add ejercicio7_tcp_udp.pkt
  git commit -m "Agregar archivo de Packet Tracer"
  git push
  ```

Tus compañeros lo abren con Cisco Packet Tracer (*File → Open*). Conviene que todos usen la misma versión de PT o una más nueva: un `.pkt` guardado en una versión nueva puede no abrir en una más vieja.
