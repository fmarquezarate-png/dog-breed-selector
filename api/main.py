"""
Dog Breed Selector - API REST
API principal usando FastAPI
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
import json
import os

# Importar calculador
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from calculator import CompatibilityCalculator, load_data, BreedScore

# Inicializar FastAPI
app = FastAPI(
    title="Dog Breed Selector API",
    description="API para recomendacion de razas de perros basada en preferencias personales",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cargar datos al iniciar
breeds_data, questions_data = load_data()
calculator = CompatibilityCalculator(breeds_data, questions_data)


# Modelos Pydantic
class QuestionnaireResponse(BaseModel):
    """Respuesta del cuestionario del usuario"""
    housing_type: str = Field(..., description="Tipo de vivienda")
    housing_size_sqm: int = Field(..., ge=20, le=500, description="Metros cuadrados")
    has_garden: str = Field(..., description="Espacios exteriores")
    household_size: int = Field(..., ge=1, le=10, description="Personas en el hogar")
    has_children: str = Field(..., description="Ninos en el hogar")
    activity_level: str = Field(..., description="Nivel de actividad fisica")
    daily_exercise_time_minutes: int = Field(..., ge=15, le=300, description="Minutos de ejercicio diario")
    work_schedule: str = Field(..., description="Horario laboral")
    dog_experience: str = Field(..., description="Experiencia con perros")
    first_time_owner: bool = Field(..., description="Es su primer perro")
    preferred_size: str = Field(..., description="Tamano preferido")
    shedding_tolerance: str = Field(..., description="Tolerancia a muda")
    grooming_willingness: str = Field(..., description="Disposicion para grooming")
    household_allergies: str = Field(..., description="Alergias en el hogar")
    desired_energy: str = Field(..., description="Nivel de energia deseado")
    barking_tolerance: str = Field(..., description="Tolerancia al ladrido")
    kids_compatibility: str = Field(..., description="Importancia compatibilidad con ninos")
    vet_budget_monthly: str = Field(..., description="Presupuesto veterinario")
    obedience_expectations: str = Field(..., description="Expectativas de obediencia")


class BreedRecommendation(BaseModel):
    """Recomendacion de raza individual"""
    rank: int
    breed_id: str
    breed_name: str
    breed_name_es: str
    match_percentage: float
    total_score: float
    key_traits: List[str]
    considerations: List[str]
    dealbreakers: List[str]


class RecommendationsResponse(BaseModel):
    """Respuesta con recomendaciones"""
    success: bool
    total_breeds_evaluated: int
    recommendations: List[BreedRecommendation]
    message: str


# Endpoints
@app.get("/")
async def root():
    """Endpoint raiz con informacion de la API"""
    return {
        "message": "Dog Breed Selector API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "get_questions": "/api/questions",
            "get_recommendations": "/api/recommendations",
            "get_breeds": "/api/breeds",
            "get_breed": "/api/breeds/{breed_id}"
        }
    }


@app.get("/api/questions")
async def get_questions(category: Optional[str] = None):
    """Obtener preguntas del cuestionario"""
    if category:
        categories = questions_data.get("categories", {})
        if category in categories:
            return {"success": True, "category": category, "questions": categories[category].get("questions", [])}
        else:
            raise HTTPException(status_code=404, detail=f"Categoria '{category}' no encontrada")
    
    return {"success": True, "categories": list(questions_data.get("categories", {}).keys()), "total_questions": sum(len(cat.get("questions", [])) for cat in questions_data.get("categories", {}).values())}


@app.post("/api/recommendations", response_model=RecommendationsResponse)
async def get_recommendations(response: QuestionnaireResponse, top_n: int = Query(10, ge=1, le=50)):
    """Obtener recomendaciones de razas basadas en respuestas"""
    try:
        answers = response.model_dump()
        scores = calculator.score_all_breeds(answers)
        
        recommendations = []
        for i, score in enumerate(scores[:top_n], 1):
            rec = BreedRecommendation(
                rank=i,
                breed_id=score.breed_id,
                breed_name=score.breed_name,
                breed_name_es=score.breed_name_es,
                match_percentage=score.match_percentage,
                total_score=score.total_score,
                key_traits=score.key_traits,
                considerations=score.considerations,
                dealbreakers=score.dealbreakers
            )
            recommendations.append(rec)
        
        return RecommendationsResponse(
            success=True,
            total_breeds_evaluated=len(scores),
            recommendations=recommendations,
            message=f"Se encontraron {len(recommendations)} razas recomendadas"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al calcular recomendaciones: {str(e)}")


@app.get("/api/breeds")
async def get_breeds(
    size: Optional[str] = None,
    hypoallergenic: Optional[bool] = None,
    apartment_friendly_min: Optional[int] = None,
    limit: int = Query(50, ge=1, le=200)
):
    """Obtener lista de razas con filtros opcionales"""
    results = breeds_data.copy()
    
    if size:
        results = [b for b in results if b.get("size_category") == size]
    
    if hypoallergenic is not None:
        results = [b for b in results if b.get("hypoallergenic") == hypoallergenic]
    
    if apartment_friendly_min is not None:
        results = [b for b in results if b.get("apartment_friendly", 0) >= apartment_friendly_min]
    
    return {
        "success": True,
        "count": len(results),
        "breeds": [{
            "id": b.get("id"),
            "name": b.get("name"),
            "name_es": b.get("name_es"),
            "size_category": b.get("size_category"),
            "hypoallergenic": b.get("hypoallergenic"),
            "apartment_friendly": b.get("apartment_friendly"),
            "energy_level": b.get("energy_level"),
            "good_with_children": b.get("good_with_children")
        } for b in results[:limit]]
    }


@app.get("/api/breeds/{breed_id}")
async def get_breed(breed_id: str):
    """Obtener detalles de una raza especifica"""
    for breed in breeds_data:
        if breed.get("id") == breed_id:
            return {"success": True, "breed": breed}
    
    raise HTTPException(status_code=404, detail=f"Raza '{breed_id}' no encontrada")


@app.get("/api/search")
async def search_breeds(q: str = Query(..., min_length=2, description="Termino de busqueda")):
    """Buscar razas por nombre o caracteristicas"""
    query_lower = q.lower()
    results = []
    
    for breed in breeds_data:
        if query_lower in breed.get("name", "").lower() or query_lower in breed.get("name_es", "").lower():
            results.append(breed)
            continue
        
        temperament = breed.get("temperament", [])
        if any(query_lower in t.lower() for t in temperament):
            results.append(breed)
            continue
    
    return {
        "success": True,
        "query": q,
        "count": len(results),
        "breeds": [{
            "id": b.get("id"),
            "name": b.get("name"),
            "name_es": b.get("name_es"),
            "size_category": b.get("size_category"),
            "temperament": b.get("temperament", [])
        } for b in results[:20]]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
