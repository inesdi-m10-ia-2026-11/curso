"""Carga tus textos en Supabase para el RAG (extra de la sesión 4, extra-rag.md).

Va en la carpeta rag/ del repo de tu app, con tus documentos en rag/textos/.
rag/textos/ va en el .gitignore: en el repo queda la lista DOCUMENTOS, con la URL
de cada original, no el PDF.

Qué hace, en orden:
  1. Lee los documentos de textos/ (.pdf, .txt o .md).
  2. Los trocea: unos 800 caracteres por trozo, con 150 de solape, cortando
     mejor en un final de párrafo o de frase que en mitad de una palabra.
     Un trozo de un PDF no mezcla dos páginas: así cada trozo sabe su página.
  3. Calcula el vector (embedding) de cada trozo con gemini-embedding-2, 768 dimensiones.
  4. Guarda cada trozo con su fuente, su página y su vector en la tabla trozos de
     Supabase (la de trozos.sql). Si vuelves a cargar un documento, primero borra
     sus trozos viejos: nunca hay duplicados.

Dos modos:
  python cargar_textos.py --probar    solo trocea y enseña cifras. No necesita ninguna clave.
  python cargar_textos.py             trocea, calcula los vectores y los sube.

Para el segundo hacen falta tres variables de entorno, SOLO en esta terminal (nunca en
un archivo, nunca en el repo):
  GEMINI_API_KEY        tu clave de Google AI Studio
  SUPABASE_URL          https://<tu-ref>.supabase.co
  SUPABASE_SECRET_KEY   una clave secreta (sb_secret_...) creada solo para esta carga.
                        Escribir necesita la secreta: la RLS no deja escribir a nadie más.
                        Al terminar, bórrala en Supabase (Project Settings, API Keys).

Dos trampas que este script ya evita (no las "arregles"):
  1. gemini-embedding-2 NO acepta task_type. La tarea va dentro del texto:
     "title: ... | text: ..." para los trozos y "task: question answering | query: ..."
     para las preguntas (lo hace tu MCP).
  2. Si a gemini-embedding-2 le pasas una lista de textos en una sola petición
     embedContent, devuelve UN vector para todos juntos. Por eso aquí se usa
     batchEmbedContents: una petición por trozo dentro del lote, un vector por trozo.

Probado el 26/11/2026 con Python 3.12: el troceo con PDF y Markdown de verdad, y el
resto contra servicios falsos que imitan Gemini y Supabase. Contra Gemini y Supabase
de verdad: sin probar.
"""
import os
import re
import sys
import time
from pathlib import Path

import httpx

# ======================================================================
# CAMBIA: tus documentos. Una entrada por archivo de textos/.
# "fuente" es como lo citarías en una presentación: título, quién lo publica y año.
# ======================================================================
DOCUMENTOS = {
    "mi-documento.pdf": {
        "fuente": "Título del documento, Organismo que lo publica (2025)",
        "url": "https://donde-se-lee-el-original",
        "licencia": "CC BY 4.0",
    },
}

CARPETA = Path(__file__).resolve().parent / "textos"
TAMANO = 800    # caracteres por trozo, más o menos
SOLAPE = 150    # caracteres que se repiten entre un trozo y el siguiente

# No cambies esto sin cambiarlo también en trozos.sql y en tu MCP.
MODELO = "gemini-embedding-2"
DIMENSIONES = 768
GEMINI = "https://generativelanguage.googleapis.com/v1beta/models"
POR_LOTE = 20   # trozos por petición a Gemini


# ---------- 1. Leer ----------

def leer(archivo: Path) -> list[tuple[int | None, str]]:
    """Devuelve [(página, texto)]. En .txt y .md, una sola "página" sin número."""
    if archivo.suffix.lower() == ".pdf":
        from pypdf import PdfReader  # solo hace falta si tienes PDF: pip install pypdf
        lector = PdfReader(str(archivo))
        return [(n, pagina.extract_text() or "") for n, pagina in enumerate(lector.pages, start=1)]
    return [(None, archivo.read_text(encoding="utf-8", errors="replace"))]


def limpiar(texto: str) -> str:
    texto = texto.replace("\r\n", "\n").replace("­", "")       # saltos de Windows y guiones invisibles
    texto = re.sub(r"(\w)-\n(\w)", r"\1\2", texto)                    # pala-\nbra cortada al final de línea
    texto = re.sub(r"[ \t ]+", " ", texto)                       # espacios repetidos
    texto = re.sub(r" *\n *", "\n", texto)
    texto = re.sub(r"\n{3,}", "\n\n", texto)                          # como mucho, una línea en blanco
    return texto.strip()


# ---------- 2. Trocear ----------

