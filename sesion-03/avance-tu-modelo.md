# Avance de la sesión 3: tu modelo, entrenado en local

Para quien ya tiene la sesión 2 hecha: tu URL de Vercel enseña tus datos de Supabase, con login y algo que cada usuario guarda.

Mañana, en la sesión 3, tu modelo se publica como API en Render y tu app lo usa. Hoy puedes adelantar la primera mitad: elegir qué predices, entrenar el modelo con tus datos y guardarlo. Todo en tu ordenador; no se despliega nada.

Abre tu agente en la carpeta de tu cuaderno, como hoy, y pégale este prompt:

```text
Lee brief.md, arquitectura.md, datos.md y estado.yaml. Vamos a adelantar la
pieza "modelo" (sesión 3), solo la primera mitad y solo en local: mañana la
publicamos como API en Render.

1. Propónme qué columna de mis datos predecir y con qué columnas, y si es
   regresión o clasificación. Espera a que te diga que sí antes de seguir.
2. En el repo de mi app (dentro de apps/), crea una carpeta modelo/ con
   entrenar.py: lee mi CSV, separa 80 % para entrenar y 20 % para probar
   (random_state=42) y entrena un modelo sencillo de scikit-learn dentro de
   un Pipeline (el preprocesado va dentro del pipeline).
3. Compáralo con una predicción ingenua (la media, o la clase más frecuente)
   con una métrica que yo entienda: error medio absoluto en las unidades de
   mi columna, o porcentaje de aciertos. Enséñame las dos cifras.
4. Guarda el pipeline entrenado en modelo/modelo.joblib y escribe
   modelo/requirements.txt con las versiones exactas que tengo instaladas
   de pandas, scikit-learn y joblib (Render tendrá que usar las mismas).
5. Usa un entorno virtual (.venv) y añádelo a .gitignore. Si estoy en
   Windows, los comandos en PowerShell.
6. Si mis datos son privados o el CSV pesa más de 50 MB, no los subas a
   GitHub: dímelo y lo decidimos.
7. En mi cuaderno: una entrada en decisiones.md (qué predigo, con qué, qué
   modelo, las dos cifras del paso 3 y por qué me quedo con este), la pieza
   "modelo" de estado.yaml actualizada sin cambiar las claves, y todo.md.
8. No despliegues nada. Si te sobra tiempo: una API local con FastAPI con
   GET /health y POST /predict que cargue modelo.joblib, y una prueba con
   curl (en Windows, Invoke-RestMethod).

Commit y push en el repo de la app y después en el cuaderno.
```

## Si tu agente te pide crear el entorno virtual tú

En la carpeta `modelo/` de tu app.

**Mac, Linux o Git Bash en Windows:**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pandas scikit-learn joblib
```

**Windows, en PowerShell:**

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install pandas scikit-learn joblib
```

Si PowerShell dice que no puede ejecutar scripts ("running scripts is disabled"), ejecuta esto una vez y vuelve a activar el entorno:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

## Hecho

- Sabes qué predices y por qué, y está en `decisiones.md`.
- Tu modelo mejora la predicción ingenua, con las dos cifras apuntadas. Si no la mejora, también se apunta: es un resultado.
- `modelo/modelo.joblib` y `modelo/requirements.txt` están en el repo de tu app.
- `estado.yaml` y `todo.md` dicen dónde lo dejas.

Mañana lo publicamos en Render y tu app enseña la predicción.
