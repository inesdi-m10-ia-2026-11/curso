"""Tu servidor MCP (sesión 4). Plantilla: va en modelo/ del repo de tu app.

Dos herramientas para que un asistente de IA (Claude Code, Codex, OpenCode,
Antigravity, Gemini CLI...) use tu proyecto:

    buscar_X     lee filas de tu tabla (o vista) de Supabase
    predecir_Y   llama a tu propia API: el /predict de la sesión 3

No es un servicio aparte: main.py lo monta en /mcp, dentro de tu API del modelo.
Cómo, en README.md (cinco líneas en main.py).

Protección: un token en la variable de entorno MCP_TOKEN. El asistente lo manda
en la cabecera  Authorization: Bearer <tu token>.  Sin token, /mcp responde 401.

Qué cambias tú (o tu agente): todo lo que lleva la marca CAMBIA. El resto,
déjalo como está.

Las cuatro trampas que esta plantilla ya resuelve (no las "arregles"):
  1. La librería es mcp 2.x: la clase se llama MCPServer. FastMCP era la 1.x y
     aquí da "No module named 'mcp.server.fastmcp'". Tampoco instales el paquete
     fastmcp: es otra librería.
  2. Este archivo NO se puede llamar mcp.py: taparía la librería mcp.
  3. En Render, sin RENDER_EXTERNAL_HOSTNAME en allowed_hosts, todo da
     421 Misdirected Request. Render pone esa variable solo.
  4. En main.py, el MCP se monta al final (después de tus rutas) y su gestor
     de sesiones arranca en el lifespan. Si no: /predict desaparece, o
     "Task group is not initialized".
"""
import os
import secrets
from typing import Annotated, Literal

import httpx
from mcp.server.mcpserver import MCPServer  # trampa 1: MCPServer, no FastMCP
from mcp.server.mcpserver.exceptions import ToolError
from mcp.server.transport_security import TransportSecuritySettings
from pydantic import Field
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

# ======================================================================
# CAMBIA: tu Supabase. Los mismos dos valores que tu web/index.html.
# ======================================================================
# La clave PUBLICABLE (sb_publishable_... o, en proyectos antiguos, la "anon").
# Es pública por diseño: solo lee lo que la RLS deja leer a cualquiera.
# NUNCA la secreta (sb_secret_... o service_role): con ella el MCP se salta la RLS
# y cualquiera con tu token leería todo. Si la pones, el servidor no arranca.
SUPABASE_URL = "https://TU-PROYECTO.supabase.co"
SUPABASE_KEY = "sb_publishable_TU_CLAVE"

# CAMBIA: qué lee buscar_X.
TABLA = "tu_tabla"                      # tu tabla o vista, tal cual se llama en Supabase
COLUMNAS = "*"                          # las que devuelve, separadas por comas: "id,fecha,linea,viajeros"
COLUMNA_TEXTO = "tu_columna_de_texto"   # la que se filtra con texto: categoría, línea, distrito, país...
COLUMNA_NUMERO = "tu_columna_numero"    # la que se filtra con mínimo y máximo, y por la que se ordena

# La API de tu modelo. Por defecto, la de este mismo servicio: en local escucha
# en el puerto 8000 y en Render en $PORT. Solo si tu modelo está en otra URL,
# pon esa URL en la variable de entorno URL_MODELO.
URL_MODELO = os.environ.get("URL_MODELO") or f"http://127.0.0.1:{os.environ.get('PORT', '8000')}"

mcp = MCPServer(
    name="mi-proyecto",  # CAMBIA: el nombre de tu proyecto, en minúsculas y con guiones
    # CAMBIA: lo primero que lee la IA de tu servidor. Qué datos hay, de dónde
    # salen y de qué fechas; qué hace cada herramienta; y la regla de las cifras.
    instructions=(
        "<Qué datos hay, de dónde salen y de qué fechas.> "
        "Usa buscar_X para <...> y predecir_Y para <...>. "
        "No inventes cifras: sácalas de las herramientas."
    ),
)


# ---------- Ayudantes (no son herramientas: la IA no los ve) ----------

def _comprobar_configuracion() -> None:
    """Para con un mensaje claro si la plantilla sigue sin rellenar."""
    if "TU-PROYECTO" in SUPABASE_URL or "TU_CLAVE" in SUPABASE_KEY or TABLA == "tu_tabla":
        raise ToolError(
            "La plantilla está sin configurar: cambia SUPABASE_URL, SUPABASE_KEY y TABLA "
            "en servidor_mcp.py (los bloques marcados CAMBIA)."
        )


