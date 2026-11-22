# Setup paso a paso

Módulo 10 · Sesión 1 · lunes 23/11/2026

Al terminar esta guía tendrás todo lo necesario para el módulo: tu cuenta de GitHub, Git conectado a ella, un agente de programación con IA (OpenCode) y tus cuentas de Vercel, Supabase y Render. Son unos 30 a 45 minutos si empiezas de cero.

**Tres reglas antes de empezar:**
1. **Usa tu email personal**, no el de Inesdi. Son cuentas que te vas a quedar.
2. **Todo en plan gratuito.** Ningún paso de esta guía cuesta dinero.
3. **Si alguna web te pide una tarjeta, para.** Casi siempre es que has elegido un plan de pago o una prueba sin querer. Vuelve atrás y, si no lo ves claro, avísame.

**Orden de ayuda:** esta guía, tu pareja de apoyo, yo.

---

## Paso 1: cuenta de GitHub

GitHub es donde vivirá el código de tu proyecto. Todo lo demás se conecta a él.

1. Entra en https://github.com y pulsa **Sign up**.
2. Email personal, contraseña y un nombre de usuario. Elígelo bien: aparecerá en tus URLs y en tu portfolio (por ejemplo, `nombre-apellido`).
3. Verifica el email con el código que te llega.
4. Si te pide activar la verificación en dos pasos, hazlo con una app de autenticación del móvil. Guarda los códigos de recuperación.

**Ya lo tengo si:** entro en github.com y veo mi panel.

---

## Paso 2: abre una terminal

La terminal es la ventana donde se escriben comandos. Te va a hacer falta en los pasos 3 y 4.

- **Mac:** pulsa `Cmd + Espacio`, escribe `Terminal` y pulsa Enter.
- **Windows:** usa **Git Bash**, que se instala con Git en el paso 3. Hasta entonces, PowerShell (menú Inicio, escribe `PowerShell`).

En esta guía, lo que va en un recuadro gris es un comando: se escribe (o se pega) en la terminal y se pulsa Enter.

---

## Paso 3: Git

Git guarda la historia de tu código y lo sube a GitHub.

**Mac:**
```bash
git --version
```
Si aparece una versión (`git version 2.x`), ya lo tienes. Si aparece una ventana que ofrece instalar las "herramientas de desarrollo de línea de comandos", pulsa **Instalar** y espera (5 a 10 minutos). Después repite el comando.

**Windows:**
1. Descarga el instalador de https://git-scm.com/downloads/win.
2. Instálalo con todas las opciones por defecto (siguiente, siguiente...).
3. Abre **Git Bash** desde el menú Inicio y comprueba:
```bash
git --version
```

**Dile a Git quién eres** (en los dos sistemas; con tu nombre y el email de tu cuenta de GitHub):
```bash
git config --global user.name "Tu Nombre"
git config --global user.email "tu-email@ejemplo.com"
```

**Ya lo tengo si:** `git --version` muestra una versión y `git config --global user.name` muestra mi nombre.

---

## Paso 4: conecta Git con tu GitHub

Para subir código a GitHub, Git necesita tu permiso. La forma más sencilla es la herramienta oficial de GitHub para la terminal, `gh`.

1. Instálala:
   - **Mac:** descarga el instalador de macOS en https://cli.github.com (o, si usas Homebrew, `brew install gh`).
   - **Windows:** descarga el instalador de Windows en https://cli.github.com (o en PowerShell: `winget install --id GitHub.cli`). Después **cierra y vuelve a abrir** Git Bash.
2. Inicia sesión:
   ```bash
   gh auth login
   ```
   Responde así a las preguntas:
   - Where do you use GitHub? **GitHub.com**
   - Preferred protocol? **HTTPS**
   - Authenticate Git with your GitHub credentials? **Yes**
   - How would you like to authenticate? **Login with a web browser**

   Copia el código de 8 caracteres que aparece, pulsa Enter, pégalo en la web que se abre y autoriza.
3. Comprueba:
   ```bash
   gh auth status
   ```

**Ya lo tengo si:** `gh auth status` dice `Logged in to github.com`.

> **Si no hay manera:** hoy puedes llegar al hito igual creando los archivos directamente en la web de GitHub (lo explica `de-cero-a-url.md`, "Camino sin instalar nada"). Arreglamos Git con calma después.

---

## Paso 5: OpenCode, tu agente de programación

OpenCode es un agente de IA que lee tu proyecto, escribe código y ejecuta comandos por ti. Es gratuito y trae modelos gratis. Casi nunca pide permiso: ábrelo solo en la carpeta de tu proyecto.

**¿Ya usas otro agente?** También vale: Claude Code, Codex, Gemini CLI o Antigravity. Los prompts del módulo funcionan igual; si tu agente no lee `AGENTS.md` solo, empieza tus prompts con "Lee AGENTS.md". Las guías van con OpenCode, y en clase te ayudo con el tuyo.

1. Descárgalo de https://opencode.ai/download. Vale la **app de escritorio** (Mac o Windows).
   - En Mac también puedes instalarlo desde la terminal: `curl -fsSL https://opencode.ai/v2/install | bash` (sin `/v2/` instala la versión antigua, sin modelos gratis)
