# Inicio Rapido - Quick Start

!Comienza a usar Dog Breed Selector en 5 minutos! 🚀

## Opcion 1: Usar la Interfaz Web (Recomendado para principiantes)

### Pasos:
1. Abre el archivo `web/index.html` en tu navegador
2. Completa el cuestionario con tus preferencias
3. Haz clic en "Obtener Recomendaciones"
4. !Ve tus razas ideales!

## Opcion 2: Usar la API REST

### 1. Instalar dependencias:
```bash
pip install -r requirements.txt
```

### 2. Iniciar la API:
```bash
cd api
python main.py
```

### 3. Abrir documentacion:
- Ve a `http://localhost:8000/docs` en tu navegador
- Explora los endpoints disponibles
- Prueba las peticiones directamente desde Swagger UI

### 4. Ejemplo de peticion:
```bash
curl -X POST "http://localhost:8000/api/recommendations" \
  -H "Content-Type: application/json" \
  -d '{
    "housing_type": "apartamento_mediano",
    "housing_size_sqm": 75,
    "has_garden": "terrace",
    "household_size": 2,
    "has_children": "no",
    "activity_level": "moderate",
    "daily_exercise_time_minutes": 45,
    "work_schedule": "office_8h",
    "dog_experience": "basic",
    "first_time_owner": true,
    "preferred_size": "small",
    "shedding_tolerance": "low",
    "grooming_willingness": "moderate",
    "household_allergies": "none",
    "desired_energy": "medium",
    "barking_tolerance": "low",
    "kids_compatibility": "not_important",
    "vet_budget_monthly": "medium",
    "obedience_expectations": "good"
  }'
```

## Opcion 3: Usar el Script de Python

### 1. Ejecutar ejemplo:
```bash
cd examples
python example_usage.py
```

### 2. Ver resultados:
- El script mostrara las top 5 razas recomendadas
- Incluye caracteristicas clave y consideraciones

## Opcion 4: Ejecutar Tests

### 1. Instalar pytest:
```bash
pip install pytest pytest-cov
```

### 2. Ejecutar tests:
```bash
pytest tests/ -v
```

### 3. Ver coverage:
```bash
pytest tests/ --cov=src --cov-report=html
# Abrir htmlcov/index.html en el navegador
```

## Estructura del Proyecto

```
dog-breed-selector/
├── README.md              # Documentacion principal
├── QUICKSTART.md          # Esta guia de inicio rapido
├── CONTRIBUTING.md        # Guia de contribuciones
├── requirements.txt       # Dependencias de Python
├── .gitignore            # Archivos a ignorar
│
├── questionnaire/
│   └── questions.json    # Preguntas del cuestionario
│
├── database/
│   └── breeds.csv        # Base de datos de razas
│
├── src/
│   ├── __init__.py
│   └── calculator.py     # Logica de calculo
│
├── api/
│   ├── __init__.py
│   └── main.py           # API REST (FastAPI)
│
├── web/
│   └── index.html        # Interfaz web
│
├── examples/
│   └── example_usage.py  # Ejemplo de uso
│
├── tests/
│   └── test_calculator.py # Tests unitarios
│
└── docs/
    └── methodology.md    # Metodologia de evaluacion
```

## Comandos Utiles

### Instalar dependencias:
```bash
pip install -r requirements.txt
```

### Ejecutar API en modo desarrollo:
```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Ejecutar tests:
```bash
pytest tests/ -v --tb=short
```

### Formatear codigo:
```bash
black src/ api/ tests/
flake8 src/ api/ tests/
```

## Problemas Comunes

### Error: "ModuleNotFoundError: No module named 'calculator'"
**Solucion:** Asegurate de estar en el directorio correcto o anadir src al path:
```python
import sys
sys.path.insert(0, 'src')
```

### Error: "Port 8000 is already in use"
**Solucion:** Usa otro puerto:
```bash
uvicorn api.main:app --reload --port 8001
```

### Error: "pytest: command not found"
**Solucion:** Instala pytest:
```bash
pip install pytest
```

## Siguientes Pasos

1. !Explora la documentacion en `/docs`!
2. Personaliza el cuestionario con tus propias preguntas
3. Anade mas razas a la base de datos
4. Contribuye con mejoras al proyecto

## Recursos Adicionales

- [Documentacion de FastAPI](https://fastapi.tiangolo.com/)
- [Documentacion de pytest](https://docs.pytest.org/)
- [Guia de estilo PEP 8](https://pep8.org/)

!Disfruta encontrando tu raza ideal! 🐕