def _clave_secreta(clave: str) -> bool:
    """True si la clave de Supabase es secreta (sb_secret_ o una service_role antigua)."""
    if clave.startswith("sb_secret_"):
        return True
    if clave.startswith("eyJ"):  # las claves antiguas son un JWT: el rol va dentro
        import base64, json
        try:
            cuerpo = clave.split(".")[1]
            datos = json.loads(base64.urlsafe_b64decode(cuerpo + "=" * (-len(cuerpo) % 4)))
            return datos.get("role") == "service_role"
        except Exception:
            return False
    return False


if _clave_secreta(SUPABASE_KEY):
    raise RuntimeError(
        "SUPABASE_KEY es una clave SECRETA. El MCP solo puede usar la publicable "
        "(sb_publishable_... o anon). Cámbiala, y si ya la subiste a GitHub, "
        "genera otra en Supabase (Project Settings, API Keys)."
    )


def _numero(valor: float) -> str:
    """400000.0 se escribe 400000: una columna de enteros de Supabase no acepta el '.0'."""
    return str(int(valor)) if float(valor).is_integer() else str(valor)


def _leer_supabase(filtros: list[tuple[str, str]]) -> httpx.Response:
    """Lee TABLA por la API REST de Supabase y pide el total de filas que cumplen."""
    cabeceras = {"apikey": SUPABASE_KEY, "Prefer": "count=exact"}
    try:
        respuesta = httpx.get(f"{SUPABASE_URL}/rest/v1/{TABLA}", params=filtros, headers=cabeceras, timeout=20)
    except httpx.HTTPError as error:
        raise ToolError(f"No he podido conectar con Supabase ({error}). Prueba otra vez en un momento.")
    if respuesta.status_code not in (200, 206):  # 206: "te doy una parte de las filas", también vale
        # El texto de Supabase dice qué columna o qué tabla no existe: la IA lo puede leer.
        raise ToolError(f"Supabase ha dado un error {respuesta.status_code}: {respuesta.text[:300]}")
    return respuesta


# ---------- Las dos herramientas ----------
# La IA no lee tu código: lee el nombre de la herramienta, su docstring (el texto
# entre las tres comillas) y la descripción de cada parámetro. Eso es la interfaz.
# Escríbelos para alguien que no conoce tus datos.

@mcp.tool()
def buscar_X(  # CAMBIA el nombre: buscar_ventas, buscar_vuelos, buscar_viajes...
    texto: Annotated[
        str | None,
        Field(description="CAMBIA: qué es este texto, con dos o tres valores reales de ejemplo"),
    ] = None,
    minimo: Annotated[float | None, Field(description="CAMBIA: valor mínimo de <tu columna numérica>, en sus unidades")] = None,
    maximo: Annotated[float | None, Field(description="CAMBIA: valor máximo de <tu columna numérica>, en sus unidades")] = None,
    orden: Annotated[
        Literal["de_menor_a_mayor", "de_mayor_a_menor"],
        Field(description="Orden por <tu columna numérica>"),
    ] = "de_menor_a_mayor",
    limite: Annotated[int, Field(description="Cuántas filas devolver como mucho", ge=1, le=20)] = 10,
) -> dict:
    """CAMBIA: qué busca esta herramienta, en una frase, y en qué datos.

    CAMBIA: qué devuelve (cuántas filas cumplen en total y las primeras, con qué
    columnas) y para qué sirve después (por ejemplo: con esas columnas se puede
    llamar a predecir_Y).
    """
    _comprobar_configuracion()
    filtros = [
        ("select", COLUMNAS),
        ("order", f"{COLUMNA_NUMERO}.{'asc' if orden == 'de_menor_a_mayor' else 'desc'}"),
        ("limit", str(limite)),
    ]
    if texto:
        filtros.append((COLUMNA_TEXTO, f"ilike.*{texto}*"))  # contiene el texto, sin mirar mayúsculas
    if minimo is not None:
        filtros.append((COLUMNA_NUMERO, f"gte.{_numero(minimo)}"))
    if maximo is not None:
        filtros.append((COLUMNA_NUMERO, f"lte.{_numero(maximo)}"))

    respuesta = _leer_supabase(filtros)
    filas = respuesta.json()
    total = int(respuesta.headers.get("content-range", "*/0").split("/")[-1])  # "0-9/245" quiere decir 245
    resultado = {"encontradas": total, "mostradas": len(filas), "filas": filas}
    if total == 0:
        resultado["aviso"] = (
            "Ninguna fila cumple. Prueba sin algún filtro. Si la tabla tiene datos y aun así sale 0, "
            "la RLS no deja leerla sin login."
        )
    return resultado


