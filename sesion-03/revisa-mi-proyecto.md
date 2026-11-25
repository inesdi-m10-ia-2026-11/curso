# Revisa mi proyecto

Un prompt para saber, en cinco minutos, por dónde vas de verdad. Tu agente hace de revisor: comprueba cada pieza con pruebas (archivos, URLs que responden), te dice qué falta y te deja las tres tareas siguientes.

Funciona con cualquier agente (Claude Code, Gemini CLI, Codex, Antigravity u OpenCode). Ábrelo en la carpeta de tu cuaderno y pega el prompt. Úsalo cuando quieras; lo normal, una vez al día antes de cerrar.

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
   - MCP (sesión 4), agente (sesiones 5 y 6), seguridad (sesión 7): si la
     sesión todavía no ha pasado, "todavía no toca".
2. SEGURIDAD. Busca en los dos repos claves que no deberían estar: claves
   secretas de Supabase (sb_secret_, service_role), contraseñas, cadenas de
   conexión postgres://, tokens. Dime el archivo y la línea, nunca el valor.
   La clave publicable de Supabase y la URL de mi API no son secretas.
3. EL MODELO, si existe: ¿hay alguna columna que no tendría antes de
   conocer la respuesta (fuga de datos)? ¿Mejora a la predicción ingenua?
   ¿Cuánto pesa el archivo? ¿Coinciden las versiones de requirements.txt
   con las que usé para entrenar?
4. EL CUADERNO: ¿decisiones.md explica por qué elegí cada cosa, o solo qué
   hice? ¿Hay una nota en la bitácora por cada sesión? ¿estado.yaml dice la
   verdad y respeta su esquema?
5. SI PRESENTARA HOY. La nota es complejidad técnica (50 %), uso de las
   técnicas del módulo (30 %) y presentación y resolución de problemas
   (20 %). Para aprobar tienen que funcionar la app con datos, el modelo
   como API y el MCP. Sin poner nota: ¿qué tengo para cada parte y cuál es
   mi punto más débil?
6. LAS TRES SIGUIENTES. Las tres tareas que más me acercan a tener todo
   funcionando, en orden, cada una de menos de una hora.

Escribe el resultado en revision/AAAA-MM-DD.md (la fecha de hoy), con una
tabla para el punto 1. Después actualiza estado.yaml para que diga lo que
has comprobado (no cambies las claves), pon las tres tareas en todo.md y
haz commit y push en el cuaderno.
```

Qué hacer con el resultado:

- **Un "a medias" en una sesión que ya pasó** va antes que lo de hoy. Pide ayuda a tu pareja de apoyo o al docente.
- **Una clave secreta en el repo:** avisa al docente antes de seguir. Hay que cambiarla en el panel, no basta con borrarla del archivo.
- **Todo "hecho" y te sobra tiempo:** el apartado "Si vas por delante" de la guía del día.
