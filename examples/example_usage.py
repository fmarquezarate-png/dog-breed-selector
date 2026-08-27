"""
Ejemplo de uso del Dog Breed Selector

Este script demuestra cómo usar el sistema de recomendació´´´n
para obtener razas de perro ideales basadas en preferencias personales.
"""

import sys
import os

# Añ´´´adir src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from calculator import CompatibilityCalculator, load_data


def main():
    print("="*60)
    print("🐕 DOG BREED SELECTOR - Ejemplo de Uso")
    print("="*60)
    
    # Cargar datos
    print("\n📂 Cargando datos...")
    breeds_data, questions_data = load_data()
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
        "vet_budget_monthly": "medium"
    }
    
    print("\nPerfil:")
    print("   • Apartamento mediano (75m2) con terraza")
    print("   • Pareja joven sin niños")
    print("   • Trabajo oficina 8h")
    print("   • Actividad moderada (45 min ejercicio/dí´´a)")
    print("   • Primerizo, tolerancia baja a pelo/ladridos")
    
    scores_1 = calculator.score_all_breeds(user_1)
    
    print("\n🏆 Top 5 Razas Recomendadas:")
    for i, score in enumerate(scores_1[:5], 1):
        print(f"\n   {i}. {score.breed_name_es} - {score.match_percentage}% compatible")
        print(f"      Caracterí´´sticas: {', '.join(score.key_traits)}")
        if score.dealbreakers:
            print(f"      ⚠️  Consideraciones: {', '.join(score.dealbreakers)}")
    
    print("\n" + "="*60)
    print("✅ Ejemplo completado exitosamente")
    print("="*60)


if __name__ == "__main__":
    main()
