# Sesión 3: tu modelo como API, paso a paso

**Hecho** = en tu URL de Vercel rellenas un formulario y ves la predicción de tu modelo, servida desde Render.

Son seis partes, en orden. No empieces una sin tener la anterior. Los prompts se pegan en tu agente, abierto **en la carpeta de tu cuaderno**, como ayer.

| Parte | Qué | Dónde |
|---|---|---|
| 1 | Decides qué predices | Tu cuaderno |
| 2 | Tu agente entrena el modelo | Tu ordenador (o Colab) |
| 3 | El modelo se convierte en una API | Tu ordenador |
| 4 | Publicas la API | Render |
| 5 | Tu app la usa | Tu app, en Vercel |
| 6 | Cierras el día | Tu cuaderno |

¿Te falta algo de ayer (datos en Supabase, login)? Eso va primero: `sesion-02/tu-app-con-datos.md`. ¿Ya has terminado? Abajo tienes "Si vas por delante".

---

## Antes de empezar: ¿tienes Python?

**Mac, Linux o Git Bash en Windows:**

```bash
python3 --version
```

**Windows, en PowerShell:**

```powershell
py --version
```

Tiene que salir `Python 3.10` o más. Apunta el número entero (por ejemplo `3.12.7`): lo vas a necesitar en Render.

- **No sale nada o da error:** instálalo desde https://www.python.org/downloads/ (en Windows, marca "Add python.exe to PATH" en la primera pantalla), cierra la terminal y ábrela otra vez.
- **Portátil de empresa y no puedes instalar:** usa el camino sin Python, al final de la parte 2.

---

## Parte 1: decide qué predices

Tu agente propone; tú decides. Pégale esto:

```text
Lee brief.md, arquitectura.md, datos.md y estado.yaml. Hoy toca la pieza
"modelo". Antes de escribir código, propónme:

1. Qué columna de mis datos predecir, y si es un número (regresión) o una
   etiqueta (clasificación).
2. Con qué columnas. Solo las que conoceré ANTES de saber la respuesta: si
   una columna se calcula a partir de lo que quiero predecir, fuera.
3. Con qué filas se examina el modelo: si mis datos tienen fecha, las más
   recientes; si no, un 20 % al azar (random_state=42).
4. Cuál es la predicción ingenua (la media, o la etiqueta más frecuente)
   y con qué medida la comparo, en unidades que yo entienda.
5. Qué verá el usuario de mi app: qué rellena y qué le devuelvo.

Dame dos o tres opciones si las hay, con lo bueno y lo malo de cada una.
No escribas código todavía. Cuando yo elija, apunta la decisión en
decisiones.md con la fecha de hoy.
```

**Hecho:** en `decisiones.md` está qué predices, con qué columnas y por qué.

---

## Parte 2: tu agente entrena el modelo

```text
Lee la decisión de hoy en decisiones.md. Entrena el modelo, en local:

1. En el repo de mi app (dentro de apps/), crea la carpeta modelo/ con un
   entorno virtual (.venv, añadido a .gitignore). Si estoy en Windows, dame
   los comandos en PowerShell.
2. modelo/pistas.py: la lista de columnas y una función preparar(tabla) que
   deja las columnas listas (sí o no como 1 y 0, etc.). La usarán el
   entrenamiento y la API: así un dato nuevo pasa por los mismos pasos.
3. modelo/entrenar.py: lee mi CSV, separa aprender y examen como decidimos,
   calcula la predicción ingenua, entrena un modelo sencillo de scikit-learn
   dentro de un Pipeline (rellenar huecos y convertir texto van dentro) y
   enseña las dos cifras: la ingenua y la del modelo.
4. Guarda el pipeline en modelo/modelo.joblib y las cifras en
   modelo/metricas.json. El archivo del modelo tiene que pesar menos de
   50 MB: si pesa más, usa HistGradientBoosting en vez de un bosque.
5. modelo/requirements.txt con las versiones exactas que has instalado.
6. Si mis datos son privados o el CSV pesa más de 50 MB, no los subas a
   GitHub: dímelo y lo decidimos.
7. Explícame el resultado en tres frases: cuánto mejora a la ingenua y si
   hay algo sospechoso (un resultado demasiado bueno suele ser una fuga).
8. Añade a la entrada de hoy en decisiones.md el modelo elegido y las dos
   cifras. Commit y push en el repo de la app.
```

### Si tu agente te pide crear el entorno virtual tú

En la carpeta `modelo/` de tu app.

**Mac, Linux o Git Bash en Windows:**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pandas scikit-learn joblib
```

**Windows, en PowerShell:**

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install pandas scikit-learn joblib
```

Si PowerShell dice "running scripts is disabled", ejecuta esto una vez y vuelve a activar el entorno:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### El camino sin Python: entrenar en Colab

