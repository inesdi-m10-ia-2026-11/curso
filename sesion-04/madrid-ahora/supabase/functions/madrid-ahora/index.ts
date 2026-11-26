// Madrid ahora, versión Supabase: el mismo MCP en una Edge Function, con el login de Supabase.
//
// Diferencia con la versión de Render (Python, token fijo):
//   - Aquí no hay un token para toda la clase: cada persona inicia sesión con su cuenta
//     (OAuth 2.1 de Supabase Auth) y cada llamada a una herramienta va como esa persona.
//   - Por eso hay dos herramientas con datos de cada uno: guardar_lugar y mis_lugares.
//     La tabla lugares_favoritos tiene RLS: cada usuario ve solo sus filas, también a través del MCP.
//
// Piezas (las mismas que la guía oficial, https://supabase.com/docs/guides/ai-tools/byo-mcp):
//   withOAuthProtectedResource  dice al cliente dónde iniciar sesión (401 con WWW-Authenticate)
//   withSupabase({auth:'user'})  comprueba el token del usuario y da un cliente con su RLS
//   el manejador MCP             las herramientas
//
// Versiones fijadas el 25/11/2026 (las que se probaron en local).
import 'jsr:@supabase/functions-js@2.108.2/edge-runtime.d.ts'

import { createMcpHandler, McpServer } from 'npm:@modelcontextprotocol/server@2.4.0'
import type { CallToolResult } from 'npm:@modelcontextprotocol/server@2.4.0'
import { pipeline } from 'npm:@supabase/middleware@1.0.0'
import { withOAuthProtectedResource, withSupabase, type SupabaseContext } from 'npm:@supabase/server@1.9.2'
import { z } from 'npm:zod@4.6.7'

// Para que un cliente que corre en el navegador (MCP Inspector) pueda llamar.
const CORS: Record<string, string> = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, DELETE, OPTIONS',
  'Access-Control-Allow-Headers':
    'Authorization, Content-Type, Accept, Mcp-Protocol-Version, Mcp-Session-Id, Mcp-Method, Mcp-Name',
  'Access-Control-Expose-Headers': 'WWW-Authenticate, Mcp-Session-Id',
}

const SOLO_LEER = { readOnlyHint: true, destructiveHint: false, openWorldHint: true }

const CIELO: Record<number, string> = {
  0: 'despejado', 1: 'casi despejado', 2: 'parcialmente nuboso', 3: 'cubierto',
  45: 'niebla', 48: 'niebla con escarcha',
  51: 'llovizna débil', 53: 'llovizna', 55: 'llovizna intensa', 56: 'llovizna helada', 57: 'llovizna helada intensa',
  61: 'lluvia débil', 63: 'lluvia', 65: 'lluvia fuerte', 66: 'lluvia helada', 67: 'lluvia helada fuerte',
  71: 'nieve débil', 73: 'nieve', 75: 'nieve fuerte', 77: 'granos de nieve',
  80: 'chubascos débiles', 81: 'chubascos', 82: 'chubascos fuertes', 85: 'chubascos de nieve', 86: 'chubascos de nieve fuertes',
  95: 'tormenta', 96: 'tormenta con granizo', 99: 'tormenta con granizo fuerte',
}

// ---------- Ayudantes (no son herramientas: la IA no los ve) ----------

class ErrorParaLaIA extends Error {}

function texto(valor: unknown): CallToolResult {
  return { content: [{ type: 'text', text: JSON.stringify(valor, null, 2) }] }
}

function error(mensaje: string): CallToolResult {
  return { isError: true, content: [{ type: 'text', text: mensaje }] }
}

// Envuelve una herramienta: los errores pensados para la IA le llegan tal cual; los demás, con un aviso.
function protegida<A>(fn: (args: A) => Promise<CallToolResult>) {
  return async (args: A): Promise<CallToolResult> => {
    try {
      return await fn(args)
    } catch (e) {
      if (e instanceof ErrorParaLaIA) return error(e.message)
      console.error(e)
      return error('Ha fallado algo dentro del servidor. Prueba otra vez; si se repite, avisa a quien lo mantiene.')
    }
  }
}

async function pedir(url: string, params: Record<string, string | number>, quien: string) {
  const direccion = new URL(url)
  for (const [clave, valor] of Object.entries(params)) direccion.searchParams.set(clave, String(valor))
  let respuesta: Response
  try {
    respuesta = await fetch(direccion, { signal: AbortSignal.timeout(20_000) })
  } catch {
    throw new ErrorParaLaIA(`${quien} no responde. Prueba otra vez en un minuto.`)
  }
  if (!respuesta.ok) {
    throw new ErrorParaLaIA(
      `${quien} ha respondido con un error ${respuesta.status}. Prueba otra vez en un minuto; si sigue fallando, su servicio está caído.`
    )
  }
  return await respuesta.json()
}