2. Ábrelo y elige una carpeta para trabajar (por ejemplo, Documentos).
3. **Elige un modelo gratis:** en el selector de modelos (el botón con el nombre del modelo, junto a donde escribes; en la terminal, `/models`), uno de los que aparecen como *Free*.
4. Si te pide iniciar sesión, crea tu cuenta en opencode.ai con "Continue with GitHub".
5. Prueba que funciona. Escribe:
   ```
   Hola. Dime qué modelo eres y lista los archivos de esta carpeta.
   ```

**Ya lo tengo si:** OpenCode me contesta y me enseña los archivos de la carpeta.

**Si ya pagas un plan de IA:**
- **ChatGPT Go o Plus:** OpenCode debería poder usar tu cuenta de ChatGPT (con `/connect`, eligiendo OpenAI). Lo comprobamos juntos en clase; mientras, usa un modelo gratis.
- **Claude Pro o Max:** ese plan no se puede usar dentro de OpenCode (las condiciones de Anthropic lo reservan para sus propias apps). Puedes usar **Claude Code** en lugar de OpenCode: todo lo de este módulo vale igual.
- **OpenCode Go** (10 $ al mes) es opcional. Nadie tiene que pagar nada para seguir el módulo.

**Plan B: si OpenCode dice que se ha acabado la cuota gratis** (puede pasar: somos muchos en la misma wifi):
1. Entra en https://aistudio.google.com con tu cuenta de Google personal y pulsa **Get API key**, **Create API key**. Es gratis y no pide tarjeta.
2. En OpenCode, escribe `/connect`, elige **Google** y pega la clave.
3. En el selector de modelos, elige un modelo Gemini Flash.

La clave es como una contraseña: no la pegues en ningún archivo, ni en el debate “Ideas y URLs” del aula virtual, ni en GitHub.

---

## Paso 6: Vercel

Vercel publica tu web en internet. Cada vez que subas un cambio a GitHub, lo vuelve a publicar solo.

1. Entra en https://vercel.com/signup.
2. Elige **Hobby** (proyectos personales). No elijas Pro ni pruebas de Pro.
3. **Continue with GitHub** y autoriza.

**Ya lo tengo si:** entro en vercel.com y veo mi panel, con el plan Hobby.

---

## Paso 7: Supabase

Supabase será tu base de datos y tu login. Lo usamos mañana; hoy solo la cuenta.

1. Entra en https://supabase.com y pulsa **Start your project**.
2. **Continue with GitHub** y autoriza.
3. Si te pide crear una organización: tu nombre, tipo **Personal**, plan **Free**.
4. **No crees ningún proyecto todavía.** Lo hacemos mañana juntos.

**Ya lo tengo si:** entro en supabase.com y veo mi panel, con el plan Free.

---

## Paso 8: Render

Render servirá tu modelo de machine learning como una API (sesión 3). Hoy solo la cuenta.

1. Entra en https://render.com y pulsa **Get Started**.
2. Entra con **GitHub** y autoriza.
3. No crees nada todavía.

**Ya lo tengo si:** entro en render.com y veo mi panel.

---

## ¿Lo tengo? Comprobación de 1 minuto

| | Cómo lo compruebo |
|---|---|
| [ ] Cuenta de GitHub con email personal | Entro en github.com y veo mi panel |
| [ ] Git instalado | `git --version` muestra una versión |
| [ ] Git sabe quién soy | `git config --global user.name` muestra mi nombre |
| [ ] Git conectado a GitHub | `gh auth status` dice `Logged in to github.com` |
| [ ] Mi agente funciona (OpenCode u otro) | Contesta a "hola" y lista los archivos de la carpeta |
| [ ] Vercel | Entro con GitHub y veo el plan Hobby |
| [ ] Supabase | Entro con GitHub y veo el plan Free |
| [ ] Render | Entro con GitHub y veo mi panel |
| [ ] Sin tarjeta | No he metido una tarjeta en ningún sitio |
| [ ] Opcional: Python | `python3 --version` (en Windows, `python --version`) muestra una versión. Sirve para calcular cifras con tus datos; si no lo tienes, no lo instales hoy |

¿Todo marcado? Ayuda a tu pareja de apoyo y, después, empieza con tu idea (paso 0 de `de-cero-a-url.md`).

---

## Si algo falla

| Síntoma | Causa típica | Arreglo |
|---|---|---|
| Vercel, Supabase o Render piden tarjeta | Has elegido un plan de pago o una prueba | Vuelve atrás y elige Hobby o Free. Si insiste, para y avísame |
| Windows: `git` o `gh` "no se reconoce como comando" | La terminal se abrió antes de instalar | Cierra la terminal y ábrela de nuevo |
| Mac: aparece una ventana de "herramientas de desarrollo" | Git no estaba instalado | Pulsa Instalar y espera |
| `git push` pide usuario y contraseña | Git no está conectado a GitHub | Repite el paso 4 (`gh auth login`) |
| `gh auth login` no abre el navegador | Pasa en algunos equipos | Abre a mano https://github.com/login/device y pega el código |
| OpenCode: "Free usage limit reached" o no contesta | La cuota gratis es limitada y compartida por la red | Plan B del paso 5 (clave gratis de Gemini) |
| OpenCode no ofrece modelos *Free* | Tienes la versión 1 | Instala la app de opencode.ai/download |
| Portátil de empresa que no deja instalar | Política de tu empresa | Avísame al principio. Hoy puedes seguir con el "Camino sin instalar nada" de `de-cero-a-url.md` |
