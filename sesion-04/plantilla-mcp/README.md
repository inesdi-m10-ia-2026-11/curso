# Plantilla de tu servidor MCP (sesión 4)

Tu MCP no es un servicio nuevo: va **dentro de tu API del modelo**, en `/mcp`, en el mismo Render. Un servicio, un despertar, un despliegue.

| Archivo | Qué es | Dónde va |
|---|---|---|
| `servidor_mcp.py` | El servidor: `buscar_X` (lee tu tabla de Supabase), `predecir_Y` (llama a tu `/predict`) y el token | `modelo/` de tu app, junto a `main.py` |
| `probar_mcp.py` | Prueba sin asistente: lista tus herramientas y llama a cada una | `modelo/` |
| `requirements-mcp.txt` | Las dos líneas que se añaden a tu `requirements.txt` | Se copian al final de `modelo/requirements.txt` |

Lo normal es que tu agente haga todo esto con el prompt de la parte 3 de `tu-mcp.md`. Esta página es para entender qué hace, o para hacerlo a mano.

## 1. Copia los archivos

`servidor_mcp.py` y `probar_mcp.py` a la carpeta `modelo/` de tu app. **No le cambies el nombre a `mcp.py`:** taparía la librería y saldría `No module named 'mcp.server'; 'mcp' is not a package`.

## 2. Añade las dependencias

Al final de `modelo/requirements.txt`:

```text
mcp==2.3.0
httpx==0.28.1
```

`mcp==2.3.0` va fijado a propósito. Con la 1.x, o con el paquete `fastmcp` (que es otro), la plantilla no funciona. Si tu agente propone `from mcp.server.fastmcp import FastMCP`, es código de la 1.x: dile que no.

## 3. Cinco líneas en tu `main.py`

Lo marcado con `# MCP` es lo nuevo. Lo demás ya lo tienes de la sesión 3.

```python
from contextlib import asynccontextmanager          # MCP 1: arriba, con los otros import
from fastapi import FastAPI
# ... tus otros import ...
from servidor_mcp import app_mcp, mcp               # MCP 2


@asynccontextmanager                                # MCP 3: antes de crear la app
async def arranque(app):
    async with mcp.session_manager.run():
        yield


app = FastAPI(title="...", lifespan=arranque)       # MCP 4: añade lifespan=arranque

# ... tu CORS, /health, /info, /predict: igual que estaban ...

app.mount("/", app_mcp)                             # MCP 5: la ÚLTIMA línea del archivo
```

Por qué así:

- **El `mount` va al final.** Si va antes de tus rutas, el MCP se queda con todas: `/health` y `/predict` dan `404 Not Found` y tu web de la sesión 3 deja de predecir.
- **El `lifespan` arranca el gestor del MCP.** Sin él, tu agente no conecta y en los logs sale `RuntimeError: Task group is not initialized`. Si tu `main.py` ya tiene un `lifespan`, mete el `async with mcp.session_manager.run():` dentro del tuyo. Si tiene `@app.on_event("startup")`, pide a tu agente que pase eso al `lifespan`.
- **El token lo comprueba `servidor_mcp.py`.** Solo `/mcp` lo pide; `/health`, `/info` y `/predict` siguen abiertos para tu web.

## 4. Rellena lo marcado con CAMBIA

En `servidor_mcp.py`:

1. **Tu Supabase:** `SUPABASE_URL` y `SUPABASE_KEY`, los mismos que en tu `web/index.html`. Solo la clave **publicable** (`sb_publishable_...` o `anon`). Si pones la secreta, el servidor no arranca: lo hace a propósito.
2. **Qué lee `buscar_X`:** `TABLA`, `COLUMNAS`, `COLUMNA_TEXTO` y `COLUMNA_NUMERO`.
3. **Los nombres:** `buscar_X` y `predecir_Y` pasan a ser los tuyos (`buscar_ventas`, `predecir_viajeros`...). Cambia también los nombres en `instructions`, en los docstrings y en `PRUEBAS` de `probar_mcp.py`.
4. **Los parámetros de `predecir_Y`:** los mismos campos que pide tu `/predict` (el modelo de Pydantic de tu `main.py`), con el mismo nombre, tipo y límites.
5. **Las descripciones.** Es lo más importante: la IA no lee tu código, lee el nombre de cada herramienta, su docstring y la descripción de cada parámetro. Escríbelas para alguien que no conoce tus datos, con valores de ejemplo reales.

## 5. Pruébalo en local

Dos terminales, en `modelo/`, con tu entorno de la sesión 3. En local el token puede ser cualquier palabra: el servidor solo está en tu ordenador.

**Mac, Linux o Git Bash.** Terminal 1:

```bash
source .venv/bin/activate
pip install -r requirements.txt
export MCP_TOKEN=prueba-local
uvicorn main:app --reload
```

Terminal 2:

```bash
source .venv/bin/activate
MCP_URL=http://localhost:8000/mcp MCP_TOKEN=prueba-local python probar_mcp.py
```

En Git Bash en Windows, el entorno se activa con `source .venv/Scripts/activate` (`Scripts`, no `bin`).

**Windows PowerShell.** Terminal 1:

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:MCP_TOKEN = "prueba-local"
uvicorn main:app --reload
```

Terminal 2:

```powershell
.venv\Scripts\Activate.ps1
$env:MCP_URL = "http://localhost:8000/mcp"
$env:MCP_TOKEN = "prueba-local"
python probar_mcp.py
```

`$env:` solo vale para esa ventana de PowerShell: si abres otra, hay que repetirlo. La última línea tiene que decir **Todo bien**.

## 6. En Render

En tu servicio del modelo: **Environment, Add Environment Variable**, `MCP_TOKEN` con un token de verdad (la parte 4 de `tu-mcp.md` dice cómo inventarlo). `RENDER_EXTERNAL_HOSTNAME` no la tocas: la pone Render y la plantilla la usa para no dar `421`. Commit, push, y cuando esté "live", abre `https://tu-servicio.onrender.com/mcp` en el navegador: tiene que decir `{"error":"Falta el token..."}`. Ese 401 quiere decir que está vivo y protegido.

## Qué está probado

El 25/11/2026, en macOS con Python 3.12, en un entorno nuevo con `fastapi==0.165.0`, `uvicorn==0.54.0` y este `requirements-mcp.txt`, montado en una API de prueba con un `/predict` falso y `buscar_X` contra la vista pública `pisos_publicados` de Pisos Madrid:

- `/mcp` sin token y con token malo: 401 con el mensaje; servidor sin `MCP_TOKEN`: 401 "El servidor no tiene token".
- `/health` y `/predict` sin token: 200 (la web de la sesión 3 no cambia).
- Con token: lista `buscar_X` y `predecir_Y`; `buscar_X` devuelve el total y las filas; `predecir_Y` llama a `/predict`; `probar_mcp.py` termina en "Todo bien".
- Errores que lee la IA: plantilla sin rellenar, modelo apagado, número fuera de límites, ninguna fila.
- Con `RENDER_EXTERNAL_HOSTNAME` puesta, ese nombre entra (200) y otro da 421.
- Clave secreta (`sb_secret_` o `service_role`): el servidor no arranca.
- Las tres trampas reproducidas: `mount` antes de las rutas (404 en `/health`), sin `lifespan` ("Task group is not initialized"), archivo `mcp.py` ("'mcp' is not a package").
- El prompt y el recurso comentados al final de `servidor_mcp.py` funcionan al quitarles el `#`.

**Sin probar:** en Render de verdad, en Windows y con Python 3.10 y 3.11.