type Sitio = { name: string; latitude: number; longitude: number; admin1?: string; admin2?: string }

async function buscarLugar(lugar: string): Promise<Sitio> {
  const datos = await pedir(
    'https://geocoding-api.open-meteo.com/v1/search',
    { name: lugar.trim(), count: 1, language: 'es', countryCode: 'ES' },
    'El buscador de lugares de Open-Meteo'
  )
  if (!datos.results?.length) {
    throw new ErrorParaLaIA(
      `No encuentro '${lugar}' en España. Escribe el nombre de un municipio o de un barrio de España, ` +
        'sin la calle ni el código postal; por ejemplo Madrid, Getafe o Chamberí.'
    )
  }
  return datos.results[0]
}

async function tiempoEn(sitio: Sitio) {
  const datos = await pedir(
    'https://api.open-meteo.com/v1/forecast',
    {
      latitude: sitio.latitude, longitude: sitio.longitude, timezone: 'Europe/Madrid',
      current: 'temperature_2m,apparent_temperature,relative_humidity_2m,precipitation,weather_code,wind_speed_10m,is_day',
    },
    'La API del tiempo de Open-Meteo'
  )
  const ahora = datos.current
  return {
    lugar: sitio.name,
    provincia: sitio.admin2 ?? sitio.admin1 ?? null,
    medido_a_las: String(ahora.time).slice(11, 16),
    temperatura_c: ahora.temperature_2m,
    sensacion_termica_c: ahora.apparent_temperature,
    cielo: CIELO[ahora.weather_code] ?? `código WMO ${ahora.weather_code}`,
    lluvia_mm: ahora.precipitation,
    viento_kmh: ahora.wind_speed_10m,
    humedad_pct: ahora.relative_humidity_2m,
    es_de_dia: Boolean(ahora.is_day),
    fuente: 'Open-Meteo',
  }
}

function ahoraEnMadrid() {
  const partes = Object.fromEntries(
    new Intl.DateTimeFormat('en-CA', {
      timeZone: 'Europe/Madrid', year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', hourCycle: 'h23',
    }).formatToParts(new Date()).map((p) => [p.type, p.value])
  )
  return { fecha: `${partes.year}-${partes.month}-${partes.day}`, hora: `${partes.hour}:00` }
}

const tramo = (hora: string) => `${hora} a ${String((Number(hora.slice(0, 2)) + 1) % 24).padStart(2, '0')}:00`

const LUGAR = z.string().min(2).max(80)
  .describe('Municipio o barrio de España, por ejemplo Madrid, Getafe, Chamberí o Sevilla')

// ---------- El servidor: uno nuevo en cada petición, atado a quien llama ----------

