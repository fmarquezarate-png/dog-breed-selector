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

# Importar el motor de recomendación
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from breeds import load_breeds, load_questions
from calculator import CompatibilityCalculator

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
breeds_data = load_breeds()
questions_data = load_questions()
calculator = CompatibilityCalculator(breeds_data, questions_data)
breeds_by_id = {b.id: b for b in breeds_data}


# Modelos Pydantic
class QuestionnaireResponse(BaseModel):
    """Respuesta del cuestionario del usuario.

    Todos los campos son opcionales: `CompatibilityCalculator` rellena lo
    que falte con los valores por defecto de `questionnaire/questions.json`,
    así que un perfil parcial no debe rechazarse con un 422.
    """
    housing_type: Optional[str] = None
    housing_size_sqm: Optional[int] = Field(None, ge=20, le=500)
    has_garden: Optional[str] = None
    geographic_location: Optional[str] = None
    household_size: Optional[int] = Field(None, ge=1, le=12)
    has_children: Optional[str] = None
    activity_level: Optional[str] = None
    daily_exercise_time_minutes: Optional[int] = Field(None, ge=10, le=300)
    work_schedule: Optional[str] = None
    dog_experience: Optional[str] = None
    first_time_owner: Optional[bool] = None
    preferred_size: Optional[str] = None
    shedding_tolerance: Optional[str] = None
    drooling_tolerance: Optional[str] = None
    grooming_willingness: Optional[str] = None
    household_allergies: Optional[str] = None
    desired_energy: Optional[str] = None
    barking_tolerance: Optional[str] = None
    kids_compatibility: Optional[str] = None
    other_pets: Optional[str] = None
    vet_budget_monthly: Optional[str] = None
    obedience_expectations: Optional[str] = None
    main_purpose: Optional[str] = None

    def to_answers(self) -> Dict[str, Any]:
        return {k: v for k, v in self.model_dump().items() if v is not None}


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
        answers = response.to_answers()
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
    results = list(breeds_data)

    if size:
        results = [b for b in results if b.size_category == size]

    if hypoallergenic is not None:
        results = [b for b in results if b.hypoallergenic == hypoallergenic]

    if apartment_friendly_min is not None:
        results = [b for b in results if b["apartment_friendly"] >= apartment_friendly_min]

    return {
        "success": True,
        "count": len(results),
        "breeds": [{
            "id": b.id,
            "name": b.name,
            "name_es": b.name_es,
            "size_category": b.size_category,
            "hypoallergenic": b.hypoallergenic,
            "apartment_friendly": b["apartment_friendly"],
            "energy_level": b["energy_level"],
            "good_with_children": b["good_with_children"]
        } for b in results[:limit]]
    }


@app.get("/api/breeds/{breed_id}")
async def get_breed(breed_id: str):
    """Obtener detalles de una raza especifica"""
    breed = breeds_by_id.get(breed_id)
    if breed is None:
        raise HTTPException(status_code=404, detail=f"Raza '{breed_id}' no encontrada")
    return {"success": True, "breed": breed.to_dict()}


@app.get("/api/search")
async def search_breeds(q: str = Query(..., min_length=2, description="Termino de busqueda")):
    """Buscar razas por nombre o caracteristicas"""
    query_lower = q.lower()
    results = []

    for breed in breeds_data:
        if query_lower in breed.name.lower() or query_lower in breed.name_es.lower():
            results.append(breed)
            continue

        if any(query_lower in t.lower() for t in breed.temperament):
            results.append(breed)
            continue

    return {
        "success": True,
        "query": q,
        "count": len(results),
        "breeds": [{
            "id": b.id,
            "name": b.name,
            "name_es": b.name_es,
            "size_category": b.size_category,
            "temperament": b.temperament
        } for b in results[:20]]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
