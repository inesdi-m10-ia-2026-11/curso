// ---------- RAG: buscar_en_textos, versión Edge Function (extra de la sesión 4) ----------
//
// NO es un archivo para desplegar: son DOS trozos para PEGAR en tu
// supabase/functions/mcp/index.ts, el de la parte 7a de tu-mcp.md (copiado del de
// "Madrid ahora"). Usa lo que ese archivo ya tiene: z, SOLO_LEER, ErrorParaLaIA, texto,
// protegida y la constante supabase de crearServidor (ctx.supabase: el cliente con el
// token de quien llama, así que la RLS de trozos se aplica también aquí).
//
// Necesita un secreto en la función: GEMINI_API_KEY, tu clave de AI Studio. En el panel
// de Supabase: Edge Functions, Secrets (https://supabase.com/dashboard/project/_/functions/secrets).
// Nunca en el código ni en un .env del repo. La función lo lee al momento: no hace falta
// volver a desplegar después de guardarlo.
//
// Mismo modelo, mismas 768 dimensiones y mismo prefijo de pregunta que cargar_textos.py y
// herramienta_textos.py. Sin probar: ni en local ni en Supabase (26/11/2026).


// ===== Trozo 1: fuera de crearServidor, debajo de los otros ayudantes (después de pedir) =====

const GEMINI_EMBEDDINGS =
  'https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-2:embedContent'
const DIMENSIONES = 768 // las mismas que trozos.sql y cargar_textos.py

async function vectorDeLaPregunta(pregunta: string): Promise<number[]> {
  const clave = Deno.env.get('GEMINI_API_KEY')
  if (!clave) {
    throw new ErrorParaLaIA('La función no tiene GEMINI_API_KEY: añádela en Supabase (Edge Functions, Secrets).')
  }
  let respuesta: Response
  try {
    respuesta = await fetch(GEMINI_EMBEDDINGS, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'x-goog-api-key': clave },
      body: JSON.stringify({
        model: 'models/gemini-embedding-2',
        // gemini-embedding-2 no tiene task_type: la tarea va dentro del texto.
        content: { parts: [{ text: `task: question answering | query: ${pregunta}` }] },
        output_dimensionality: DIMENSIONES,
      }),
      signal: AbortSignal.timeout(20_000),
    })
  } catch {
    throw new ErrorParaLaIA('No he podido conectar con Gemini. Prueba otra vez en un momento.')
  }
  if (respuesta.status === 429) {
    throw new ErrorParaLaIA('Gemini dice que hay demasiadas peticiones (429). Espera un minuto y vuelve a preguntar.')
  }
  if (!respuesta.ok) {
    throw new ErrorParaLaIA(`Gemini ha dado un error ${respuesta.status}: ${(await respuesta.text()).slice(0, 300)}`)
  }
  const valores: number[] = (await respuesta.json()).embedding?.values ?? []
  if (valores.length !== DIMENSIONES) {
    throw new ErrorParaLaIA(`Gemini ha devuelto ${valores.length} dimensiones y la tabla espera ${DIMENSIONES}.`)
  }
  return valores
}

type Trozo = { fuente: string; pagina: number | null; texto: string; parecido: number; url: string | null }


// ===== Trozo 2: dentro de crearServidor, con las otras herramientas (antes de "return server") =====

  server.registerTool(
    'buscar_en_textos',
    {
      description:
        // CAMBIA: qué documentos son (título, quién los publica, año) y para qué preguntas sirven.
        'Busca en <tus documentos: cuáles, de quién y de qué año> los trozos de texto que mejor ' +
        'responden a una pregunta. Úsala para lo que DICEN esos documentos: definiciones, normas, ' +
        'recomendaciones, explicaciones. NO la uses para cifras, filas o recuentos de <tus datos>: ' +
        'para eso están tus otras herramientas. Devuelve los trozos con su fuente, su página y un ' +
        '"parecido" (más cerca de 1, más se parece). Responde solo con lo que digan los trozos y cita ' +
        'fuente y página. Si ninguno responde, dilo: no completes de memoria.',
      inputSchema: z.object({
        pregunta: z.string().min(3).max(500)
          .describe("La pregunta del usuario, entera y con sus palabras. CAMBIA el ejemplo: '¿qué dice la guía sobre la fianza?'"),
        cuantos: z.number().int().min(1).max(10).default(5)
          .describe('Cuántos trozos devolver, del más parecido al menos'),
      }),
      annotations: SOLO_LEER,
    },
    protegida(async ({ pregunta, cuantos }: { pregunta: string; cuantos: number }) => {
      const vector = await vectorDeLaPregunta(pregunta)
      // Con el token de quien llama: rol authenticated, que trozos.sql deja leer.
      const { data, error: fallo } = await supabase.rpc('buscar_trozos', {
        pregunta_embedding: vector,
        cuantos,
      })
      if (fallo) throw new ErrorParaLaIA(`Supabase no ha podido buscar en los textos: ${fallo.message}`)
      const filas = (data ?? []) as Trozo[]
      if (!filas.length) {
        return texto({
          pregunta,
          trozos: [],
          aviso: 'No ha salido ningún trozo. Si la tabla trozos tiene filas, revisa el paso 4 de trozos.sql (grant y política).',
        })
      }
      return texto({
        pregunta,
        trozos: filas.map((f) => ({
          fuente: f.fuente,
          pagina: f.pagina,
          texto: f.texto,
          parecido: Math.round(f.parecido * 1000) / 1000,
          url: f.url,
        })),
        como_citar: '(fuente, página). Si el parecido del primer trozo es bajo, probablemente el texto no lo dice.',
      })
    })
  )
