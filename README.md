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
tests/                      pytest sobre datos y motor
web/index.html + engine.js  Front estático (sin backend); usa un espejo
                             en JS del motor de Python
docs/methodology.md         Metodología de scoring
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
un espejo simplificado de `src/calculator.py`. Si cambias una fórmula de
scoring, cámbiala en los dos sitios.

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

## Pendiente / roadmap

- API HTTP (el `requirements.txt` original prometía FastAPI sin código;
  se ha retirado hasta que exista)
- Ampliar el catálogo de razas más allá de las 29 actuales
- CI (lint + pytest) en GitHub Actions
