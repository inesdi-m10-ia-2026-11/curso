"""Prueba tu servidor MCP sin asistente: lista tus herramientas y llama a cada una.

Va en modelo/, junto a servidor_mcp.py. Con el entorno activado y tu API
arrancada en otra terminal (uvicorn main:app --reload):

  Mac, Linux o Git Bash:
      MCP_URL=http://localhost:8000/mcp MCP_TOKEN=<tu token> python probar_mcp.py
  Windows PowerShell:
      $env:MCP_URL = "http://localhost:8000/mcp"
      $env:MCP_TOKEN = "<tu token>"
      python probar_mcp.py

Para probar el de Render, cambia MCP_URL por https://tu-servicio.onrender.com/mcp
y MCP_TOKEN por el de Render.

Si todo va bien, la última línea dice "Todo bien". Si no, dice qué ha fallado
y el programa termina con error (sirve para no hacer push si falla).
"""
import asyncio
import json
import os
import sys

import httpx2  # el cliente HTTP que usa la librería mcp
from mcp import Client
from mcp.client.streamable_http import streamable_http_client

URL = os.environ.get("MCP_URL", "http://localhost:8000/mcp")
TOKEN = os.environ.get("MCP_TOKEN", "")

# CAMBIA: una llamada de ejemplo a cada herramienta, con valores reales de tus datos.
# Los nombres tienen que ser los de tu servidor_mcp.py (si renombraste buscar_X, aquí también).
PRUEBAS = [
    ("buscar_X", {"texto": "<un valor real de tu columna de texto>", "limite": 3}),
    ("predecir_Y", {"campo_numero": 10, "campo_texto": "<un valor real>"}),
]


def comprobar_que_responde() -> None:
    """Antes de hablar MCP: ¿el servidor contesta y acepta el token? Da mensajes claros."""
    try:
        # Un POST vacío: si el token vale, el MCP contesta 400 (no es una petición MCP) y seguimos.
        # (Un GET con token no sirve: el MCP deja la conexión abierta esperando mensajes.)
        r = httpx2.post(URL, json={}, headers={"Authorization": f"Bearer {TOKEN}"}, timeout=120)
    except httpx2.HTTPError as error:
        sys.exit(f"No responde {URL} ({error}). ¿Está arrancada tu API? Si es Render gratis, "
                 'abre antes /health en el navegador y espera a ver {"ok":true}.')
    if r.status_code == 401:
        sys.exit(f"401: {r.json().get('error')}  (Compara el MCP_TOKEN de esta terminal con el del servidor.)")
    if r.status_code == 421:
        sys.exit("421: el MCP no acepta este nombre de servidor. Revisa allowed_hosts en servidor_mcp.py.")
    if r.status_code == 404:
        sys.exit("404: no hay nada en /mcp. ¿Has montado app_mcp al final de main.py? ¿La URL acaba en /mcp?")


async def main() -> None:
    if not TOKEN:
        sys.exit("Falta MCP_TOKEN en esta terminal (mira las instrucciones al principio de este archivo).")
    comprobar_que_responde()

    fallos = 0
    http = httpx2.AsyncClient(headers={"Authorization": f"Bearer {TOKEN}"}, timeout=120)
    async with Client(streamable_http_client(URL, http_client=http)) as cliente:
        herramientas = (await cliente.list_tools()).tools
        print(f"Conectado a {URL}. Herramientas: {[h.name for h in herramientas]}\n")
        for h in herramientas:  # lo mismo que lee la IA: nombre, descripción y parámetros
            print(f"- {h.name}: {((h.description or '').strip().splitlines() or ['(sin descripción)'])[0]}")
            for nombre, campo in h.input_schema.get("properties", {}).items():
                print(f"    {nombre}: {campo.get('description', '(sin descripción)')}")

        for herramienta, argumentos in PRUEBAS:
            print(f"\n>>> {herramienta}({json.dumps(argumentos, ensure_ascii=False)})")
            resultado = await cliente.call_tool(herramienta, argumentos)
            texto = resultado.content[0].text if resultado.content else ""
            if resultado.is_error:
                fallos += 1
                print("[ERROR]", texto)
            else:
                print("[ok]", texto[:1500])

    print("\nTodo bien." if fallos == 0 else f"\nAlgo falla: {fallos} herramienta(s) con error. No hagas push todavía.")
    sys.exit(1 if fallos else 0)


asyncio.run(main())
