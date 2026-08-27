# Documentacion de la API - Dog Breed Selector

## Vision General

La API de Dog Breed Selector es una API RESTful construida con FastAPI que proporciona acceso programatico al sistema de recomendacion de razas de perros.

**URL Base**: `http://localhost:8000` (en desarrollo)  
**Version**: 1.0.0  
**Formato**: JSON  
**Documentacion Interactiva**: http://localhost:8000/docs

## Endpoints

### 1. GET / - Informacion de la API

Obtiene informacion basica sobre la API y endpoints disponibles.

**Request:**
```bash
curl http://localhost:8000/
```

**Response:**
```json
{
  "message": "Dog Breed Selector API",
  "version": "1.0.0",
  "docs": "/docs",
  "endpoints": {
    "get_questions": "/api/questions",
    "get_recommendations": "/api/recommendations",
    "get_breeds": "/api/breeds",
    "get_breed": "/api/breeds/{breed_id}",
    "search": "/api/search"
  }
}
```

### 2. GET /api/questions - Obtener Preguntas

Obtiene las preguntas del cuestionario, opcionalmente filtradas por categoria.

**Parametros:**
- `category` (query, opcional): ID de la categoria (hogar, estilo_vida, experiencia, etc.)

**Request:**
```bash
# Todas las categorias
curl http://localhost:8000/api/questions

# Categoria especifica
curl "http://localhost:8000/api/questions?category=hogar"
```

**Response:**
```json
{
  "success": true,
  "categories": ["hogar", "estilo_vida", "experiencia", "preferencias_fisicas", "salud", "personalidad", "cuidados", "objetivos"],
  "total_questions": 17
}
```

### 3. POST /api/recommendations - Obtener Recomendaciones

Obtiene recomendaciones de razas basadas en las respuestas del usuario al cuestionario.

**Parametros:**
- `top_n` (query, opcional): Numero de recomendaciones a devolver (default: 10, max: 50)

**Body:** (ver ejemplo completo en seccion de ejemplos)

**Request:**
```bash
curl -X POST "http://localhost:8000/api/recommendations?top_n=5" \
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

**Response:**
```json
{
  "success": true,
  "total_breeds_evaluated": 29,
  "recommendations": [
    {
      "rank": 1,
      "breed_id": "cavalier_king_charles",
      "breed_name": "Cavalier King Charles Spaniel",
      "breed_name_es": "Cavalier King Charles Spaniel",
      "match_percentage": 87.5,
      "total_score": 89.2,
      "key_traits": ["Small size", "Energy: 3/5", "Affectionate", "Gentle"],
      "considerations": ["Moderate exercise", "Good with children"],
      "dealbreakers": []
    }
  ],
  "message": "Se encontraron 5 razas recomendadas"
}
```

### 4. GET /api/breeds - Listar Razas

Obtiene una lista de todas las razas disponibles, opcionalmente filtrada.

**Parametros:**
- `size` (query, opcional): Filtrar por tamaño (mini, small, medium, large, giant)
- `hypoallergenic` (query, opcional): Filtrar por hipoalergenicas (true/false)
- `apartment_friendly_min` (query, opcional): Minimo score de amigabilidad con apartamentos (1-5)
- `limit` (query, opcional): Maximo numero de resultados (default: 50, max: 200)

**Request:**
```bash
# Todas las razas
curl "http://localhost:8000/api/breeds"

# Filtrar por tamaño
curl "http://localhost:8000/api/breeds?size=small"

