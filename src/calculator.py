"""Dog Breed Selector - Calculator Module"""

import json
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass


@dataclass
class BreedScore:
    """Puntuaciò´´´n de una raza para un usuario especí´´fico"""
    breed_id: str
    breed_name: str
    breed_name_es: str
    total_score: float
    category_scores: Dict[str, float]
    match_percentage: float
    key_traits: List[str]
    considerations: List[str]
    dealbreakers: List[str]


class CompatibilityCalculator:
    """Calcula la compatibilidad entre usuario y razas de perros"""
    
    def __init__(self, breeds_data: List[Dict], questions_data: Dict):
        self.breeds = breeds_data
        self.questions = questions_data
        self.category_weights = {
            cat_id: cat_data.get("weight", 0.125)
            for cat_id, cat_data in questions_data["categories"].items()
        }
    
    def calculate_size_match(self, user_prefs: Dict, breed: Dict) -> float:
        """Calcula compatibilidad de tamaño"""
        preferred_size = user_prefs.get("preferred_size", "no_preference")
        if preferred_size == "no_preference":
            return 70
        
        breed_size = breed.get("size_category", "")
        if preferred_size == breed_size:
            return 100
        
        size_order = ["mini", "small", "medium", "large", "giant"]
        try:
            pref_idx = size_order.index(preferred_size)
            breed_idx = size_order.index(breed_size)
            diff = abs(pref_idx - breed_idx)
            return max(10, 100 - (diff * 30))
        except ValueError:
            return 50
    
    def calculate_energy_match(self, user_prefs: Dict, breed: Dict) -> float:
        """Calcula compatibilidad de nivel de energí´´a"""
        user_energy = user_prefs.get("desired_energy", "medium")
        breed_energy = breed.get("energy_level", 3)
        
        energy_mapping = {"low": 1, "medium": 3, "high": 4, "very_high": 5}
        user_energy_val = energy_mapping.get(user_energy, 3)
        
        diff = abs(user_energy_val - breed_energy)
        return max(20, 100 - (diff * 20))
    
    def calculate_exercise_match(self, user_prefs: Dict, breed: Dict) -> float:
        """Calcula compatibilidad de necesidades de ejercicio"""
        user_exercise = user_prefs.get("daily_exercise_time_minutes", 60)
        breed_exercise_min = breed.get("exercise_needs_daily_min", 60)
        breed_exercise_max = breed.get("exercise_needs_daily_max", 90)
        
        if user_exercise >= breed_exercise_max:
            return 100
        if user_exercise >= breed_exercise_min:
            return 90
        return max(0, (user_exercise / breed_exercise_min) * 100)
    
    def calculate_apartment_match(self, user_prefs: Dict, breed: Dict) -> float:
        """Calcula compatibilidad para vivir en apartamento"""
        housing_type = user_prefs.get("housing_type", "casa_mediana")
        apartment_friendly = breed.get("apartment_friendly", 3)
        
        apartment_types = ["apartamento_pequeno", "apartamento_mediano", "apartamento_grande"]
        if housing_type in apartment_types:
            return (apartment_friendly / 5) * 100
        return 70 + (apartment_friendly * 6)
    
    def calculate_children_match(self, user_prefs: Dict, breed: Dict) -> float:
        """Calcula compatibilidad con niños"""
        has_children = user_prefs.get("has_children", "no")
        kids_importance = user_prefs.get("kids_compatibility", "not_important")
        good_with_children = breed.get("good_with_children", 3)
        
        if has_children == "no" and kids_importance == "not_important":
            return 70
        
        importance_mapping = {"essential": 1.0, "important": 0.8, "nice_to_have": 0.5, "not_important": 0.2}
        importance = importance_mapping.get(kids_importance, 0.5)
        base_score = (good_with_children / 5) * 100
        
        return base_score * importance + 30 * (1 - importance)
    
    def calculate_grooming_match(self, user_prefs: Dict, breed: Dict) -> float:
        """Calcula compatibilidad de grooming"""
        user_grooming = user_prefs.get("grooming_willingness", "moderate")
        breed_grooming = breed.get("grooming_needs", 3)
        
        grooming_mapping = {"minimal": 1, "moderate": 3, "high": 4, "professional": 5}
        user_grooming_val = grooming_mapping.get(user_grooming, 3)
        
        if user_grooming_val >= breed_grooming:
            return 100
        return max(0, (user_grooming_val / breed_grooming) * 100)
    
    def calculate_shedding_match(self, user_prefs: Dict, breed: Dict) -> float:
        """Calcula compatibilidad de tolerancia a muda"""
        user_tolerance = user_prefs.get("shedding_tolerance", "medium")
        breed_shedding = breed.get("shedding", 3)
        
        tolerance_mapping = {"none": 1, "low": 2, "medium": 3, "high": 5}
        user_tolerance_val = tolerance_mapping.get(user_tolerance, 3)
        
        if user_tolerance_val >= breed_shedding:
            return 100
        return max(0, 100 - ((breed_shedding - user_tolerance_val) * 25))
    
    def calculate_hypoallergenic_match(self, user_prefs: Dict, breed: Dict) -> float:
        """Calcula compatibilidad para alé´´rgicos"""
        allergies = user_prefs.get("household_allergies", "none")
        is_hypoallergenic = breed.get("hypoallergenic", False)
        
        if allergies == "none":
            return 70
        if allergies in ["moderate", "severe"]:
            return 100 if is_hypoallergenic else 20
        if allergies == "mild":
            return 90 if is_hypoallergenic else 50
        return 70
    
    def calculate_first_time_match(self, user_prefs: Dict, breed: Dict) -> float:
        """Calcula compatibilidad para due˜nos primerizos"""
        is_first_time = user_prefs.get("first_time_owner", False)
        good_for_first_time = breed.get("good_for_first_time", 3)
        
        if is_first_time:
            return (good_for_first_time / 5) * 100
        return 70
    
    def calculate_barking_match(self, user_prefs: Dict, breed: Dict) -> float:
        """Calcula compatibilidad de tolerancia a ladridos"""
        user_tolerance = user_prefs.get("barking_tolerance", "medium")
        breed_barking = breed.get("barking_level", 3)
        
        tolerance_mapping = {"none": 1, "low": 2, "medium": 3, "high": 5}
        user_tolerance_val = tolerance_mapping.get(user_tolerance, 3)
        
        if user_tolerance_val >= breed_barking:
            return 100
        return max(0, 100 - ((breed_barking - user_tolerance_val) * 30))
    
    def calculate_health_budget_match(self, user_prefs: Dict, breed: Dict) -> float:
        """Calcula compatibilidad de presupuesto para salud"""
        user_budget = user_prefs.get("vet_budget_monthly", "medium")
        breed_health_issues = breed.get("health_issues", 3)
        
        budget_mapping = {"low": 1, "medium": 3, "high": 4, "unlimited": 5}
        user_budget_val = budget_mapping.get(user_budget, 3)
        
        if user_budget_val >= breed_health_issues:
            return 100
        return max(0, (user_budget_val / breed_health_issues) * 100)
    
    def calculate_space_match(self, user_prefs: Dict, breed: Dict) -> float:
        """Calcula compatibilidad de espacio"""
        housing_size = user_prefs.get("housing_size_sqm", 100)
        has_garden = user_prefs.get("has_garden", "no")
        breed_size = breed.get("size_category", "medium")
        
        space_requirements = {"mini": 30, "small": 50, "medium": 80, "large": 120, "giant": 150}
        required_space = space_requirements.get(breed_size, 80)
        
        garden_bonus = {"yes_large": 20, "yes_medium": 20, "yes_small": 10, "terrace": 10}.get(has_garden, 0)
        
        if housing_size >= required_space:
            return min(100, 80 + garden_bonus)
        return max(0, (housing_size / required_space) * 80 + garden_bonus)
    
    def calculate_category_score(self, category_id: str, user_prefs: Dict, breed: Dict) -> float:
        """Calcula score para una categorí´´a especí´´fica"""
        scores = []
        
        if category_id == "hogar":
            scores = [self.calculate_space_match(user_prefs, breed), self.calculate_apartment_match(user_prefs, breed)]
        elif category_id == "estilo_vida":
            scores = [self.calculate_energy_match(user_prefs, breed), self.calculate_exercise_match(user_prefs, breed)]
        elif category_id == "experiencia":
            scores = [self.calculate_first_time_match(user_prefs, breed), self.calculate_barking_match(user_prefs, breed)]
        elif category_id == "preferencias_fisicas":
            scores = [self.calculate_size_match(user_prefs, breed), self.calculate_shedding_match(user_prefs, breed), self.calculate_grooming_match(user_prefs, breed)]
        elif category_id == "salud":
            scores = [self.calculate_hypoallergenic_match(user_prefs, breed), self.calculate_health_budget_match(user_prefs, breed)]
        elif category_id == "personalidad":
            scores = [self.calculate_energy_match(user_prefs, breed), self.calculate_children_match(user_prefs, breed)]
        elif category_id == "cuidados":
            scores = [self.calculate_grooming_match(user_prefs, breed), self.calculate_shedding_match(user_prefs, breed)]
        elif category_id == "objetivos":
            scores = [self.calculate_first_time_match(user_prefs, breed)]
        
        return sum(scores) / len(scores) if scores else 70
    
    def calculate_total_score(self, user_prefs: Dict, breed: Dict) -> Tuple[float, Dict[str, float]]:
        """Calcula score total de compatibilidad"""
        category_scores = {}
        weighted_sum = 0
        
        for cat_id, weight in self.category_weights.items():
            score = self.calculate_category_score(cat_id, user_prefs, breed)
            category_scores[cat_id] = score
            weighted_sum += score * weight
        
        return weighted_sum, category_scores
    
    def get_dealbreakers(self, user_prefs: Dict, breed: Dict) -> List[str]:
        """Obtiene incompatibilidades crí´´ticas"""
        dealbreakers = []
        
        if user_prefs.get("household_allergies") in ["severe", "moderate"] and not breed.get("hypoallergenic", False):
            dealbreakers.append("No hipoalergé´´nico")
        
        if user_prefs.get("housing_type") == "apartamento_pequeno" and breed.get("size_category") in ["large", "giant"]:
            dealbreakers.append("Tama˜no inadecuado")
        
        if user_prefs.get("first_time_owner", False) and breed.get("good_for_first_time", 3) <= 2:
            dealbreakers.append("No recomendada para primerizos")
        
        return dealbreakers
    
    def score_breed(self, user_prefs: Dict, breed: Dict) -> BreedScore:
        """Calcula score completo para una raza"""
        total_score, category_scores = self.calculate_total_score(user_prefs, breed)
        dealbreakers = self.get_dealbreakers(user_prefs, breed)
        penalty = len(dealbreakers) * 15
        final_score = max(0, total_score - penalty)
        
        return BreedScore(
            breed_id=breed.get("id", ""),
            breed_name=breed.get("name", ""),
            breed_name_es=breed.get("name_es", ""),
            total_score=round(total_score, 1),
            category_scores={k: round(v, 1) for k, v in category_scores.items()},
            match_percentage=round(final_score, 1),
            key_traits=[f"{breed.get('size_category', 'medium').title()} size", f"Energy: {breed.get('energy_level', 3)}/5"],
            considerations=[breed.get("special_needs", "")],
            dealbreakers=dealbreakers
        )
    
    def score_all_breeds(self, user_prefs: Dict) -> List[BreedScore]:
        """Calcula scores para todas las razas"""
        scores = [self.score_breed(user_prefs, breed) for breed in self.breeds]
        scores.sort(key=lambda x: x.match_percentage, reverse=True)
        return scores


def load_data():
    """Carga datos desde archivos JSON"""
    with open("database/breed_characteristics.json", "r", encoding="utf-8") as f:
        breeds_data = json.load(f)["breeds"]
    with open("questionnaire/questions.json", "r", encoding="utf-8") as f:
        questions_data = json.load(f)
    return breeds_data, questions_data


if __name__ == "__main__":
    breeds_data, questions_data = load_data()
    calculator = CompatibilityCalculator(breeds_data, questions_data)
    
    example_prefs = {
        "housing_type": "apartamento_mediano", "housing_size_sqm": 85,
        "has_garden": "terrace", "daily_exercise_time_minutes": 60,
        "dog_experience": "basic", "first_time_owner": True,
        "preferred_size": "small", "shedding_tolerance": "low",
        "grooming_willingness": "moderate", "household_allergies": "none",
        "desired_energy": "medium", "barking_tolerance": "low",
        "kids_compatibility": "not_important", "vet_budget_monthly": "medium"
    }
    
    scores = calculator.score_all_breeds(example_prefs)
    print("Top 10 razas recomendadas:\n")
    for i, score in enumerate(scores[:10], 1):
        print(f"{i}. {score.breed_name_es} - {score.match_percentage}% compatible")
