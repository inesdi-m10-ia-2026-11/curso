# ---------- RAG: buscar_en_textos (extra de la sesión 4) ----------
#
# NO es un archivo para ejecutar: es un bloque para PEGAR en tu servidor_mcp.py,
# después de predecir_Y y antes del bloque "El token y la aplicación web del MCP".
# Usa lo que ya tiene la plantilla: os, httpx, Annotated, Field, ToolError, mcp,
# SUPABASE_URL, SUPABASE_KEY (la PUBLICABLE) y _comprobar_configuracion.
#
# Necesita una variable de entorno más en Render (Environment): GEMINI_API_KEY, tu
# clave de AI Studio. Sirve para calcular el vector de cada pregunta.
#
# Cambia también las instructions de MCPServer (más arriba): una frase con qué texto
# hay y cuándo usar buscar_en_textos y cuándo tus herramientas de datos.
#
# Probado el 26/11/2026 con mcp==2.3.0 y httpx==0.28.1, montado en la plantilla, contra
# servicios falsos que imitan Gemini y la API de Supabase (con un Postgres con pgvector
# y la RLS de trozos.sql). Contra Gemini y Supabase de verdad: sin probar.

GEMINI_EMBEDDINGS = "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-2:embedContent"
DIMENSIONES = 768  # las mismas que trozos.sql y cargar_textos.py


def _vector_de_la_pregunta(pregunta: str) -> list[float]:
    """El vector de la pregunta, con el mismo modelo y tamaño que los trozos."""
    clave = os.environ.get("GEMINI_API_KEY", "")
    if not clave:
        raise ToolError("El servidor no tiene GEMINI_API_KEY: añádela en Render (Environment) y espera al despliegue.")
    cuerpo = {
        "model": "models/gemini-embedding-2",
        # gemini-embedding-2 no tiene task_type: la tarea va dentro del texto.
        "content": {"parts": [{"text": f"task: question answering | query: {pregunta}"}]},
        "output_dimensionality": DIMENSIONES,
    }
    try:
        r = httpx.post(GEMINI_EMBEDDINGS, json=cuerpo, headers={"x-goog-api-key": clave}, timeout=30)
    except httpx.HTTPError as error:
        raise ToolError(f"No he podido conectar con Gemini ({error}). Prueba otra vez en un momento.")
    if r.status_code == 429:
        raise ToolError("Gemini dice que hay demasiadas peticiones (429). Espera un minuto y vuelve a preguntar.")
    if r.status_code != 200:
        raise ToolError(f"Gemini ha dado un error {r.status_code}: {r.text[:300]}")
    valores = r.json()["embedding"]["values"]
    if len(valores) != DIMENSIONES:
        raise ToolError(f"Gemini ha devuelto {len(valores)} dimensiones y la tabla espera {DIMENSIONES}.")
    return valores


@mcp.tool()
def buscar_en_textos(
    pregunta: Annotated[
        str,
        Field(description="La pregunta del usuario, entera y con sus palabras. "
                          "CAMBIA el ejemplo: '¿qué dice la guía sobre la fianza de un alquiler?'"),
    ],
    cuantos: Annotated[int, Field(description="Cuántos trozos devolver, del más parecido al menos", ge=1, le=10)] = 5,
) -> dict:
    """CAMBIA: Busca en <tus documentos: cuáles, de quién y de qué año> los trozos de texto que mejor responden a una pregunta.

    Úsala para lo que DICEN esos documentos: definiciones, normas, recomendaciones, explicaciones.
    NO la uses para cifras, filas, recuentos o predicciones de <tus datos>: para eso están buscar_X y predecir_Y.
    Devuelve los trozos más parecidos con su fuente y su página, y un "parecido" (más cerca de 1, más se parece).
    Responde solo con lo que digan los trozos y cita fuente y página. Si ninguno responde, dilo: no completes de memoria.
    """
    _comprobar_configuracion()
    vector = _vector_de_la_pregunta(pregunta)
    try:
        r = httpx.post(
            f"{SUPABASE_URL}/rest/v1/rpc/buscar_trozos",
            json={"pregunta_embedding": vector, "cuantos": cuantos},
            headers={"apikey": SUPABASE_KEY},  # la publicable: solo lee lo que la RLS deja leer
            timeout=20,
        )
    except httpx.HTTPError as error:
        raise ToolError(f"No he podido conectar con Supabase ({error}). Prueba otra vez en un momento.")
    if r.status_code != 200:
        raise ToolError(f"Supabase ha dado un error {r.status_code}: {r.text[:300]}")
    filas = r.json()
    if not filas:
        return {
            "pregunta": pregunta,
            "trozos": [],
            "aviso": "No ha salido ningún trozo. Si la tabla trozos tiene filas, la RLS no deja leerla sin "
                     "login: revisa el paso 4 de trozos.sql.",
        }
    return {
        "pregunta": pregunta,
        "trozos": [
            {
                "fuente": f["fuente"],
                "pagina": f["pagina"],
                "texto": f["texto"],
                "parecido": round(f["parecido"], 3),
                "url": f["url"],
            }
            for f in filas
        ],
        "como_citar": "(fuente, página). Si el parecido del primer trozo es bajo, probablemente el texto no lo dice.",
    }