def trocear(texto: str, tamano: int = TAMANO, solape: int = SOLAPE) -> list[str]:
    """Trozos de unos `tamano` caracteres que se solapan `solape` caracteres.

    Corta, por orden de preferencia, en un final de párrafo, de frase, de línea o de
    palabra, siempre en la segunda mitad del trozo. Nunca devuelve trozos vacíos.
    """
    texto = limpiar(texto)
    trozos, inicio = [], 0
    while inicio < len(texto):
        fin = inicio + tamano
        if fin >= len(texto):
            fin = len(texto)
        else:
            minimo = inicio + tamano // 2
            for separador in ("\n\n", ". ", "? ", "! ", ".\n", "\n", "; ", ", ", " "):
                corte = texto.rfind(separador, minimo, fin)
                if corte != -1:
                    fin = corte + len(separador)
                    break
        trozo = texto[inicio:fin].strip()
        if trozo:
            trozos.append(trozo)
        if fin >= len(texto):
            break
        # El siguiente empieza `solape` caracteres antes, en el principio de una palabra.
        siguiente = max(fin - solape, inicio + 1)
        espacio = texto.find(" ", siguiente, fin)
        inicio = espacio + 1 if espacio != -1 else siguiente
    return trozos


def trocear_documento(archivo: Path) -> list[dict]:
    datos = DOCUMENTOS.get(archivo.name)
    if datos is None:
        print(f"  Aviso: {archivo.name} no está en DOCUMENTOS; uso el nombre del archivo como fuente.")
        datos = {"fuente": archivo.stem, "url": None, "licencia": None}
    filas = []
    for pagina, texto in leer(archivo):
        for trozo in trocear(texto):
            filas.append({
                "fuente": datos["fuente"],
                "pagina": pagina,
                "posicion": len(filas),
                "url": datos.get("url"),
                "licencia": datos.get("licencia"),
                "texto": trozo,
            })
    return filas


# ---------- 3. Vectores con Gemini ----------

def como_documento(fila: dict) -> str:
    """El formato que pide gemini-embedding-2 para lo que se va a buscar."""
    titulo = fila["fuente"] + (f", página {fila['pagina']}" if fila["pagina"] else "")
    return f"title: {titulo} | text: {fila['texto']}"


def vectores(textos: list[str], clave: str) -> list[list[float]]:
    """Un vector por texto, con batchEmbedContents. Si Gemini dice 429, espera y repite."""
    cuerpo = {"requests": [
        {"model": f"models/{MODELO}",
         "content": {"parts": [{"text": t}]},
         "output_dimensionality": DIMENSIONES}
        for t in textos
    ]}
    for intento in range(1, 6):
        try:
            r = httpx.post(f"{GEMINI}/{MODELO}:batchEmbedContents", json=cuerpo,
                           headers={"x-goog-api-key": clave}, timeout=120)
        except httpx.HTTPError as error:
            print(f"  Gemini no responde ({error}). Reintento {intento} de 5 en 20 segundos.")
            time.sleep(20)
            continue
        if r.status_code == 429:
            espera = 30 * intento
            print(f"  Gemini: demasiadas peticiones (429). Espero {espera} segundos (intento {intento} de 5).")
            time.sleep(espera)
            continue
        if r.status_code != 200:
            sys.exit(f"Gemini ha dado un error {r.status_code}: {r.text[:400]}")
        resultado = [e["values"] for e in r.json()["embeddings"]]
        if len(resultado) != len(textos):
            sys.exit(f"Gemini ha devuelto {len(resultado)} vectores para {len(textos)} trozos. Para aquí.")
        if any(len(v) != DIMENSIONES for v in resultado):
            sys.exit(f"Gemini ha devuelto vectores de {len(resultado[0])} dimensiones, no {DIMENSIONES}. "
                     "¿Falta output_dimensionality?")
        return resultado
    sys.exit("Gemini sigue diciendo 429 después de 5 intentos. Espera unos minutos y vuelve a ejecutar: "
             "los documentos ya subidos se vuelven a subir sin duplicarse.")


# ---------- 4. Subir a Supabase ----------

def rol_de_la_clave(clave: str) -> str:
    """'secreta', 'publicable' o 'desconocida'. Las claves antiguas (eyJ...) llevan el rol dentro."""
    if clave.startswith("sb_secret_"):
        return "secreta"
    if clave.startswith("sb_publishable_"):
        return "publicable"
    if clave.startswith("eyJ"):
        import base64, json
        try:
            cuerpo = clave.split(".")[1]
            rol = json.loads(base64.urlsafe_b64decode(cuerpo + "=" * (-len(cuerpo) % 4))).get("role")
        except Exception:
            return "desconocida"
        return {"service_role": "secreta", "anon": "publicable"}.get(rol, "desconocida")
    return "desconocida"


