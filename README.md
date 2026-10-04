# Ejercicio 7 – Cliente/Servidor TCP y UDP con clave (Python)

Trabajo práctico de **Redes**: dos aplicaciones cliente/servidor en Python, una sobre **TCP** y otra sobre **UDP**.

- El servidor recibe un texto del cliente y lo devuelve en **formato Frase** (primera letra de cada palabra en mayúscula):

  ```
  entrada: programación de redes con python
  salida:  Programación De Redes Con Python
  ```

- Antes de procesar cualquier texto, el servidor **pide una clave**. Si no coincide, no ejecuta nada.

| Dato | Valor |
|---|---|
| Clave | `redes2026` (se cambia en `comun.py`) |
| Puerto TCP | `5000` |
| Puerto UDP | `5001` |

## Integrantes

- _Nombre Apellido_
- _Nombre Apellido_
- _Nombre Apellido_

## Contenido del repositorio

| Archivo | Qué es |
|---|---|
| `comun.py` | Configuración compartida (clave, puertos) y la función `formato_frase()` |
| `servidor_tcp.py` / `cliente_tcp.py` | Versión **TCP** |
| `servidor_udp.py` / `cliente_udp.py` | Versión **UDP** |
| [`respuestas.md`](respuestas.md) | Respuestas a las preguntas teóricas a–i |
| [`explicacion_codigo.md`](explicacion_codigo.md) | Explicación del código línea por línea |
| [`guion_exposicion.md`](guion_exposicion.md) | Guion completo de la exposición (qué decir y qué hacer) |
| [`guia_packet_tracer.md`](guia_packet_tracer.md) | Cómo armar y demostrar la red en Cisco Packet Tracer |
| `ejercicio7_tcp_udp.pkt` | Archivo de Packet Tracer (PC, 2 switches, router y servidor web + DNS) |

---

## 1. Descargar el proyecto

**Opción fácil (sin Git):** en la página del repositorio, botón verde **Code → Download ZIP**. Después hay que **descomprimirlo**: clic derecho → *Extraer todo*. No lo ejecutes desde dentro del ZIP.

**Opción con Git:**

```
git clone https://github.com/Facundobermudez09/app-redes-tcp-udp.git
```

Los 5 archivos `.py` tienen que estar **en la misma carpeta**, porque todos usan `comun.py`.

## 2. Instalar Python (una sola vez)

1. Descargá **Python 3** desde <https://www.python.org/downloads/>.
2. En Windows, en la primera pantalla del instalador **marcá "Add python.exe to PATH"** y después *Install Now*.
3. No hace falta instalar nada más (nada de `pip install`): el programa usa solo la biblioteca estándar de Python.

Para saber qué comando usar, abrí una terminal (ver el punto 3) y probá en este orden:

```
py --version
python --version
python3 --version
```

Usá el primero que muestre `Python 3.x.x`. En Mac y Linux casi siempre es `python3`. En esta guía se escribe `py`; reemplazalo por el tuyo.

## 3. Abrir una terminal en la carpeta del proyecto

- **Windows:** abrí la carpeta en el Explorador de archivos.
  - Opción 1: hacé clic en la **barra de direcciones** (donde está la ruta), escribí `cmd` y apretá Enter.
  - Opción 2: clic derecho en un lugar vacío → **Abrir en Terminal**.
- **Mac / Linux:** abrí la Terminal y escribí `cd ` (con espacio). Arrastrá la carpeta a la ventana y apretá Enter.

Para comprobar que estás en el lugar correcto, escribí `dir` (Windows) o `ls` (Mac/Linux). Tienen que aparecer los archivos `.py`.

## 4. Prueba en una sola computadora

Necesitás **dos terminales** abiertas en la carpeta: una para el servidor y otra para el cliente.

### TCP

```
Terminal 1:  py servidor_tcp.py
Terminal 2:  py cliente_tcp.py
```

En la terminal del cliente:

```
[TCP] Conectado a 127.0.0.1:5000
Ingrese la clave: redes2026
[TCP] Clave correcta. Escriba un texto ('salir' para terminar).
> programación de redes con python
Servidor: Programación De Redes Con Python
> salir
[TCP] Conexión cerrada.
```

En la terminal del servidor se ve lo que va pasando:

```
[TCP] Servidor escuchando en el puerto 5000... (Ctrl+C para terminar)
[TCP] Conexión aceptada desde ('127.0.0.1', 57492)
[TCP] ('127.0.0.1', 57492) -> clave correcta.
[TCP] ('127.0.0.1', 57492) recibido: 'programación de redes con python' -> enviado: 'Programación De Redes Con Python'
[TCP] ('127.0.0.1', 57492) pidió salir.
```