Para quien no puede instalar nada. Pídele a tu agente los archivos igual (pasos 2 a 5 del prompt, sin ejecutarlos) y después:

1. Abre https://colab.research.google.com, "Nuevo cuaderno".
2. En el panel de archivos de la izquierda, sube `pistas.py`, `entrenar.py` y tu CSV.
3. En una celda: `!python entrenar.py` (ajusta antes en `entrenar.py` la ruta del CSV).
4. Descarga `modelo.joblib` y `metricas.json` y ponlos en `modelo/` de tu repo.
5. En otra celda: `!python --version` y `!pip freeze | grep -E "scikit-learn|pandas|joblib"`. Esas son las versiones que van en `requirements.txt` y en Render.

Si tus datos son de tu empresa o tienen datos personales, no los subas a Colab: usa una muestra con los valores cambiados.

**Hecho:** tienes las dos cifras, `modelo/modelo.joblib` y `modelo/requirements.txt` en el repo de tu app. Si tu modelo no mejora a la predicción ingenua, también se apunta: es un resultado, y se puede presentar.

---

## Parte 3: tu modelo como API, en local

```text
Lee arquitectura.md y la entrada del modelo en decisiones.md. Ahora la API,
en modelo/ del repo de mi app:

1. main.py con FastAPI:
   - GET /health devuelve {"ok": true}.
   - GET /info devuelve lo que hay en metricas.json.
   - POST /predict recibe las columnas del modelo (un modelo de Pydantic con
     sus tipos y sus límites) y devuelve la predicción.
   modelo.joblib se carga una sola vez, al arrancar. Usa preparar() de
   pistas.py: no repitas esa lógica.
2. CORS: permite mi URL de Vercel (está en urls.md) y localhost en cualquier
   puerto (allow_origin_regex). Nada más.
3. Añade fastapi y uvicorn a requirements.txt, con sus versiones exactas.
4. Arráncala en local y dime qué URL abro para ver /docs, con un ejemplo
   real de mis datos para probar /predict.
5. Dime mi versión exacta de Python: la necesito para Render.

Commit y push.
```

Pruébala en el navegador: en `/docs` abre `POST /predict`, pulsa "Try it out", pega el ejemplo y "Execute".

**Hecho:** `/health` responde y `/predict` devuelve una predicción con un ejemplo de tus datos. (Sin Python en tu portátil: sáltate la prueba en local y pruébala ya publicada, en la parte 4.)

---

## Parte 4: publícala en Render

En el panel de Render, sin agente.

1. Entra en https://render.com con tu cuenta de GitHub.
2. **New, Web Service.** Conecta GitHub y elige el repo de tu app. Es privado: si no aparece, en "Configure account" dale a Render acceso solo a ese repo.
3. Rellena:
   - **Name:** tu proyecto con `-modelo` al final. Sale en la URL.
   - **Language:** Python 3. **Branch:** `main`.
   - **Region:** Frankfurt (EU Central).
   - **Root Directory:** `modelo`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type:** Free.
4. **Environment Variables:** añade `PYTHON_VERSION` con tu versión exacta de Python (por ejemplo `3.12.7`). Así Render usa la misma que tú.
5. **Deploy Web Service.** Tarda unos minutos. En "Logs", espera a ver que está en marcha ("live").
6. Abre `https://tu-servicio.onrender.com/health` y después `/docs`, y prueba `/predict`.

**El plan gratis se duerme** a los 15 minutos sin uso y tarda cerca de un minuto en despertar. La primera llamada después de un rato es lenta: es normal.

**Hecho:** tu `/health` responde en `onrender.com`.

---

## Parte 5: tu app usa tu modelo

```text
Mi modelo ya está en Render: <pega aquí tu URL de onrender.com>. Lee
arquitectura.md. En la web de mi app:

1. Añade un formulario con lo que necesita /predict y enseña la predicción
   con sus unidades y con el error medio del modelo (está en /info).
   Pregunta al usuario cosas que sepa contestar: si el modelo necesita un
   dato que el usuario no conoce, calcúlalo tú a partir de lo que sí sabe.
2. Llama a <mi URL>/predict con fetch. Mientras espera, enseña "Despertando
   el modelo, puede tardar un minuto". Si falla, un mensaje claro.
3. La URL de la API no es secreta: puede ir en el código.
4. Pruébalo en local; después commit y push para que Vercel lo publique.
```

**Hecho, el hito de hoy:** en tu URL de Vercel rellenas el formulario y ves la predicción.

---

## Parte 6: cierra el día en tu cuaderno

Lo último, cada tarde. Con este prompt tu agente escribe la bitácora a partir de lo que habéis hecho, sin que tengas que acordarte:

