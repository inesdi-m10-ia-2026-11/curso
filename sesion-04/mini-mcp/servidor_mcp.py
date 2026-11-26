"""Tu mini MCP (sesión 4): un servidor MCP pequeño, tuyo, con datos en directo.

Trae UNA herramienta de ejemplo:
    tiempo_en(ciudad)   el tiempo de ahora en cualquier ciudad del mundo (sin clave)
Tú añades la tuya en el bloque "CAMBIA: TU HERRAMIENTA", con una API pública sin clave.

main.py lo monta en /mcp y le pone delante el token (MCP_TOKEN).

Tres trampas que esta base ya resuelve (no las "arregles"):
  1. Es mcp 2.x: la clase se llama MCPServer. FastMCP era la 1.x y aquí da
     "No module named 'mcp.server.fastmcp'". Tampoco instales el paquete fastmcp.
  2. Este archivo NO se puede llamar mcp.py: taparía la librería mcp.
  3. En Render, sin RENDER_EXTERNAL_HOSTNAME en allowed_hosts, todo da
     421 Misdirected Request. Render pone esa variable sola.

Lo que lleva CAMBIA lo cambias tú (o tu agente). El resto, déjalo como está.
"""
import os
import time
import unicodedata
from datetime import datetime
from typing import Annotated
from zoneinfo import ZoneInfo

import httpx
from mcp.server.mcpserver import MCPServer  # trampa 1: MCPServer, no FastMCP
from mcp.server.mcpserver.exceptions import ToolError
from mcp.server.transport_security import TransportSecuritySettings
from mcp.types import ToolAnnotations
from pydantic import Field

SOLO_LEER = ToolAnnotations(read_only_hint=True, open_world_hint=True)  # no cambia nada; lee de internet

# CAMBIA: quién llama, con el nombre de tu mini MCP. Algunas APIs (MET Norway,
# Wikipedia, Open Food Facts) rechazan a quien no dice quién es.
CABECERAS = {"User-Agent": "mini-mcp/1.0 (ejemplo de un curso; https://github.com/inesdi-m10-ia-2026-11/curso)"}

mcp = MCPServer(
    name="mini-mcp",  # CAMBIA: el nombre de tu mini MCP, en minúsculas y con guiones
    # CAMBIA: lo primero que lee la IA de tu servidor. Qué herramientas hay, para
    # qué sirve cada una y la regla de las cifras. Añade la tuya.
    instructions=(
        "Datos en directo: el tiempo de ahora en cualquier ciudad del mundo (tiempo_en). "
        "Para cualquier dato del tiempo, usa la herramienta: no lo inventes ni lo recuerdes."
    ),
)


# ---------- Ayudantes (no son herramientas: la IA no los ve) ----------

def _pedir(url: str, params: dict, quien: str) -> dict | list:
    """Llama a una API pública y devuelve su JSON, o un ToolError que la IA entiende."""
    try:
        respuesta = httpx.get(url, params=params, headers=CABECERAS, timeout=20, follow_redirects=True)
    except httpx.HTTPError:
        raise ToolError(f"{quien} no responde. Prueba otra vez en un minuto.")
    if respuesta.status_code == 429:
        raise ToolError(
            f"{quien} dice que le llegan demasiadas peticiones (error 429). "
            "Espera un minuto y prueba otra vez."
        )
    if respuesta.status_code >= 500:
        raise ToolError(
            f"{quien} falla ahora mismo (error {respuesta.status_code}). "
            "Prueba otra vez en un minuto; si sigue fallando, su servicio está caído."
        )
    if respuesta.status_code >= 400:  # 400, 404...: casi siempre, un dato que la API no reconoce
        raise ToolError(
            f"{quien} no reconoce lo que le hemos pedido (error {respuesta.status_code}). "
            f"Revisa estos datos y prueba con otros: {params}"
        )
    try:
        return respuesta.json()
    except ValueError:
        raise ToolError(f"{quien} no ha devuelto JSON. Prueba otra vez en un minuto.")


def _comparable(texto: str) -> str:
    """'México' y 'mexico' se comparan igual: sin acentos, sin mayúsculas."""
    sin_acentos = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return sin_acentos.strip().lower()


_ciudades: dict[str, tuple[dict, list[str]]] = {}  # una ciudad no se mueve: se busca una vez
_tiempo: dict[str, tuple[float, dict]] = {}        # el tiempo de una ciudad se guarda 10 minutos


