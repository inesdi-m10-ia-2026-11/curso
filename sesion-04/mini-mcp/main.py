"""Tu mini MCP: la aplicación web que lo publica. No hace falta tocar nada aquí.

En local:   uvicorn main:app --reload
En Render:  uvicorn main:app --host 0.0.0.0 --port $PORT

GET /health  comprueba que está vivo (sin token; ábrela para despertar Render)
    /mcp     el servidor MCP (servidor_mcp.py). Pide el token de la variable de entorno
             MCP_TOKEN, de una de estas dos formas:
               - la cabecera  Authorization: Bearer <tu token>   (Claude Code, Codex, OpenCode...)
               - la URL       /mcp?token=<tu token>              (conectores de claude.ai, que no
                                                                  dejan poner cabeceras; el token
                                                                  queda en los logs de Render)
             Sin MCP_TOKEN en el servidor, /mcp no se abre a nadie.
"""
import os
import secrets
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from servidor_mcp import app_mcp, mcp


@asynccontextmanager
async def arranque(app):
    async with mcp.session_manager.run():  # el MCP necesita esto para atender en /mcp
        yield


app = FastAPI(title="Mini MCP", lifespan=arranque)


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/")
def inicio():
    return {"servicio": "mini MCP", "mcp": "/mcp (con token)", "salud": "/health"}


# ---------- El token: solo /mcp lo pide ----------

def error_de_token(cabecera: str | None) -> str | None:
    """Devuelve un mensaje si falta el token o no es el bueno; None si todo está bien."""
    token = os.environ.get("MCP_TOKEN", "")
    if not token:
        return "El servidor no tiene token: falta la variable de entorno MCP_TOKEN (en Render, en Environment)."
    if not cabecera:
        return "Falta el token. Manda la cabecera  Authorization: Bearer <tu token>."
    if not secrets.compare_digest(cabecera.encode(), f"Bearer {token}".encode()):
        return "El token no es correcto. Revisa la cabecera Authorization en la configuración de tu asistente."
    return None


@app.middleware("http")
async def pide_token_en_mcp(request, call_next):
    if request.url.path.startswith("/mcp"):
        cabecera = request.headers.get("authorization")
        if not cabecera and request.query_params.get("token"):
            cabecera = f"Bearer {request.query_params['token']}"  # .../mcp?token=... (conectores de claude.ai)
        error = error_de_token(cabecera)
        if error:
            return JSONResponse(status_code=401, content={"error": error})
    return await call_next(request)


app.mount("/", app_mcp)  # el MCP responde en /mcp. Va al final: si no, taparía /health