```text
Cierra el día en mi cuaderno:

1. Repasa lo que hemos hecho hoy: esta conversación y el historial de git de
   hoy (git log --since=midnight) en el cuaderno y en el repo de mi app.
2. Escribe bitacora/AAAA-MM-DD.md (la fecha de hoy) con cuatro apartados
   cortos: qué quería conseguir, qué te pedí (los dos o tres prompts que
   funcionaron, tal cual), qué falló y cómo lo arreglamos, y qué he
   aprendido. Que suene a mí, sin adornos. Lo que no sepas, pregúntamelo.
3. Actualiza estado.yaml (la pieza "modelo" con su estado, su url y su
   repo; no cambies las claves), todo.md y urls.md con la URL de Render.
4. Commit y push en el cuaderno.
```

Y publica tu URL de Vercel y una frase con lo que funciona en el debate "Ideas y URLs" del aula.

La bitácora es de donde sale tu documento de autoevaluación del 3 de diciembre y la parte de "cómo resolví los errores" de tu presentación (el 20 % de la nota).

---

## Si vas por delante

Siete escalones, de menos a más. Cada uno deja algo que enseñar el 9 de diciembre. Apunta en `decisiones.md` lo que pruebes, también lo que no funcione.

1. **Compara modelos.** Que tu agente entrene tres (uno lineal, un árbol, un boosting) con el mismo examen y te haga una tabla: error, tamaño del archivo y tiempo. ¿Con cuál te quedas y por qué?
2. **Mira dónde falla.** El error por grupos (por categoría, por tramo, por fecha). ¿Hay un grupo donde el modelo no sirve? Dilo en tu app.
3. **Qué columnas pesan más.** Importancia por permutación. Quita las tres que menos pesan: ¿empeora? Un formulario más corto es mejor producto.
4. **Un rango en vez de un número.** Que `/predict` devuelva también un mínimo y un máximo (cuantiles 10 y 90) y que tu app lo enseñe.
5. **Guarda las predicciones.** Una tabla `predicciones` en Supabase, con RLS, donde cada usuario ve las suyas: une lo de ayer con lo de hoy.
6. **Una prueba automática.** Un archivo `test_api.py` que llame a `/health` y a `/predict` con un ejemplo y compruebe que la respuesta tiene sentido. Lo ejecutas antes de cada push.
7. **Explica tu modelo a alguien que no es técnico.** Una sección "Cómo funciona" en tu app: con qué datos aprendió, cuánto se equivoca y cuándo no hay que fiarse.

Los extras A a F del cuaderno de Colab de hoy enseñan cómo se hacen el 2, el 3 y el 4.

Y siempre vale el escalón cero: ayudar a quien tienes al lado. Explicar un error que ya resolviste cuenta en el stand-up de las 21:00.

---

## Si algo falla

| Qué ves | Qué pasa | Qué hacer |
|---|---|---|
| `python3` o `py` no se reconoce | Python no está instalado o falta reabrir la terminal | Instálalo desde python.org (en Windows, "Add python.exe to PATH") y abre una terminal nueva |
| "running scripts is disabled" en PowerShell | Windows no deja activar el entorno | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` y vuelve a activar |
| El modelo acierta casi siempre | Fuga de datos: una columna es la respuesta disfrazada | Revisa cada columna: ¿la tendrás antes de conocer la respuesta? |
| `Can't get attribute ... on <module '__main__'>` al arrancar la API | El modelo se guardó con una función definida en `entrenar.py` | Esa función va en `pistas.py` y se importa desde los dos archivos; entrena otra vez |
| Render: `ModuleNotFoundError` | Falta una librería en `requirements.txt` | Añádela con su versión exacta, commit y push |
| Render: error al instalar o aviso de versión de scikit-learn | Render usa otra versión de Python que tú | Variable `PYTHON_VERSION` con tu versión exacta, y "Manual Deploy" |
| Render: "Out of memory" | El modelo o los datos no caben en 512 MB | Modelo más pequeño (HistGradientBoosting); la API no carga el CSV, solo el modelo |
| Render no encuentra `main.py` | El Root Directory no es `modelo` | Settings, Root Directory: `modelo` |
| La app dice que no puede llamar a la API y la consola dice "CORS" | Tu URL de Vercel no está en la lista de la API | En `main.py`, tu URL tal cual, con `https://` y sin `/` al final; commit y push |
| `/predict` devuelve 422 | Falta un campo o su tipo no cuadra | Lee el mensaje: dice qué campo. Compara con el ejemplo de `/docs` |
| La primera llamada tarda un minuto | El servicio gratis estaba dormido | Es normal. Tu app tiene que avisarlo |

Para cualquier otro error en Render: copia las últimas líneas de "Logs" y pégaselas a tu agente con "Render me da este error al desplegar modelo/. ¿Qué cambio?".