@mcp.tool()
def predecir_Y(  # CAMBIA el nombre: predecir_viajeros, predecir_retraso, estimar_precio...
    # CAMBIA: un parámetro por cada campo que pide tu /predict (el modelo de Pydantic
    # de tu main.py), con el mismo nombre, el mismo tipo y los mismos límites, y una
    # descripción que entienda alguien que no ha visto tus datos.
    campo_numero: Annotated[float, Field(description="CAMBIA: qué es y en qué unidades", ge=0)],
    campo_texto: Annotated[str, Field(description="CAMBIA: qué es, con valores de ejemplo")],
) -> dict:
    """CAMBIA: qué predice tu modelo, en una frase, y cuándo usar esta herramienta.

    CAMBIA: cuánto se equivoca de media (está en tu metricas.json, en sus unidades)
    y cuándo no hay que fiarse de la predicción.
    """
    entrada = {"campo_numero": campo_numero, "campo_texto": campo_texto}  # CAMBIA: los mismos nombres
    try:
        respuesta = httpx.post(f"{URL_MODELO}/predict", json=entrada, timeout=90)  # Render gratis tarda en despertar
    except httpx.HTTPError:
        raise ToolError("La API del modelo no responde. Si está en Render gratis, puede estar despertando: prueba otra vez en un minuto.")
    if respuesta.status_code == 422:
        raise ToolError(f"El modelo no acepta estos datos: {respuesta.json().get('detail')}")
    if respuesta.status_code != 200:
        raise ToolError(f"La API del modelo ha dado un error {respuesta.status_code}. Prueba otra vez en un momento.")
    return {
        "entrada": entrada,
        "prediccion": respuesta.json(),  # lo que devuelve tu /predict, tal cual
        "aviso": "CAMBIA: unidades y qué no hay que creerse (por ejemplo: estimación con datos de 2023)",
    }


# ---------- Si vas por delante: un prompt y un recurso (escalón 6) ----------
# Quita el # del principio de cada línea para activarlos. Son de la librería 2.x.
#
# @mcp.prompt()
# def analiza(texto: str) -> str:
#     """Análisis guiado: busca, predice y resume en una tabla."""
#     return (f"Usa buscar_X con texto='{texto}'. Con la primera fila, llama a predecir_Y. "
#             "Responde con una tabla de tres filas y una frase de conclusión. Sin cifras inventadas.")
#
# @mcp.resource("info://datos")
# def sobre_los_datos() -> str:
#     """De dónde salen los datos, de qué fechas y con qué licencia."""
#     return "CAMBIA: fuente, fechas, licencia y qué columnas hay."


# ---------- El token y la aplicación web del MCP (no hace falta tocar nada) ----------

def error_de_token(cabecera: str | None) -> str | None:
    """Devuelve un mensaje si falta el token o no es el bueno; None si todo está bien."""
    token = os.environ.get("MCP_TOKEN", "")
    if not token:
        return "El servidor no tiene token: falta la variable de entorno MCP_TOKEN."
    if not cabecera:
        return "Falta el token. Manda la cabecera  Authorization: Bearer <tu token>."
    if not secrets.compare_digest(cabecera.encode(), f"Bearer {token}".encode()):
        return "El token no es correcto. Revisa la cabecera Authorization en la configuración de tu asistente."
    return None


class PideToken(BaseHTTPMiddleware):
    """Solo /mcp pide token: /health, /info y /predict siguen abiertos para tu web."""

    async def dispatch(self, request, call_next):
        if request.url.path.startswith("/mcp"):
            error = error_de_token(request.headers.get("authorization"))
            if error:
                return JSONResponse(status_code=401, content={"error": error})
        return await call_next(request)


app_mcp = mcp.streamable_http_app(
    stateless_http=True,  # sin sesiones en memoria: Render gratis se duerme y las perdería
    json_response=True,   # respuestas JSON normales, sin streaming
    # Trampa 3: qué nombres de servidor se aceptan. Tu ordenador y tu URL de Render
    # (Render pone RENDER_EXTERNAL_HOSTNAME solo). Sin esto, en Render: 421.
    transport_security=TransportSecuritySettings(
        allowed_hosts=["localhost:*", "127.0.0.1:*", os.environ.get("RENDER_EXTERNAL_HOSTNAME", "localhost")],
    ),
)
app_mcp.add_middleware(PideToken)