### UDP

```
Terminal 1:  py servidor_udp.py
Terminal 2:  py cliente_udp.py
```

Funciona igual que la versión TCP.

**Para terminar:** en el cliente escribí `salir`. Para detener el servidor, `Ctrl+C`.

## 5. Prueba entre dos computadoras

Una notebook hace de **servidor** y otra de **cliente**.

1. **Las dos tienen que estar conectadas a la misma red** (mismo Wi-Fi).
2. **En la notebook servidor, averiguá su IP:**
   - Windows: escribí `ipconfig` y buscá **"Dirección IPv4"** del adaptador Wi-Fi (ej. `192.168.0.15`).
   - Mac: `ipconfig getifaddr en0`
   - Linux: `hostname -I`
3. **Ejecutá el servidor:** `py servidor_tcp.py` o `py servidor_udp.py`.
   - La primera vez, Windows muestra un aviso del **firewall**: hacé clic en **Permitir acceso**.
   - Si aparecen casillas, marcá **también "Redes públicas"**: el Wi-Fi de la facultad suele figurar como pública.
4. **En la notebook cliente, pasale la IP del servidor:**

   ```
   py cliente_tcp.py 192.168.0.15
   py cliente_udp.py 192.168.0.15
   ```

**Si no conecta:** en la notebook servidor abrí PowerShell **como administrador** (clic derecho en Inicio → *Terminal (Administrador)*) y ejecutá:

```
New-NetFirewallRule -DisplayName "TP Redes TCP" -Direction Inbound -Protocol TCP -LocalPort 5000 -Action Allow
New-NetFirewallRule -DisplayName "TP Redes UDP" -Direction Inbound -Protocol UDP -LocalPort 5001 -Action Allow
```

**Plan B (muy recomendable llevarlo preparado):** muchas redes Wi-Fi de facultades no dejan que las computadoras se comuniquen entre sí.
- **Hotspot del celular:** todos se conectan al celular y se repiten los pasos 2 a 4.
- **Zona con cobertura inalámbrica móvil de Windows** en la notebook servidor (*Configuración → Red e Internet*): los demás se conectan a esa red. La IP del servidor suele ser `192.168.137.1`.

`ping` **no sirve** para comprobar la conexión: Windows lo bloquea por defecto aunque el programa sí funcione. Probá directamente con el cliente.

## 6. Cómo funciona

### TCP (orientado a conexión)

```
   CLIENTE                                         SERVIDOR
                                                   socket(SOCK_STREAM)
                                                   bind(("0.0.0.0", 5000))
                                                   listen(5)
                                                   accept()   ... espera
   socket(SOCK_STREAM)
   connect((ip, 5000))  ── SYN ──────────────────►
                        ◄──────────────── SYN+ACK ─
                        ── ACK ──────────────────►  accept() devuelve un socket nuevo
   send("redes2026")    ─────────────────────────►  ¿clave == CLAVE?
                        ◄────────────── "OK" ─────   (si no, "ERROR" y cierra)
   send("hola mundo")   ─────────────────────────►  formato_frase()
                        ◄────── "Hola Mundo" ─────
   send("salir")        ─────────────────────────►  cierra la conexión
   close()              ── FIN / ACK ────────────►
```

### UDP (sin conexión)

```
   CLIENTE                                         SERVIDOR
                                                   socket(SOCK_DGRAM)
                                                   bind(("0.0.0.0", 5001))
                                                   recvfrom()  ... espera
   socket(SOCK_DGRAM)
   (no hay connect ni handshake)
   sendto("redes2026", (ip, 5001)) ──────────────►  dirección no autenticada → es la clave
                        ◄────────────── "OK" ─────   guarda (ip, puerto) en `autenticados`
   sendto("hola mundo") ─────────────────────────►  dirección autenticada → formato_frase()
                        ◄────── "Hola Mundo" ─────   sendto(respuesta, dirección)
   sendto("salir")      ─────────────────────────►  borra la dirección de `autenticados`
```

Como UDP no tiene conexión, el servidor **no sabe** "quién está conectado". Por eso recuerda en un `set` las direcciones `(ip, puerto)` que ya mandaron la clave correcta. En TCP no hace falta: cada conexión es un socket aparte.

### Qué hace cada parte del código

