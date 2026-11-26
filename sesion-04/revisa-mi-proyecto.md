# Revisa mi proyecto

Un prompt para saber, en cinco minutos, por dónde vas de verdad. Tu agente hace de revisor: comprueba cada pieza con pruebas (archivos, URLs que responden), te dice qué falta y te deja las tres tareas siguientes.

Funciona con cualquier agente (Claude Code, Gemini CLI, Codex, Antigravity u OpenCode). Ábrelo en la carpeta de tu cuaderno y pega el prompt. Úsalo cuando quieras; lo normal, una vez al día antes de cerrar. Desde hoy comprueba también tu MCP: **tus tres URLs** (web, modelo y MCP).

```text
Haz de revisor de mi proyecto del Módulo 10. Sé directo: no me des ánimos,
dime qué hay y qué falta. No cambies código ni despliegues nada; solo los
archivos del cuaderno que te digo al final.

Lee mi cuaderno (brief.md, arquitectura.md, estado.yaml, todo.md,
decisiones.md, urls.md, bitacora/) y el repo de mi app en apps/.

1. PIEZAS. Para cada una, di "hecho", "a medias" o "sin empezar", con la
   prueba: el archivo que lo demuestra o la URL, abierta de verdad (haz la
   petición y dime el código que devuelve).
   - Web publicada en Vercel desde el repo de mi app (sesión 1).
   - Datos en Supabase y app que los lee, con login y algo que guarda cada
     usuario (sesión 2).
   - Modelo: predicción ingenua y modelo comparados, API en Render con
     /health y /predict, y la app enseñando la predicción (sesión 3).
   - MCP (sesión 4): modelo/servidor_mcp.py con al menos dos herramientas,
     montado en /mcp de mi API del modelo, y mi agente conectado a él.
   - Agente (sesiones 5 y 6), seguridad (sesión 7): si la sesión todavía no
     ha pasado, "todavía no toca".
2. MIS TRES URLS. Haz las tres peticiones sin ningún token y dime el código:
   - Mi web en Vercel: tiene que dar 200.
   - <mi API del modelo>/health: tiene que dar 200 con {"ok": true}.
   - <mi API del modelo>/mcp, sin cabecera Authorization: tiene que dar 401
     con un mensaje de "Falta el token". Un 401 quiere decir vivo y
     protegido. Un 200 sin token es un fallo de seguridad grave: dímelo el
     primero. Un 404 o un 502 quiere decir que no está.
   Si la primera petición a Render tarda o falla, espera un minuto y repite:
   el plan gratis se duerme.
3. SEGURIDAD. Busca en los dos repos (también en el historial de git, con
   git log -p) claves que no deberían estar: claves secretas de Supabase
   (sb_secret_, service_role), contraseñas, cadenas de conexión
   postgres://, y el token de mi MCP. El token puede estar en: .mcp.json,
   opencode.json, .env, .codex/, cualquier archivo con "Authorization:
   Bearer" seguido de algo que no sea un marcador como <tu token>, o una
   línea MCP_TOKEN= con un valor. Dime el archivo y la línea, nunca el
   valor. Comprueba también que servidor_mcp.py usa la clave publicable de
   Supabase, no una secreta. La clave publicable de Supabase y las URLs de
   mi web y de mi API no son secretas.
4. EL MCP, si existe:
   - ¿Usa la librería mcp 2.x (MCPServer, mcp==2.3.0 en requirements.txt)
     y no FastMCP ni el paquete fastmcp?
   - ¿El app.mount del MCP es la última línea de main.py, y /predict sigue
     respondiendo?
   - ¿Las descripciones de las herramientas y de sus parámetros las
     entendería alguien que no conoce mis datos? ¿Queda algún "CAMBIA" o
     algún nombre de la plantilla (buscar_X, predecir_Y)?
   - ¿Hay en la bitácora la prueba de que mi agente está conectado: la
     lista de mis herramientas como la ve mi agente y una pregunta con su
     respuesta y las herramientas que llamó? Si no está, dímelo como "a
     medias".
5. EL MODELO, si existe: ¿hay alguna columna que no tendría antes de
   conocer la respuesta (fuga de datos)? ¿Mejora a la predicción ingenua?
   ¿Cuánto pesa el archivo? ¿Coinciden las versiones de requirements.txt
   con las que usé para entrenar? ¿Están modelo.joblib y metricas.json en
   el repo de mi app (Render construye desde ahí y sin ellos no arranca), y
   fuera el CSV grande o privado y .venv?
6. EL CUADERNO: ¿decisiones.md explica por qué elegí cada cosa, o solo qué
   hice? ¿Hay una nota en la bitácora por cada sesión, también la de la
   sesión 3 (25/11)? ¿estado.yaml dice la verdad y respeta su esquema?
   ¿urls.md tiene mis tres URLs?
7. SI PRESENTARA HOY. La nota es complejidad técnica (50 %), uso de las
   técnicas del módulo (30 %) y presentación y resolución de problemas
   (20 %). Para aprobar tienen que funcionar la app con datos, el modelo
   como API y el MCP. Sin poner nota: ¿qué tengo para cada parte y cuál es
   mi punto más débil?
8. LAS TRES SIGUIENTES. Las tres tareas que más me acercan a tener todo
   funcionando, en orden, cada una de menos de una hora.

Escribe el resultado en revision/AAAA-MM-DD.md (la fecha de hoy), con una
tabla para el punto 1 y otra para el punto 2. Después actualiza estado.yaml
para que diga lo que has comprobado (no cambies las claves), pon las tres
tareas en todo.md y haz commit y push en el cuaderno. Ningún token ni
ninguna clave en lo que escribas.
```

Qué hacer con el resultado:

- **Un "a medias" en una sesión que ya pasó** va antes que lo de hoy. Pide ayuda a tu pareja de apoyo o al docente.
- **`/mcp` responde 200 sin token:** no conectes nada más. Vuelve a la plantilla (`app_mcp.add_middleware(PideToken)` y `MCP_TOKEN` en Render) y repite la revisión.
- **Tu token o una clave secreta en el repo:** avisa al docente antes de seguir. Hay que cambiarlo en el panel (otro `MCP_TOKEN` en Render, otra clave en Supabase) y en la configuración de tu agente: borrarlo del archivo no basta, sigue en el historial de git.
- **Falta la prueba de conexión en la bitácora:** el apartado "Mi MCP" del prompt de cierre de `tu-mcp.md` (parte 6).
- **Todo "hecho" y te sobra tiempo:** el apartado "Si vas por delante" de la guía del día.