def _buscar_ciudad(texto: str) -> tuple[dict, list[str]]:
    """'Lima' o 'Valencia, Venezuela' pasan a coordenadas, con el buscador de Open-Meteo.

    Devuelve la ciudad elegida (la más poblada con ese nombre) y, si no se dijo el
    país, las otras que se llaman igual, para que la IA pueda avisar.
    """
    clave = _comparable(texto)
    if clave in _ciudades:
        return _ciudades[clave]
    nombre, coma, pais = texto.rpartition(",")
    if not coma:  # sin coma: todo es el nombre de la ciudad
        nombre, pais = pais, ""
    datos = _pedir(
        "https://geocoding-api.open-meteo.com/v1/search",
        {"name": nombre.strip(), "count": 10, "language": "es"},
        "El buscador de ciudades de Open-Meteo",
    )
    sitios = datos.get("results") or []
    if pais.strip():  # 'Valencia, Venezuela', 'Valencia, VE' o 'Springfield, Illinois'
        buscado = _comparable(pais)
        sitios = [s for s in sitios if buscado in (
            _comparable(s.get("country") or ""), _comparable(s.get("country_code") or ""),
            _comparable(s.get("admin1") or ""),
        )]
    if not sitios:
        raise ToolError(
            f"No encuentro la ciudad '{texto}'. Escribe solo el nombre de la ciudad, sin calle ni código "
            "postal (por ejemplo Bogotá o Lima). Si es una ciudad pequeña o el nombre se repite, añade el "
            "país después de una coma: 'Valencia, Venezuela'."
        )
    mismo_nombre = {_comparable(nombre), _comparable(sitios[0]["name"])}
    otras = [] if pais.strip() else [  # las que se llaman igual y tienen más de 50.000 habitantes
        f"{s['name']} ({', '.join(x for x in (s.get('admin1'), s.get('country')) if x)})"
        for s in sitios[1:] if (s.get("population") or 0) >= 50_000 and _comparable(s["name"]) in mismo_nombre
    ][:3]
    _ciudades[clave] = (sitios[0], otras)
    return _ciudades[clave]


CIELO = [  # el principio del symbol_code de MET Norway, en palabras
    ("clearsky", "despejado"), ("fair", "casi despejado"), ("partlycloudy", "parcialmente nublado"),
    ("cloudy", "nublado"), ("fog", "niebla"), ("lightrainshowers", "chubascos ligeros"),
    ("heavyrainshowers", "chubascos fuertes"), ("rainshowers", "chubascos"), ("lightrain", "lluvia ligera"),
    ("heavyrain", "lluvia fuerte"), ("rain", "lluvia"), ("lightsleet", "aguanieve ligera"),
    ("sleet", "aguanieve"), ("lightsnow", "nieve ligera"), ("heavysnow", "nieve fuerte"),
    ("snow", "nieve"), ("thunder", "tormenta"),
]


def _hora_local(instante_utc: str, zona: str | None) -> str:
    """'2026-11-26T20:00:00Z' pasa a '15:00' en la hora de la ciudad."""
    momento = datetime.fromisoformat(instante_utc.replace("Z", "+00:00"))
    try:
        return momento.astimezone(ZoneInfo(zona or "UTC")).strftime("%H:%M")
    except Exception:  # zona desconocida: mejor la hora UTC que un error
        return momento.strftime("%H:%M UTC")


# ---------- La herramienta de ejemplo ----------
# La IA no lee tu código: lee el nombre de la herramienta, su docstring (el texto
# entre las tres comillas) y la descripción de cada parámetro. Eso es la interfaz.

