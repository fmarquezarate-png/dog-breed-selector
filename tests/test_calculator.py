"""
Tests para el modulo calculator
"""

import pytest
import json
import os
import sys

# Anadir src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from calculator import CompatibilityCalculator, load_data, BreedScore


@pytest.fixture
def sample_breeds():
    """Datos de prueba de razas"""
    return [
        {
            "id": "test_breed_1",
            "name": "Test Breed 1",
            "name_es": "Raza de Prueba 1",
            "size_category": "small",
            "energy_level": 3,
            "exercise_needs_daily_min": 30,
            "exercise_needs_daily_max": 60,
            "apartment_friendly": 4,
            "good_with_children": 4,
            "grooming_needs": 3,
            "shedding": 3,
            "hypoallergenic": True,
            "good_for_first_time": 4,
            "barking_level": 2,
            "health_issues": 2,
            "special_needs": "Ninguna"
        },
        {
            "id": "test_breed_2",
            "name": "Test Breed 2",
            "name_es": "Raza de Prueba 2",
            "size_category": "large",
            "energy_level": 5,
            "exercise_needs_daily_min": 90,
            "exercise_needs_daily_max": 120,
            "apartment_friendly": 2,
            "good_with_children": 3,
            "grooming_needs": 4,
            "shedding": 4,
            "hypoallergenic": False,
            "good_for_first_time": 2,
            "barking_level": 4,
            "health_issues": 4,
            "special_needs": "Ejercicio intensivo"
        }
    ]


@pytest.fixture
def sample_questions():
    """Datos de prueba de preguntas"""
    return {
        "categories": {
            "hogar": {"name": "Perfil del Hogar", "weight": 0.15, "questions": []},
            "estilo_vida": {"name": "Estilo de Vida", "weight": 0.20, "questions": []},
            "experiencia": {"name": "Experiencia", "weight": 0.10, "questions": []},
            "preferencias_fisicas": {"name": "Preferencias Fisicas", "weight": 0.12, "questions": []},
            "salud": {"name": "Salud", "weight": 0.15, "questions": []},
            "personalidad": {"name": "Personalidad", "weight": 0.18, "questions": []},
            "cuidados": {"name": "Cuidados", "weight": 0.10, "questions": []},
            "objetivos": {"name": "Objetivos", "weight": 0.10, "questions": []}
        }
    }


@pytest.fixture
def calculator(sample_breeds, sample_questions):
    """Calculador de prueba"""
    return CompatibilityCalculator(sample_breeds, sample_questions)


def test_calculator_initialization(calculator):
    """Test de inicializacion del calculador"""
    assert len(calculator.breeds) == 2
    assert len(calculator.category_weights) == 8
    assert abs(sum(calculator.category_weights.values()) - 1.0) < 0.01


def test_size_match_perfect(calculator):
    """Test de coincidencia perfecta de tamano"""
    user_prefs = {"preferred_size": "small"}
    breed = {"size_category": "small"}
    
    score = calculator.calculate_size_match(user_prefs, breed)
    assert score == 100


def test_size_match_mismatch(calculator):
    """Test de no coincidencia de tamano"""
    user_prefs = {"preferred_size": "mini"}
    breed = {"size_category": "giant"}
    
    score = calculator.calculate_size_match(user_prefs, breed)
    assert score < 50


def test_energy_match(calculator):
    """Test de coincidencia de energia"""
    user_prefs = {"desired_energy": "medium"}
    breed = {"energy_level": 3}
    
    score = calculator.calculate_energy_match(user_prefs, breed)
    assert score == 100


def test_apartment_match(calculator):
    """Test de compatibilidad con apartamento"""
    user_prefs = {"housing_type": "apartamento_mediano"}
    breed = {"apartment_friendly": 5}
    
    score = calculator.calculate_apartment_match(user_prefs, breed)
    assert score == 100


def test_hypoallergenic_match(calculator):
    """Test de compatibilidad hipoalergenica"""
    user_prefs = {"household_allergies": "severe"}
    breed_hypo = {"hypoallergenic": True}
    breed_not_hypo = {"hypoallergenic": False}
    
    score_hypo = calculator.calculate_hypoallergenic_match(user_prefs, breed_hypo)
    score_not_hypo = calculator.calculate_hypoallergenic_match(user_prefs, breed_not_hypo)
    
    assert score_hypo == 100
    assert score_not_hypo == 20


def test_dealbreakers(calculator):
    """Test de dealbreakers"""
    user_prefs = {
        "household_allergies": "severe",
        "housing_type": "apartamento_pequeno",
        "first_time_owner": True
    }
    breed = {
        "hypoallergenic": False,
        "size_category": "giant",
        "good_for_first_time": 2
    }
    
    dealbreakers = calculator.get_dealbreakers(user_prefs, breed)
    assert len(dealbreakers) == 3
    assert "No hipoalergenico" in dealbreakers
    assert "Tamano inadecuado" in dealbreakers
    assert "No recomendada para primerizos" in dealbreakers


def test_score_breed(calculator):
    """Test de puntuacion completa de raza"""
    user_prefs = {
        "housing_type": "casa_mediana",
        "housing_size_sqm": 100,
        "has_garden": "yes_medium",
        "preferred_size": "small",
        "desired_energy": "medium",
        "daily_exercise_time_minutes": 60,
        "shedding_tolerance": "medium",
        "grooming_willingness": "moderate",
        "household_allergies": "none",
        "first_time_owner": False,
        "barking_tolerance": "medium",
        "kids_compatibility": "important",
        "vet_budget_monthly": "medium"
    }
    
    breed = calculator.breeds[0]
    score = calculator.score_breed(user_prefs, breed)
    
    assert isinstance(score, BreedScore)
    assert 0 <= score.match_percentage <= 100
    assert score.breed_id == "test_breed_1"


def test_score_all_breeds_sorted(calculator):
    """Test de que los scores esten ordenados"""
    user_prefs = {
        "housing_type": "casa_mediana",
        "housing_size_sqm": 100,
        "has_garden": "yes_medium",
        "preferred_size": "no_preference",
        "desired_energy": "medium",
        "daily_exercise_time_minutes": 60,
        "shedding_tolerance": "medium",
        "grooming_willingness": "moderate",
        "household_allergies": "none",
        "first_time_owner": False,
        "barking_tolerance": "medium",
        "kids_compatibility": "not_important",
        "vet_budget_monthly": "medium"
    }
    
    scores = calculator.score_all_breeds(user_prefs)
    
    assert len(scores) == 2
    assert scores[0].match_percentage >= scores[1].match_percentage


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
