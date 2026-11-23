# Tu app en tu cuenta, enlazada en tu cuaderno

Módulo 10 · Sesión 1 · lunes 23/11/2026

**Para quién:** si has montado tu página en `web/` dentro de tu cuaderno (`alumno-...`), o si todavía no tienes repo para tu app.

**Por qué:** tu cuaderno es un repo privado de la organización del curso, y Vercel gratis no publica repos privados de una organización. Tu app vive en un repo de **tu cuenta** de GitHub (privado), que Vercel sí publica, y queda enlazado en tu cuaderno como submódulo, en `apps/`. Así tu agente ve todo el proyecto desde el cuaderno.

```
alumno-tu-nombre/        tu cuaderno (organización, privado)
├── idea.md, bitacora/, urls.md...
└── apps/
    └── tu-proyecto/     tu app (tu cuenta, privado): web/, datos/, scripts/
```

**Antes de empezar:**
1. Abre tu agente **en la carpeta de tu cuaderno**.
2. En la terminal, `gh auth status` tiene que decir `Logged in to github.com`. Si no tienes `gh`, crea el repo a mano en github.com (**Private** y con **Add a README file**) y, cuando el agente te pregunte, dale su URL.

---

## El prompt (cópialo entero)

```
Lee AGENTS.md antes de nada. Estás en mi cuaderno del curso, un repo
privado de la organización del curso. La app de mi proyecto tiene que vivir
en un repo de mi cuenta de GitHub, enlazado aquí como submódulo en apps/,
porque Vercel gratis no publica repos privados de una organización.
Dime cada comando antes de ejecutarlo y espera mi OK.

1. Comprueba que gh funciona (gh auth status) y dime con qué usuario.
2. Pregúntame si ya tengo un repo de mi proyecto en mi cuenta.
   - Si lo tengo, pídeme su URL y usa ese.
   - Si no, pregúntame el nombre del proyecto (minúsculas y guiones) y
     créalo en mi cuenta, privado y con README:
     gh repo create NOMBRE --private --add-readme
3. Añádelo a este cuaderno como submódulo en apps/NOMBRE.
4. Si en el cuaderno hay carpetas de la app (web/, datos/, scripts/),
   pásalas a apps/NOMBRE/ y quítalas del cuaderno. No toques idea.md,
   datos.md, decisiones.md, bitacora/, prompts/, urls.md ni el AGENTS.md
   del cuaderno. Si mis datos son de mi empresa o tienen datos personales,
   pregúntame antes de subirlos: en ese caso, añade datos/ al .gitignore
   de la app.
5. Si apps/NOMBRE no tiene AGENTS.md, créalo con mi idea (de idea.md), mis
   datos (de datos.md) y esta estructura: web/ es la página pública,
   publicada en Vercel con Root Directory web, en HTML estático; vendrán
   api/ (sesión 3), mcp/ (sesión 4) y agente/ (sesión 5). Añade también un
   CLAUDE.md con una sola línea: @AGENTS.md
6. Dentro de apps/NOMBRE: enséñame el git status, haz commit con el mensaje
   "Mi app" y push.
7. Da acceso a mi profesor: invita a sergio-inesdi como colaborador de mi
   repo de la app.
8. En el cuaderno: apunta en urls.md el repo de la app, haz commit (con el
   submódulo y sin las carpetas que has pasado) con el mensaje
   "Mi app, enlazada en apps/" y push.
9. Resúmeme qué ha quedado en cada repo.
```

Lee los comandos antes de aprobarlos. Si algo no te cuadra, pregúntale qué hace ese comando.

---

## Después: publícala en Vercel

1. En https://vercel.com, **Add New...** y **Project**.
2. Importa el repo **de tu app** (no el cuaderno). ¿No aparece? **Adjust GitHub App Permissions**, da acceso a ese repo de tu cuenta y vuelve.
3. **Root Directory:** `web`. **Framework Preset:** Other.
4. **Deploy.** Abre la URL en el móvil.
5. Pide a tu agente: "Apunta esta URL de Vercel en urls.md, haz commit y push": [tu URL].

Desde ahora, cada `push` en el repo de tu app vuelve a publicar la página.

---

## Si algo falla

| Síntoma | Arreglo |
|---|---|
| `gh: command not found` o "not logged in" | Paso 4 del setup (`gh auth login`). O crea el repo en github.com y dale la URL al agente |
| `git submodule add` dice que el repo está vacío | El repo se creó sin README. Añade uno en github.com ("Add a README") y repite el paso 3 |
| `git push` pide usuario y contraseña | `gh auth login` y responde **Yes** a "Authenticate Git with your GitHub credentials" |
| Vercel no ve tu repo | **Adjust GitHub App Permissions** y da acceso al repo de tu app |
| Vercel da 404 | El Root Directory no es `web`, o el archivo no se llama `index.html` |
| Importaste el cuaderno por error | Vercel no lo publicará: es privado y de la organización. Importa el repo de tu app |