# Filtrar por hipoalergenicas
curl "http://localhost:8000/api/breeds?hypoallergenic=true"
```

**Response:**
```json
{
  "success": true,
  "count": 29,
  "breeds": [
    {
      "id": "chihuahua",
      "name": "Chihuahua",
      "name_es": "Chihuahua",
      "size_category": "mini",
      "hypoallergenic": false,
      "apartment_friendly": 5,
      "energy_level": 3,
      "good_with_children": 2
    }
  ]
}
```

### 5. GET /api/breeds/{breed_id} - Obtener Raza Especifica

Obtiene informacion detallada de una raza especifica por su ID.

**Parametros:**
- `breed_id` (path, requerido): ID de la raza (ej: labrador_retriever)

**Request:**
```bash
curl "http://localhost:8000/api/breeds/labrador_retriever"
```

**Response:**
```json
{
  "success": true,
  "breed": {
    "id": "labrador_retriever",
    "name": "Labrador Retriever",
    "name_es": "Labrador Retriever",
    "size_category": "medium",
    "weight_kg_min": 25,
    "weight_kg_max": 36,
    "height_cm_min": 55,
    "height_cm_max": 62,
    "life_expectancy_min": 10,
    "life_expectancy_max": 12,
    "energy_level": 5,
    "exercise_needs_daily_min": 60,
    "exercise_needs_daily_max": 90,
    "trainability": 5,
    "intelligence": 4,
    "good_with_children": 5,
    "good_with_dogs": 5,
    "good_with_cats": 4,
    "shedding": 4,
    "grooming_needs": 2,
    "barking_level": 2,
    "drooling": 3,
    "coat_type": "short",
    "hypoallergenic": false,
    "apartment_friendly": 3,
    "good_for_first_time": 5,
    "temperament": ["amigable", "activo", "salida", "inteligente"],
    "special_needs": "Ejercicio diario, control de peso",
    "common_health_problems": ["displasia de cadera", "displasia de codo", "obesidad"],
    "description_es": "El perro familiar por excelencia, amigable y versatil."
  }
}
```

### 6. GET /api/search - Buscar Razas

Busca razas por nombre o caracteristicas.

**Parametros:**
- `q` (query, requerido): Termino de busqueda (minimo 2 caracteres)

**Request:**
```bash
curl "http://localhost:8000/api/search?q=labrador"
curl "http://localhost:8000/api/search?q=hypoallergenic"
curl "http://localhost:8000/api/search?q=inteligente"
```

**Response:**
```json
{
  "success": true,
  "query": "labrador",
  "count": 2,
  "breeds": [
    {
      "id": "labrador_retriever",
      "name": "Labrador Retriever",
      "name_es": "Labrador Retriever",
      "size_category": "medium",
      "temperament": ["amigable", "activo", "salida", "inteligente"]
    }
  ]
}
```

## Ejemplos de Uso

### Python

```python
import requests

# Obtener recomendaciones
url = "http://localhost:8000/api/recommendations"
data = {
    "housing_type": "apartamento_mediano",
    "housing_size_sqm": 75,
    "has_garden": "terrace",
    "household_size": 2,
    "has_children": "no",
    "activity_level": "moderate",
    "daily_exercise_time_minutes": 45,
    "work_schedule": "office_8h",
    "dog_experience": "basic",
    "first_time_owner": True,
    "preferred_size": "small",
    "shedding_tolerance": "low",
    "grooming_willingness": "moderate",
    "household_allergies": "none",
    "desired_energy": "medium",
    "barking_tolerance": "low",
    "kids_compatibility": "not_important",
    "vet_budget_monthly": "medium",
    "obedience_expectations": "good"
}

response = requests.post(url, json=data, params={"top_n": 5})
results = response.json()

for rec in results["recommendations"]:
    print(f"{rec['rank']}. {rec['breed_name_es']} - {rec['match_percentage']}%")
```

### JavaScript

```javascript
// Obtener recomendaciones
const response = await fetch('http://localhost:8000/api/recommendations?top_n=5', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    housing_type: 'apartamento_mediano',
    housing_size_sqm: 75,
    has_garden: 'terrace',
    household_size: 2,
    has_children: 'no',
    activity_level: 'moderate',
    daily_exercise_time_minutes: 45,
    work_schedule: 'office_8h',
    dog_experience: 'basic',
    first_time_owner: true,
    preferred_size: 'small',
    shedding_tolerance: 'low',
    grooming_willingness: 'moderate',
    household_allergies: 'none',
    desired_energy: 'medium',
    barking_tolerance: 'low',
    kids_compatibility: 'not_important',
    vet_budget_monthly: 'medium',
    obedience_expectations: 'good'
  })
});

const results = await response.json();
results.recommendations.forEach(rec => {
  console.log(`${rec.rank}. ${rec.breed_name_es} - ${rec.match_percentage}%`);
});
```

## Errores Comunes

### 422 Validation Error

```json
{
  "detail": [
    {
      "loc": ["body", "housing_size_sqm"],
      "msg": "ensure this value is greater than or equal to 20",
      "type": "value_error.number.not_ge"
    }
  ]
}
```

**Solucion**: Verifica que todos los campos requeridos esten presentes y tengan valores validos.

### 404 Not Found

```json
{
  "detail": "Raza 'invalid_breed' no encontrada"
}
```

**Solucion**: Verifica que el breed_id sea correcto. Usa `/api/breeds` para ver la lista completa.

## Documentacion Interactiva

FastAPI proporciona documentacion interactiva automatica:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

En estas interfaces puedes:
- Ver todos los endpoints
- Probar peticiones directamente
- Ver esquemas de request/response
- Descargar especificacion OpenAPI

---

*Documentacion de la API v1.0.0 - Agosto 2024*
