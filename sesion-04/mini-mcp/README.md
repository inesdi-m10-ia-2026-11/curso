# Tu mini MCP

Un servidor MCP pequeño y tuyo, con datos en directo, como "Madrid ahora" pero para tu ciudad o para un caso de uso tuyo. Trae una herramienta de ejemplo, `tiempo_en(ciudad)`, el tiempo de ahora en cualquier ciudad del mundo, y un molde para que añadas la tuya con una API pública sin clave. Se publica como un servicio nuevo de Render, aparte de tu modelo.

Los pasos para la clase están en la guía de la sesión 4 (`tu-mcp.md`, "Primero, tu mini MCP"), con la lista de APIs recomendadas.

| Archivo | Qué hace | ¿Lo tocas? |
|---|---|---|
| `servidor_mcp.py` | Las herramientas. `tiempo_en` y el molde de la tuya | Sí: todo lo marcado `CAMBIA` |
| `probar.py` | Lista las herramientas y llama a cada una; acaba en "Todo bien" | Sí: la lista `PRUEBAS` |
| `main.py` | La aplicación web: `/health`, y el MCP en `/mcp` con token | No |
| `requirements.txt` | Las versiones exactas probadas (`mcp==2.3.0`) | No |
| `render.yaml` | Los valores de Render, por si usas "New, Blueprint" | Solo el nombre |

## Las reglas que no se tocan

- La librería es `mcp==2.3.0` y la clase es `MCPServer`. `FastMCP` era la versión 1.x: no la uses, ni instales el paquete `fastmcp`.
- Ningún archivo se llama `mcp.py`: taparía la librería.
- El token nunca va al repo: vive en la variable de entorno `MCP_TOKEN` (en Render, en Environment). Sin ella, `/mcp` no se abre a nadie.
- `/mcp` acepta el token en la cabecera `Authorization: Bearer <tu token>` o, para los conectores de claude.ai, en la URL: `/mcp?token=<tu token>`. La URL con token queda en los logs de Render: úsala solo si tu cliente no deja poner cabeceras.

## Probarlo en local

Python 3.10 o más. Dos terminales, en esta carpeta. En local, el token puede ser cualquier palabra.

**Mac, Linux o Git Bash.** Terminal 1:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export MCP_TOKEN=prueba-local
uvicorn main:app --reload
```

Terminal 2:

```bash
source .venv/bin/activate
MCP_URL=http://localhost:8000/mcp MCP_TOKEN=prueba-local python probar.py
```

En Git Bash en Windows: `py -m venv .venv` y `source .venv/Scripts/activate` (`Scripts`, no `bin`).

**Windows PowerShell.** Terminal 1:

```powershell
py -m venv .venv
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
python probar.py
```

Si PowerShell dice "running scripts is disabled": `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` y vuelve a activar el entorno.

## Tu herramienta

En `servidor_mcp.py`, el bloque `CAMBIA: TU HERRAMIENTA` trae un molde comentado y seis pasos. Lo que más importa es la descripción: la IA no lee tu código, lee el nombre de la herramienta, su docstring y la descripción de cada parámetro. Llama a tu API con `_pedir`, que ya manda un User-Agent (Wikipedia, MET Norway y Open Food Facts lo exigen) y convierte los errores de la API en mensajes que la IA entiende.

## Lo que se aprendió el 26/11/2026

- Desde Render gratis, la previsión de Open-Meteo (`api.open-meteo.com`) responde **429**: la IP de Render es compartida. Por eso `tiempo_en` saca el tiempo de MET Norway (`api.met.no`), que funcionó desde Render, y de Open-Meteo solo usa el buscador de ciudades (`geocoding-api.open-meteo.com`), que también funcionó.
- Si tu API responde en tu ordenador y desde Render da 429, es lo mismo: guarda las respuestas unos minutos (como hace `tiempo_en`) o elige otra API.