function crearServidor(ctx: SupabaseContext): McpServer {
  const supabase = ctx.supabase
  const usuario = ctx.userClaims!

  const server = new McpServer(
    { name: 'madrid-ahora', version: '1.0.0' },
    {
      instructions:
        'Datos en directo de España (el tiempo de ahora y el precio de la luz de hoy) y los lugares ' +
        'favoritos de la persona que ha iniciado sesión. Para cualquier cifra, usa las herramientas: ' +
        'no la inventes. Las horas son las de Madrid.',
    }
  )

  server.registerTool(
    'tiempo_ahora',
    {
      description:
        'El tiempo que hace AHORA MISMO en un lugar de España: temperatura, sensación térmica, lluvia, ' +
        'viento, humedad y cómo está el cielo. Úsala para cualquier pregunta sobre el tiempo de este ' +
        'momento. No da previsiones de mañana. Datos de Open-Meteo, cada 15 minutos.',
      inputSchema: z.object({ lugar: LUGAR }),
      annotations: SOLO_LEER,
    },
    protegida(async ({ lugar }: { lugar: string }) => texto(await tiempoEn(await buscarLugar(lugar))))
  )

  server.registerTool(
    'precio_luz_hoy',
    {
      description:
        'El precio de la luz de HOY en España, hora a hora, en euros por kWh: el de la hora actual, las ' +
        'tres horas más baratas, la más cara y la media del día. Es el PVPC de Red Eléctrica (península), ' +
        'con peajes y cargos y sin impuestos. Úsala para "¿cuánto cuesta la luz ahora?" o "¿a qué hora ' +
        'pongo la lavadora?". Solo da el día de hoy.',
      inputSchema: z.object({}),
      annotations: SOLO_LEER,
    },
    protegida(async () => {
      const { fecha, hora } = ahoraEnMadrid()
      const datos = await pedir(
        'https://apidatos.ree.es/es/datos/mercados/precios-mercados-tiempo-real',
        { start_date: `${fecha}T00:00`, end_date: `${fecha}T23:59`, time_trunc: 'hour' },
        'La API de Red Eléctrica'
      )
      const pvpc = (datos.included ?? []).find((serie: { type: string }) => serie.type === 'PVPC')
      if (!pvpc?.attributes?.values?.length) {
        throw new ErrorParaLaIA('Red Eléctrica no ha publicado todavía los precios de hoy. Prueba otra vez más tarde.')
      }
      const horas = pvpc.attributes.values.map((v: { datetime: string; value: number }) => ({
        hora: v.datetime.slice(11, 16),
        eur_kwh: Math.round(v.value * 10) / 10_000, // €/MWh a €/kWh, cuatro decimales
      }))
      const ahora = horas.find((h: { hora: string }) => h.hora === hora)
      const baratas = [...horas].sort((a, b) => a.eur_kwh - b.eur_kwh).slice(0, 3)
      const cara = [...horas].sort((a, b) => b.eur_kwh - a.eur_kwh)[0]
      const media = horas.reduce((suma: number, h: { eur_kwh: number }) => suma + h.eur_kwh, 0) / horas.length
      return texto({
        fecha,
        hora_actual: tramo(hora),
        precio_ahora_eur_kwh: ahora?.eur_kwh ?? null,
        tres_horas_mas_baratas: baratas.map((h) => ({ tramo: tramo(h.hora), eur_kwh: h.eur_kwh })),
        hora_mas_cara: { tramo: tramo(cara.hora), eur_kwh: cara.eur_kwh },
        media_del_dia_eur_kwh: Math.round(media * 10_000) / 10_000,
        por_horas: Object.fromEntries(horas.map((h: { hora: string; eur_kwh: number }) => [h.hora, h.eur_kwh])),
        tarifa: 'PVPC 2.0TD (península), con peajes y cargos, sin impuestos',
        fuente: 'Red Eléctrica (apidatos.ree.es)',
      })
    })
  )

  // ---------- Lo de cada usuario: aquí es donde el login importa ----------

  server.registerTool(
    'guardar_lugar',
    {
      description:
        'Guarda un lugar de España en los lugares favoritos de la persona que ha iniciado sesión. ' +
        'Úsala cuando diga "guarda Getafe" o "apunta mis sitios". Comprueba que el lugar existe antes de guardarlo.',
      inputSchema: z.object({ lugar: LUGAR }),
      annotations: { readOnlyHint: false, destructiveHint: false, idempotentHint: true, openWorldHint: true },
    },
    protegida(async ({ lugar }: { lugar: string }) => {
      const sitio = await buscarLugar(lugar)
      // Sin user_id: la tabla lo rellena con auth.uid(), el de quien llama.
      const { error: fallo } = await supabase.from('lugares_favoritos').insert({ nombre: sitio.name })
      if (fallo?.code === '23505') return texto({ guardado: false, motivo: `Ya tenías guardado ${sitio.name}` })
      if (fallo) throw new ErrorParaLaIA(`No he podido guardar el lugar: ${fallo.message}`)
      return texto({ guardado: true, lugar: sitio.name, provincia: sitio.admin2 ?? sitio.admin1 ?? null })
    })
  )

  server.registerTool(
    'mis_lugares',
    {
      description:
        'Los lugares favoritos de la persona que ha iniciado sesión, cada uno con el tiempo de ahora. ' +
        'Úsala para "¿qué tiempo hace en mis sitios?" o "¿qué lugares tengo guardados?". ' +
        'Solo ve los lugares de quien ha iniciado sesión.',
      inputSchema: z.object({}),
      annotations: SOLO_LEER,
    },
    protegida(async () => {
      // Sin filtro por usuario: lo pone la RLS de la base de datos.
      const { data, error: fallo } = await supabase
        .from('lugares_favoritos').select('nombre').order('creado').limit(10)
      if (fallo) throw new ErrorParaLaIA(`No he podido leer tus lugares: ${fallo.message}`)
      if (!data.length) return texto({ lugares: [], aviso: 'No tienes lugares guardados. Usa guardar_lugar.' })
      const lugares = await Promise.all(data.map(async (fila) => tiempoEn(await buscarLugar(fila.nombre))))
      return texto({ lugares })
    })
  )

  server.registerTool(
    'quien_soy',
    {
      description: 'Con qué cuenta ha iniciado sesión esta conexión (correo e id). Úsala para comprobar el login.',
      inputSchema: z.object({}),
      annotations: { readOnlyHint: true, destructiveHint: false, openWorldHint: false },
    },
    protegida(async () =>
      texto({
        id: usuario.id,
        correo: usuario.email ?? null,
        cliente_oauth: typeof ctx.jwtClaims?.client_id === 'string' ? ctx.jwtClaims.client_id : null,
      })
    )
  )

  return server
}

Deno.serve(
  pipeline(
    [withOAuthProtectedResource(), withSupabase({ auth: 'user', cors: { headers: CORS } })],
    (request, ctx) =>
      createMcpHandler(() => crearServidor(ctx), {
        onerror: (fallo) => console.error('Fallo en una petición MCP', fallo),
      }).fetch(request)
  )
)