def subir(filas: list[dict], url: str, clave: str) -> None:
    cabeceras = {"apikey": clave, "Content-Type": "application/json", "Prefer": "return=minimal"}
    if clave.startswith("eyJ"):
        # Las claves antiguas (service_role) son un JWT y van también en Authorization.
        # Las nuevas (sb_secret_...) NO: solo en apikey.
        cabeceras["Authorization"] = f"Bearer {clave}"
    fuente = filas[0]["fuente"]
    r = httpx.delete(f"{url}/rest/v1/trozos", params={"fuente": f"eq.{fuente}"}, headers=cabeceras, timeout=60)
    if r.status_code not in (200, 204):
        sys.exit(f"Supabase no deja borrar los trozos viejos ({r.status_code}): {r.text[:400]}")
    for i in range(0, len(filas), 50):
        r = httpx.post(f"{url}/rest/v1/trozos", json=filas[i:i + 50], headers=cabeceras, timeout=60)
        if r.status_code not in (200, 201, 204):
            sys.exit(f"Supabase ha dado un error {r.status_code} al guardar: {r.text[:400]}")


# ---------- Todo junto ----------

def main() -> None:
    probar = "--probar" in sys.argv
    archivos = sorted(p for p in CARPETA.glob("*") if p.suffix.lower() in (".pdf", ".txt", ".md"))
    if not archivos:
        sys.exit(f"No hay documentos en {CARPETA}. Pon ahí tus .pdf, .txt o .md.")

    if not probar:
        clave_gemini = os.environ.get("GEMINI_API_KEY", "")
        url = os.environ.get("SUPABASE_URL", "").rstrip("/")
        clave_supabase = os.environ.get("SUPABASE_SECRET_KEY", "")
        if not (clave_gemini and url and clave_supabase):
            sys.exit("Faltan variables en esta terminal: GEMINI_API_KEY, SUPABASE_URL y SUPABASE_SECRET_KEY. "
                     "Para probar sin claves: python cargar_textos.py --probar")
        if not url.startswith("https://") and "127.0.0.1" not in url and "localhost" not in url:
            sys.exit("SUPABASE_URL tiene que ser la URL de tu proyecto: https://<tu-ref>.supabase.co")
        rol = rol_de_la_clave(clave_supabase)
        if rol == "publicable":
            sys.exit("SUPABASE_SECRET_KEY es la clave publicable. Para escribir hace falta una secreta "
                     "(sb_secret_...): la RLS no deja escribir con la publicable, y está bien que no deje.")
        if rol == "desconocida":
            sys.exit("SUPABASE_SECRET_KEY no parece una clave de Supabase: tiene que empezar por sb_secret_ "
                     "(o ser la service_role antigua, que empieza por eyJ). ¿Se ha copiado entera?")

    total = 0
    for archivo in archivos:
        filas = trocear_documento(archivo)
        if not filas:
            print(f"{archivo.name}: sin texto. Si es un PDF escaneado (fotos de páginas), no tiene texto que leer.")
            continue
        largos = [len(f["texto"]) for f in filas]
        print(f"{archivo.name}: {len(filas)} trozos, de {min(largos)} a {max(largos)} caracteres "
              f"(media {sum(largos) // len(largos)}). Fuente: {filas[0]['fuente']}")
        if probar:
            for f in filas[:2]:
                pagina = f"página {f['pagina']}, " if f["pagina"] else ""
                print(f"  [{pagina}trozo {f['posicion']}] {f['texto'][:200]!r}...")
            total += len(filas)
            continue
        for i in range(0, len(filas), POR_LOTE):
            lote = filas[i:i + POR_LOTE]
            for fila, vector in zip(lote, vectores([como_documento(f) for f in lote], clave_gemini)):
                fila["embedding"] = vector
            print(f"  vectores: {min(i + POR_LOTE, len(filas))} de {len(filas)}")
            time.sleep(1)  # sin prisa: el plan gratis tiene límite por minuto
        subir(filas, url, clave_supabase)
        print(f"  subidos {len(filas)} trozos a Supabase")
        total += len(filas)

    if probar:
        print(f"\nTotal: {total} trozos. Esto era una prueba: no se ha llamado a Gemini ni a Supabase.")
    else:
        print(f"\nTodo bien: {total} trozos en la tabla trozos. Compruébalo en Supabase (SQL Editor):\n"
              "  select fuente, count(*) from trozos group by fuente;\n"
              "Y ahora borra la clave secreta que has creado para esta carga (Project Settings, API Keys).")


if __name__ == "__main__":
    main()