@mcp.tool(annotations=SOLO_LEER)
def tiempo_en(
    ciudad: Annotated[str, Field(
        description="Ciudad de cualquier país, por ejemplo Bogotá, Quito o Lima. Si el nombre se repite "
                    "en varios países, añade el país después de una coma: 'Valencia, Venezuela'",
        min_length=2, max_length=80,
    )],
) -> dict:
    """El tiempo que hace AHORA MISMO en una ciudad de cualquier país: temperatura, cielo,
    lluvia prevista para la próxima hora, viento y humedad, con la hora local del dato.

    Úsala para cualquier pregunta sobre el tiempo de este momento ("¿hace calor en Lima?",
    "¿llueve en Quito?", "¿qué tiempo hace en mi ciudad?"). No da previsiones de otros días.
    Si devuelve otras_ciudades_con_ese_nombre y el usuario hablaba de otra, llámala otra vez
    con el país: 'Valencia, Venezuela'. Datos de MET Norway, el servicio meteorológico de
    Noruega, que cubre todo el mundo y se actualiza cada hora.
    """
    sitio, otras = _buscar_ciudad(ciudad)
    clave = f"{sitio['latitude']:.4f},{sitio['longitude']:.4f}"
    guardado = _tiempo.get(clave)
    if guardado and time.time() - guardado[0] < 600:  # MET Norway pide no repetir la misma consulta
        return guardado[1]

    datos = _pedir(
        "https://api.met.no/weatherapi/locationforecast/2.0/compact",
        {"lat": round(sitio["latitude"], 4), "lon": round(sitio["longitude"], 4)},  # 4 decimales, como pide
        "La API del tiempo de MET Norway",
    )
    serie = datos["properties"]["timeseries"][0]  # la hora en curso
    ahora = serie["data"]["instant"]["details"]
    proxima_hora = serie["data"].get("next_1_hours", {})
    simbolo = proxima_hora.get("summary", {}).get("symbol_code", "")

    resultado = {
        "ciudad": sitio["name"],
        "region": sitio.get("admin1"),
        "pais": sitio.get("country"),
        "hora_local_del_dato": _hora_local(serie["time"], sitio.get("timezone")),
        "temperatura_c": ahora["air_temperature"],
        "cielo": next((texto for codigo, texto in CIELO if simbolo.startswith(codigo)), simbolo or "sin dato"),
        "lluvia_proxima_hora_mm": proxima_hora.get("details", {}).get("precipitation_amount"),
        "viento_kmh": round(ahora["wind_speed"] * 3.6, 1),  # MET Norway lo da en m/s
        "humedad_pct": round(ahora["relative_humidity"]),
        "es_de_noche": simbolo.endswith("_night"),
        "fuente": "MET Norway (api.met.no); la ciudad, del buscador de Open-Meteo",
    }
    if otras:
        resultado["otras_ciudades_con_ese_nombre"] = otras
    _tiempo[clave] = (time.time(), resultado)
    return resultado


# ======================================================================
# CAMBIA: TU HERRAMIENTA. Copia este molde aquí debajo, quítale los # y rellénalo.
#   1. La URL de tu API y sus parámetros, probados antes en el navegador.
#   2. El nombre: un verbo o una pregunta con su cosa (festivos_de, cambio_de_moneda,
#      buscar_libro). En minúsculas y con _.
#   3. La descripción de cada parámetro y el docstring, para alguien que no ve tu código.
#   4. Lo que devuelves: pocos campos, con nombres claros, y la fuente.
#   5. Un ToolError en español que diga qué hacer cuando no hay resultado.
#   6. Una llamada en PRUEBAS de probar.py.
# Si tu API necesita un número, usa int o float en lugar de str, con ge= y le= si tiene límites.
# ======================================================================
#
# @mcp.tool(annotations=SOLO_LEER)
# def mi_herramienta(
#     consulta: Annotated[str, Field(
#         description="CAMBIA: qué es este dato, con dos o tres ejemplos reales",
#         min_length=1, max_length=80,
#     )],
# ) -> dict:
#     """CAMBIA: qué da, en una frase, y de dónde sale.
#
#     CAMBIA: cuándo usarla, con dos preguntas de ejemplo con las palabras de un usuario,
#     y qué NO da.
#     """
#     datos = _pedir("https://CAMBIA-la-url-de-tu-api", {"CAMBIA": consulta}, "CAMBIA: el nombre de tu API")
#     if not datos:
#         raise ToolError(f"No encuentro '{consulta}'. CAMBIA: qué puede escribir en su lugar, con un ejemplo.")
#     return {"CAMBIA": datos, "fuente": "CAMBIA: el nombre de tu API"}


# ---------- La aplicación web del MCP (main.py la monta y le pone el token) ----------

app_mcp = mcp.streamable_http_app(
    stateless_http=True,  # sin sesiones en memoria: Render gratis se duerme y las perdería
    json_response=True,   # respuestas JSON normales, sin streaming
    # Trampa 3: qué nombres de servidor se aceptan. Tu ordenador y tu URL de Render
    # (Render pone RENDER_EXTERNAL_HOSTNAME sola). Sin esto, en Render: 421.
    transport_security=TransportSecuritySettings(
        allowed_hosts=["localhost:*", "127.0.0.1:*", os.environ.get("RENDER_EXTERNAL_HOSTNAME", "localhost")],
    ),
)
