"""
Ejemplo de uso del Dog Breed Selector

Este script demuestra cómo usar el sistema de recomendación
para obtener razas de perro ideales basadas en preferencias personales.
"""

import sys
import os

# Añadir src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from breeds import load_breeds, load_questions
from calculator import CompatibilityCalculator


def main():
    print("="*60)
    print("🐕 DOG BREED SELECTOR - Ejemplo de Uso")
    print("="*60)
    
    # Cargar datos
    print("\n📂 Cargando datos...")
    breeds_data = load_breeds()
    questions_data = load_questions()
    print(f"   ✓ {len(breeds_data)} razas cargadas")
    print(f"   ✓ {len(questions_data.get('categories', {}))} categorías de preguntas")
    
    # Inicializar calculador
    calculator = CompatibilityCalculator(breeds_data, questions_data)
    
    # Ejemplo 1: Persona joven en apartamento
    print("\n" + "="*60)
    print("📝 EJEMPLO 1: Persona joven en apartamento")
    print("="*60)
    
    user_1 = {
        "housing_type": "apartamento_mediano",
        "housing_size_sqm": 75,
        "has_garden": "terrace",
        "geographic_location": "mediterraneo",
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
    
    print("\nPerfil:")
    print("   • Apartamento mediano (75m2) con terraza")
    print("   • Pareja joven sin niños")
    print("   • Trabajo oficina 8h")
    print("   • Actividad moderada (45 min ejercicio/día)")
    print("   • Primerizo, tolerancia baja a pelo/ladridos")
    
    scores_1 = calculator.score_all_breeds(user_1)
    
    print("\n🏆 Top 5 Razas Recomendadas:")
    for i, score in enumerate(scores_1[:5], 1):
        print(f"\n   {i}. {score.breed_name_es} - {score.match_percentage}% compatible")
        print(f"      Características: {', '.join(score.key_traits)}")
        if score.dealbreakers:
            print(f"      ⚠️  Consideraciones: {', '.join(score.dealbreakers)}")
    
    # Ejemplo 2: Familia con niños en casa
    print("\n" + "="*60)
    print("📝 EJEMPLO 2: Familia con niños en casa")
    print("="*60)
    
    user_2 = {
        "housing_type": "casa_mediana",
        "housing_size_sqm": 150,
        "has_garden": "yes_medium",
        "geographic_location": "continental",
        "household_size": 4,
        "has_children": "yes_4_8",
        "activity_level": "active",
        "daily_exercise_time_minutes": 90,
        "work_schedule": "home_partial",
        "dog_experience": "intermediate",
        "first_time_owner": False,
        "preferred_size": "medium",
        "shedding_tolerance": "medium",
        "grooming_willingness": "moderate",
        "household_allergies": "none",
        "desired_energy": "high",
        "barking_tolerance": "medium",
        "kids_compatibility": "essential",
        "vet_budget_monthly": "high",
        "obedience_expectations": "excellent"
    }
    
    print("\nPerfil:")
    print("   • Casa mediana (150m2) con jardín")
    print("   • Familia con 2 niños (4-8 años)")
    print("   • Trabajo híbrido")
    print("   • Muy activos (90 min ejercicio/día)")
    print("   • Experiencia intermedia, niños prioritarios")
    
    scores_2 = calculator.score_all_breeds(user_2)
    
    print("\n🏆 Top 5 Razas Recomendadas:")
    for i, score in enumerate(scores_2[:5], 1):
        print(f"\n   {i}. {score.breed_name_es} - {score.match_percentage}% compatible")
        print(f"      Características: {', '.join(score.key_traits)}")
        if score.dealbreakers:
            print(f"      ⚠️  Consideraciones: {', '.join(score.dealbreakers)}")
    
    # Ejemplo 3: Persona mayor buscando compañero tranquilo
    print("\n" + "="*60)
    print("📝 EJEMPLO 3: Persona mayor buscando compañero tranquilo")
    print("="*60)
    
    user_3 = {
        "housing_type": "apartamento_grande",
        "housing_size_sqm": 100,
        "has_garden": "no",
        "geographic_location": "mediterraneo",
        "household_size": 1,
        "has_children": "no",
        "activity_level": "light",
        "daily_exercise_time_minutes": 30,
        "work_schedule": "home_full",
        "dog_experience": "advanced",
        "first_time_owner": False,
        "preferred_size": "small",
        "shedding_tolerance": "low",
        "grooming_willingness": "high",
        "household_allergies": "mild",
        "desired_energy": "low",
        "barking_tolerance": "none",
        "kids_compatibility": "not_important",
        "vet_budget_monthly": "high",
        "obedience_expectations": "good"
    }
    
    print("\nPerfil:")
    print("   • Apartamento grande (100m2) sin jardín")
    print("   • Persona mayor viviendo sola")
    print("   • Trabaja desde casa")
    print("   • Actividad ligera (30 min paseo/día)")
    print("   • Experiencia avanzada, alergias leves")
    
    scores_3 = calculator.score_all_breeds(user_3)
    
    print("\n🏆 Top 5 Razas Recomendadas:")
    for i, score in enumerate(scores_3[:5], 1):
        print(f"\n   {i}. {score.breed_name_es} - {score.match_percentage}% compatible")
        print(f"      Características: {', '.join(score.key_traits)}")
        if score.dealbreakers:
            print(f"      ⚠️  Consideraciones: {', '.join(score.dealbreakers)}")
    
    print("\n" + "="*60)
    print("✅ Ejemplo completado exitosamente")
    print("="*60)


if __name__ == "__main__":
    main()