| Archivo | Parte clave | Qué hace |
|---|---|---|
| `comun.py` | `formato_frase(texto)` | Separa en palabras y pone en mayúscula la primera letra de cada una (no usa `str.title()`, que convertiría "don't" en "Don'T") |
| `servidor_tcp.py` | `main()` | `bind` → `listen` → bucle de `accept`, un cliente a la vez |
| `servidor_tcp.py` | `atender_cliente()` | Verifica la clave; si es correcta, repite `recv` → `formato_frase` → `sendall` |
| `servidor_tcp.py` | `recibir()` | Un `recv()` que se "despierta" cada 1 s para que `Ctrl+C` funcione en Windows |
| `cliente_tcp.py` | `main()` | `connect`; si el servidor no está, captura `ConnectionRefusedError` |
| `servidor_udp.py` | `main()` | `bind` → bucle de `recvfrom`; usa el `set` `autenticados` para la clave |
| `cliente_udp.py` | `enviar_y_esperar()` | `sendto` + `recvfrom` con **timeout de 3 s**; si no hay respuesta, avisa que el servidor no está disponible |

Los textos viajan como bytes en **UTF-8** (`.encode()` / `.decode()`), así funcionan las tildes y la ñ.

**Detalle para explicar:** el servidor **TCP atiende a un cliente por vez**. Si se conecta un segundo cliente, queda esperando en la cola de `listen()` hasta que el primero escriba `salir`. El servidor **UDP atiende a varios a la vez**, porque cada datagrama es independiente.

## 7. Guion para la exposición

| Paso | Qué hacer | Qué se explica |
|---|---|---|
| 1 | Ejecutar `servidor_tcp.py` y `cliente_tcp.py`, clave correcta y un texto | Funcionamiento general; preguntas **a** y **c** (handshake, `bind`/`listen`/`accept`) |
| 2 | Cliente TCP con clave incorrecta | El servidor no ejecuta el programa |
| 3 | Lo mismo con `servidor_udp.py` / `cliente_udp.py` | Preguntas **b**, **d** y **h** (`connect` vs `sendto`, `recv` vs `recvfrom`, orientado a conexión) |
| 4 | Cerrar el servidor TCP (`Ctrl+C`) y ejecutar el cliente TCP | Pregunta **e**: rechazo inmediato |
| 5 | Cerrar el servidor UDP y ejecutar el cliente UDP | Pregunta **f**: la clave "se envía" igual; luego error o timeout |
| 6 | Mostrar la simulación en Packet Tracer | Handshake TCP vs UDP sin conexión; pregunta **g** |
| 7 | Mencionar qué mostraría Wireshark (la clave en texto plano) | Pregunta **i** |

En el paso 5, en una sola computadora suele aparecer *"no hay ningún servidor en ese puerto (ICMP port unreachable)"*. Entre dos computadoras suele aparecer *"Sin respuesta después de 3 s"*, porque el firewall descarta el paquete sin avisar. Las dos cosas son correctas y sirven para explicar la pregunta f.

## 8. Problemas comunes

| Problema | Solución |
|---|---|
| `'python' no se reconoce como un comando...` | Probá con `py` o `python3`. Si ninguno anda, reinstalá Python marcando **"Add python.exe to PATH"** |
| `ModuleNotFoundError: No module named 'comun'` | La terminal no está en la carpeta del proyecto, o falta `comun.py` |
| `OSError: [WinError 10048]` / `Address already in use` | Ya hay un servidor ejecutándose en otra terminal: cerralo con `Ctrl+C` |
| `Ctrl+C` no cierra el servidor | Tenés una versión vieja del código: cerrá la terminal con la X y bajá de nuevo el repositorio |
| `No se pudo conectar ... (conexión rechazada)` | El servidor no está ejecutándose, o la IP está mal escrita |
| Desde otra compu se queda esperando y da timeout | Firewall de la notebook servidor, IP equivocada o red que aísla equipos: usá el **plan B** |
| `Sin respuesta después de 3 s` en UDP | Lo mismo que el anterior; también pasa si el servidor UDP no está ejecutándose |
| Se abre la Microsoft Store al escribir `python` | Usá `py`, o instalá Python desde python.org |

## 9. Más material

- [`respuestas.md`](respuestas.md): preguntas teóricas a–i.
- [`explicacion_codigo.md`](explicacion_codigo.md): explicación del código línea por línea y preguntas que nos pueden hacer.
- [`guion_exposicion.md`](guion_exposicion.md): guion completo de la exposición.
- [`guia_packet_tracer.md`](guia_packet_tracer.md): topología, direccionamiento y demostración en modo Simulación.
