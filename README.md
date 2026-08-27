# 🐕 Dog Breed Selector

Recomendador de razas de perro basado en un cuestionario de compatibilidad
multi-criterio (hogar, estilo de vida, experiencia, salud, personalidad...).

## Estado del proyecto

Revisado y estabilizado — el repo original tenía el motor sin datos que
cargar (`questionnaire/questions.json` vacío, `load_data()` apuntando a un
fichero inexistente) y corrupción de encoding en todos los ficheros de
texto. Ambos problemas están corregidos; ver `CHANGELOG` más abajo.

## Estructura

```
database/breeds.csv        Base de datos de 29 razas (fuente de verdad)
questionnaire/questions.json  Cuestionario: categorías, pesos, preguntas
src/breeds.py               Carga y valida el CSV y el cuestionario
src/calculator.py           Motor de scoring (puro, sin I/O)
src/recommender.py          API de alto nivel + CLI
api/main.py                 API HTTP (FastAPI) sobre el mismo motor
tests/                      pytest sobre datos y motor
web/index.html + engine.js  Front estático; puntúa en el navegador con un
                             espejo en JS del motor de Python (no llama a
                             la API)
docs/methodology.md         Metodología de scoring
vercel.json                 Despliega api/ como función serverless y
                             web/ como sitio estático en la raíz
```

## Uso

```bash
pip install -r requirements.txt

# CLI
PYTHONPATH=src python3 src/recommender.py --top 5
PYTHONPATH=src python3 src/recommender.py --answers mi_perfil.json --json

# Tests
PYTHONPATH=src python3 -m pytest
```

```python
import sys; sys.path.insert(0, "src")
from recommender import BreedRecommender

recommender = BreedRecommender()
for rec in recommender.recommend({"preferred_size": "small", "desired_energy": "low"}):
    print(rec.score.breed_name_es, rec.score.match_percentage)
```

### Web

`web/index.html` es estático: abre el fichero o sírvelo con
`python3 -m http.server` desde `web/`. Lee `breeds.json` y `questions.json`
(regenerables con `python3 -c "from breeds import *; ..."`, ver
`src/breeds.py:breeds_to_json`) y puntúa en el navegador con `engine.js`,
un espejo de `src/calculator.py` (misma fórmula, incluido el multiplicador
de alineación). Si cambias una fórmula de scoring, cámbiala en los dos
sitios — no hay build step ni tipo que te avise si se desincronizan. Es
intencionalmente independiente de la API: funciona sin backend.

El cuestionario se renderiza dinámicamente desde `questions.json` como un
wizard de un paso por categoría (barra de progreso, texto de ayuda bajo
cada pregunta explicando qué implica la respuesta) — no hay campos
hardcodeados en el HTML, así que una pregunta nueva en `questions.json`
aparece sola en la web sin tocar `index.html`. Los resultados muestran un
"hero card" para la raza #1 y filas compactas para el resto, pensados para
caber en una sola captura de pantalla; el botón "Compartir resultado" usa
`navigator.share` en móvil o copia un resumen al portapapeles.

### API

```bash
pip install -r requirements.txt
PYTHONPATH=src uvicorn api.main:app --reload --port 8000
# http://localhost:8000/docs
```

Endpoints: `GET /api/questions`, `POST /api/recommendations`,
`GET /api/breeds` (con filtros `size`, `hypoallergenic`,
`apartment_friendly_min`), `GET /api/breeds/{id}`, `GET /api/search?q=...`.
En Vercel, `vercel.json` la despliega como función serverless bajo `/api/*`
mientras sirve `web/` como sitio estático en la raíz.

## Metodología

Ver [`docs/methodology.md`](./docs/methodology.md): 8 categorías ponderadas,
penalización por "dealbreakers" (incompatibilidades críticas), escala de
interpretación 0-100.

## Calidad de datos

`database/breeds.csv` fue auditado fila por fila contra estándares AKC/FCI;
ver [`docs/auditoria-datos.md`](./docs/auditoria-datos.md) para el detalle y
las 31 reglas de validación (`V-01`...`V-31`) que documentan qué debe
cumplir siempre el CSV. Las reglas de mayor impacto ya están cubiertas por
`tests/test_breeds.py`. Pendiente de una futura pasada: ampliar el catálogo
(falta el grupo Terrier entero, ver §3 del informe) y terminar de normalizar
`origin_country` (V-19, mezcla países y regiones).

## Otros documentos

[`CONTRIBUTING.md`](./CONTRIBUTING.md), [`QUICKSTART.md`](./QUICKSTART.md),
[`docs/api_documentation.md`](./docs/api_documentation.md) y
[`docs/faq.md`](./docs/faq.md).

## Pendiente / roadmap

- Ampliar el catálogo de razas más allá de las 29 actuales (falta el grupo
  Terrier entero, ver `docs/auditoria-datos.md` §3)
- CI (lint + pytest) en GitHub Actions
