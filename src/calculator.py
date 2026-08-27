"""Motor de compatibilidad usuario-raza.

Cada `match_*` devuelve un score 0-100 para una dimensión concreta. Las
dimensiones se agrupan en las categorías del cuestionario, y las categorías
se combinan con los pesos definidos en `questionnaire/questions.json`.

Invariantes que el motor garantiza (y que los tests comprueban):

* Toda función `match_*` devuelve un valor en [0, 100].
* `total_score` está en [0, 100] sea cual sea el peso de las categorías:
  los pesos se re-normalizan por su suma, así que editarlos en el JSON no
  puede sacar el score de escala.
* `match_percentage` = `total_score` menos las penalizaciones, acotado a
  [0, 100].
* El scoring es puro: mismas entradas, mismo resultado. No lee ficheros ni
  muta sus argumentos.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Mapping, Sequence, Tuple

from breeds import SIZE_ORDER, Breed, default_answers

#: Puntos que resta cada incompatibilidad crítica.
DEALBREAKER_PENALTY = 15.0

#: Score neutro cuando el usuario no expresa preferencia sobre una dimensión.
#: No es 100 (no premiamos la indiferencia) ni 50 (no la penalizamos).
NEUTRAL = 70.0


def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


@dataclass
class BreedScore:
    """Resultado del scoring de una raza para un perfil de usuario."""

    breed_id: str
    breed_name: str
    breed_name_es: str
    total_score: float
    category_scores: Dict[str, float]
    dimension_scores: Dict[str, float]
    match_percentage: float
    key_traits: List[str]
    considerations: List[str]
    dealbreakers: List[str]
    rating: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return dict(self.__dict__)


#: Escala de interpretación documentada en docs/methodology.md.
RATINGS: Sequence[Tuple[float, str]] = (
    (90, "Excelente match"),
    (80, "Muy buen match"),
    (70, "Buen match"),
    (60, "Match moderado"),
    (0, "Match bajo"),
)


def rating_for(score: float) -> str:
    for threshold, label in RATINGS:
        if score >= threshold:
            return label
    return RATINGS[-1][1]


# --------------------------------------------------------------------------
# Mapas de respuesta -> valor numérico en escala 1-5
# --------------------------------------------------------------------------

ENERGY_LEVELS = {"low": 1, "medium": 3, "high": 4, "very_high": 5}
ACTIVITY_LEVELS = {
    "sedentary": 1,
    "light": 2,
    "moderate": 3,
    "active": 4,
    "very_active": 5,
}
TOLERANCE_LEVELS = {"none": 1, "low": 2, "medium": 3, "high": 5}
GROOMING_LEVELS = {"minimal": 1, "moderate": 3, "high": 4, "professional": 5}
BUDGET_LEVELS = {"low": 1, "medium": 3, "high": 4, "unlimited": 5}
EXPERIENCE_LEVELS = {
    "none": 1,
    "basic": 2,
    "intermediate": 3,
    "advanced": 4,
    "expert": 5,
}
OBEDIENCE_LEVELS = {"basic": 2, "good": 3, "excellent": 4, "competition": 5}
KIDS_IMPORTANCE = {
    "essential": 1.0,
    "important": 0.8,
    "nice_to_have": 0.5,
    "not_important": 0.2,
}
GARDEN_BONUS = {
    "yes_large": 20,
    "yes_medium": 15,
    "yes_small": 10,
    "terrace": 5,
    "no": 0,
}
#: m² de referencia que pide cada tamaño para vivir cómodo.
SPACE_REQUIREMENTS = {"mini": 30, "small": 50, "medium": 80, "large": 120, "giant": 150}
APARTMENT_TYPES = {
    "apartamento_pequeno",
    "apartamento_mediano",
    "apartamento_grande",
}
#: Horas al día que el perro pasaría solo, por horario laboral.
HOURS_ALONE = {
    "home_full": 1,
    "home_partial": 4,
    "office_8h": 9,
    "office_10h_plus": 11,
    "frequent_travel": 12,
}
#: Tolerancia (al frío, al calor) que exige cada clima, en escala 1-5.
#: Calibrado contra el rango real del CSV: `heat_tolerance` no pasa de 4, así
#: que exigir 5 marcaría a casi todas las razas y el aviso perdería valor.
CLIMATE_DEMANDS = {
    "frio": (5, 1),
    "continental": (4, 2),
    "atlantico": (3, 2),
    "mediterraneo": (2, 3),
    "calido": (1, 4),
}
#: Rasgos de la raza que más importan según el propósito declarado.
PURPOSE_TRAITS = {
    "companion": {"good_with_children": 0.3, "trainability": 0.3, "energy_level": 0.4},
    "family": {"good_with_children": 0.6, "trainability": 0.4},
    "sport": {"energy_level": 0.5, "trainability": 0.5},
    "guard": {"protectiveness": 0.6, "trainability": 0.4},
    "therapy": {"good_with_children": 0.4, "trainability": 0.6},
}
#: Para "companion", un perro menos enérgico puntúa mejor.
PURPOSE_INVERTED = {("companion", "energy_level")}


def _level(mapping: Mapping[str, int], value: Any, fallback: int) -> int:
    """Traduce una respuesta a escala 1-5, tolerando valores desconocidos."""
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return int(clamp(float(value), 1, 5))
    return mapping.get(str(value), fallback)


def _as_bool(value: Any, fallback: bool = False) -> bool:
    """Los formularios HTML mandan `"true"`/`"false"` como texto."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        if value.lower() in {"true", "1", "yes", "si", "sí"}:
            return True
        if value.lower() in {"false", "0", "no", ""}:
            return False
    return fallback


def _as_number(value: Any, fallback: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def _tolerance_match(user_level: int, breed_level: int, step: float) -> float:
    """Patrón común: si el usuario tolera tanto o más de lo que la raza
    exige, 100; si no, baja `step` puntos por cada punto de exceso."""
    if user_level >= breed_level:
        return 100.0
    return clamp(100 - (breed_level - user_level) * step)


def _capacity_match(user_level: int, breed_level: int) -> float:
    """Patrón común para 'capacidad del usuario vs exigencia de la raza'."""
    if user_level >= breed_level:
        return 100.0
    return clamp((user_level / breed_level) * 100)


# --------------------------------------------------------------------------
# Dimensiones
# --------------------------------------------------------------------------


def match_size(prefs: Mapping[str, Any], breed: Breed) -> float:
    preferred = prefs.get("preferred_size", "no_preference")
    if preferred == "no_preference":
        return NEUTRAL
    if preferred == breed.size_category:
        return 100.0
    try:
        distance = abs(
            SIZE_ORDER.index(preferred) - SIZE_ORDER.index(breed.size_category)
        )
    except ValueError:
        return 50.0
    return clamp(100 - distance * 30, low=10)


def match_energy(prefs: Mapping[str, Any], breed: Breed) -> float:
    """Compara la energía deseada con la de la raza.

    Asimétrico a propósito: una raza *más* enérgica de lo que el usuario
    quiere es un problema mayor (destructividad, ansiedad) que una más
    tranquila, que como mucho decepciona.
    """
    desired = _level(ENERGY_LEVELS, prefs.get("desired_energy"), 3)
    activity = _level(ACTIVITY_LEVELS, prefs.get("activity_level"), 3)
    # El nivel de actividad real matiza lo que el usuario dice desear.
    target = (desired * 2 + activity) / 3
    diff = breed["energy_level"] - target
    penalty = diff * 22 if diff > 0 else abs(diff) * 14
    return clamp(100 - penalty)


def match_exercise(prefs: Mapping[str, Any], breed: Breed) -> float:
    available = _as_number(prefs.get("daily_exercise_time_minutes"), 60)
    needed_min = max(1.0, float(breed.exercise_needs_daily_min))
    needed_max = max(needed_min, float(breed.exercise_needs_daily_max))
    if available >= needed_max:
        return 100.0
    if available >= needed_min:
        return 90.0
    return clamp((available / needed_min) * 100)


def match_alone_time(prefs: Mapping[str, Any], breed: Breed) -> float:
    """Cuánto aguanta la raza el tiempo que el usuario pasa fuera.

    El CSV no tiene una columna "tolerancia a la soledad", así que se
    estima con los dos rasgos que mejor la predicen: una raza muy enérgica
    y muy ladradora sola muchas horas acaba en ansiedad por separación y en
    quejas de los vecinos.
    """
    hours = HOURS_ALONE.get(str(prefs.get("work_schedule")), 9)
    strain = (breed["energy_level"] + breed["barking_level"]) / 2
    if hours <= 4:
        return 100.0
    # De 4 h en adelante, cada hora extra pesa según lo exigente que sea la raza.
    return clamp(100 - (hours - 4) * (strain * 2.2))


def match_apartment(prefs: Mapping[str, Any], breed: Breed) -> float:
    """`apartment_friendly` mezcla dos cosas distintas: tamaño/ruido (fijos)
    y necesidad de actividad (no lo es). Un Border Collie que recibe sus
    90-120 min diarios vive perfectamente en un piso; el rasgo crudo del
    CSV lo penaliza igual que si se quedara todo el día sin salir. Se
    mezcla con `match_exercise` para que ese compromiso cuente.
    """
    housing = str(prefs.get("housing_type", "casa_mediana"))
    if housing in APARTMENT_TYPES:
        base = clamp((breed["apartment_friendly"] / 5) * 100)
        exercise_met = match_exercise(prefs, breed)
        return clamp(base * 0.6 + exercise_met * 0.4)
    # En una casa, que la raza sea poco apta para piso deja de ser relevante.
    return 100.0


def match_space(prefs: Mapping[str, Any], breed: Breed) -> float:
    size_sqm = _as_number(prefs.get("housing_size_sqm"), 100)
    garden = str(prefs.get("has_garden", "no"))
    required = SPACE_REQUIREMENTS.get(breed.size_category, 80)
    bonus = GARDEN_BONUS.get(garden, 0)
    base = 80.0 if size_sqm >= required else (size_sqm / required) * 80
    return clamp(base + bonus)


def match_climate(prefs: Mapping[str, Any], breed: Breed) -> float:
    """Un Husky en Sevilla y un galgo pelón en Burgos son errores caros."""
    cold_needed, heat_needed = CLIMATE_DEMANDS.get(
        str(prefs.get("geographic_location")), (3, 3)
    )
    cold_gap = max(0, cold_needed - breed["cold_tolerance"])
    heat_gap = max(0, heat_needed - breed["heat_tolerance"])
    return clamp(100 - (cold_gap + heat_gap) * 15)


def match_children(prefs: Mapping[str, Any], breed: Breed) -> float:
    has_children = str(prefs.get("has_children", "no"))
    importance_key = str(prefs.get("kids_compatibility", "not_important"))
    importance = KIDS_IMPORTANCE.get(importance_key, 0.5)
    # Convivir con niños sube el listón aunque el usuario no lo marque.
    if has_children != "no":
        importance = max(importance, 0.9 if has_children == "yes_0_3" else 0.7)
    if has_children == "no" and importance_key == "not_important":
        return NEUTRAL
    base = (breed["good_with_children"] / 5) * 100
    return clamp(base * importance + NEUTRAL * (1 - importance))


def match_other_pets(prefs: Mapping[str, Any], breed: Breed) -> float:
    pets = str(prefs.get("other_pets", "none"))
    if pets == "none":
        return NEUTRAL
    scores = []
    if pets in {"dogs", "both"}:
        scores.append((breed["good_with_dogs"] / 5) * 100)
    if pets in {"cats", "both"}:
        # Un instinto de presa alto pesa tanto como la sociabilidad felina.
        cats = (breed["good_with_cats"] / 5) * 100
        scores.append(clamp(cats - (breed["prey_drive"] - 3) * 10))
    return clamp(sum(scores) / len(scores)) if scores else NEUTRAL


def match_grooming(prefs: Mapping[str, Any], breed: Breed) -> float:
    user = _level(GROOMING_LEVELS, prefs.get("grooming_willingness"), 3)
    return _capacity_match(user, breed["grooming_needs"])


def match_shedding(prefs: Mapping[str, Any], breed: Breed) -> float:
    user = _level(TOLERANCE_LEVELS, prefs.get("shedding_tolerance"), 3)
    return _tolerance_match(user, breed["shedding"], step=25)


def match_drooling(prefs: Mapping[str, Any], breed: Breed) -> float:
    user = _level(TOLERANCE_LEVELS, prefs.get("drooling_tolerance"), 3)
    return _tolerance_match(user, breed["drooling"], step=25)


def match_barking(prefs: Mapping[str, Any], breed: Breed) -> float:
    user = _level(TOLERANCE_LEVELS, prefs.get("barking_tolerance"), 3)
    return _tolerance_match(user, breed["barking_level"], step=30)


def match_hypoallergenic(prefs: Mapping[str, Any], breed: Breed) -> float:
    allergies = str(prefs.get("household_allergies", "none"))
    if allergies == "none":
        return NEUTRAL
    if allergies == "mild":
        return 90.0 if breed.hypoallergenic else 50.0
    if allergies in {"moderate", "severe"}:
        return 100.0 if breed.hypoallergenic else 20.0
    return NEUTRAL


def match_health_budget(prefs: Mapping[str, Any], breed: Breed) -> float:
    user = _level(BUDGET_LEVELS, prefs.get("vet_budget_monthly"), 3)
    return _capacity_match(user, breed["health_issues"])


def match_first_time(prefs: Mapping[str, Any], breed: Breed) -> float:
    experience = _level(EXPERIENCE_LEVELS, prefs.get("dog_experience"), 2)
    if _as_bool(prefs.get("first_time_owner"), fallback=experience <= 1):
        experience = min(experience, 2)
    if experience >= 4:
        # Con experiencia avanzada, ninguna raza queda descartada por difícil.
        return 100.0
    demand = 6 - breed["good_for_first_time"]  # 1 = fácil, 5 = exigente
    return _capacity_match(experience, demand)


def match_trainability(prefs: Mapping[str, Any], breed: Breed) -> float:
    expected = _level(OBEDIENCE_LEVELS, prefs.get("obedience_expectations"), 3)
    return _capacity_match(breed["trainability"], expected)


def match_purpose(prefs: Mapping[str, Any], breed: Breed) -> float:
    purpose = str(prefs.get("main_purpose", "companion"))
    traits = PURPOSE_TRAITS.get(purpose)
    if not traits:
        return NEUTRAL
    total = 0.0
    for trait, weight in traits.items():
        value = breed[trait]
        if (purpose, trait) in PURPOSE_INVERTED:
            value = 6 - value
        total += (value / 5) * 100 * weight
    return clamp(total / sum(traits.values()))


DimensionFn = Callable[[Mapping[str, Any], Breed], float]

#: Qué dimensiones componen cada categoría del cuestionario.
#: Cada dimensión pesa lo mismo dentro de su categoría.
CATEGORY_DIMENSIONS: Dict[str, Dict[str, DimensionFn]] = {
    "hogar": {
        "space": match_space,
        "apartment": match_apartment,
        "climate": match_climate,
    },
    "estilo_vida": {
        "energy": match_energy,
        "exercise": match_exercise,
        "alone_time": match_alone_time,
    },
    "experiencia": {
        "first_time": match_first_time,
        "trainability": match_trainability,
    },
    "preferencias_fisicas": {
        "size": match_size,
        "shedding": match_shedding,
    },
    "salud": {
        "hypoallergenic": match_hypoallergenic,
        "health_budget": match_health_budget,
    },
    "personalidad": {
        "children": match_children,
        "barking": match_barking,
        "other_pets": match_other_pets,
    },
    "cuidados": {
        "grooming": match_grooming,
        "drooling": match_drooling,
    },
    "objetivos": {
        "obedience": match_trainability,
        "purpose": match_purpose,
    },
}


class CompatibilityCalculator:
    """Calcula la compatibilidad entre un perfil de usuario y cada raza."""

    def __init__(self, breeds: Sequence[Breed], questions: Mapping[str, Any]):
        self.breeds = list(breeds)
        self.questions = questions
        raw_weights = {
            cat_id: float(cat.get("weight", 0))
            for cat_id, cat in questions["categories"].items()
            if cat_id in CATEGORY_DIMENSIONS
        }
        total = sum(raw_weights.values())
        if total <= 0:
            raise ValueError("Los pesos de categoría deben sumar más de 0")
        # Re-normalizar es lo que garantiza que el score total sea 0-100
        # aunque alguien edite los pesos del JSON y no sumen 1.
        self.category_weights = {k: v / total for k, v in raw_weights.items()}
        self._defaults = default_answers(questions)

    def normalize_prefs(self, prefs: Mapping[str, Any]) -> Dict[str, Any]:
        """Rellena con los defaults del cuestionario lo que el usuario no
        haya respondido, para que un perfil parcial no cambie de sentido."""
        merged = dict(self._defaults)
        merged.update({k: v for k, v in prefs.items() if v not in (None, "")})
        return merged

    def dimension_scores(
        self, prefs: Mapping[str, Any], breed: Breed
    ) -> Dict[str, float]:
        return {
            name: fn(prefs, breed)
            for dimensions in CATEGORY_DIMENSIONS.values()
            for name, fn in dimensions.items()
        }

    def category_score(
        self, category_id: str, prefs: Mapping[str, Any], breed: Breed
    ) -> float:
        dimensions = CATEGORY_DIMENSIONS.get(category_id)
        if not dimensions:
            return NEUTRAL
        scores = [fn(prefs, breed) for fn in dimensions.values()]
        return sum(scores) / len(scores)

    def alignment_multiplier(self, prefs: Mapping[str, Any], breed: Breed) -> float:
        """Corrige el punto ciego de promediar por categorías: un desajuste
        grave en UNA dimensión (p.ej. pedir "gigante" y recibir un Cocker)
        se diluye a un puñado de puntos cuando solo pesa como 1/8 de 1
        categoría entre 8. `preferred_size` y `desired_energy` son
        preferencias explícitas y difíciles de compensar en la vida real
        (un piso no se hace más grande, un perro gigante no se hace mini),
        así que actúan como multiplicador sobre el score entero en vez de
        sumar como una entrada más al promedio.
        """
        size_score = match_size(prefs, breed)
        energy_score = match_energy(prefs, breed)
        # Rango elegido para que un desajuste total corte el score a más de
        # la mitad, pero "sin preferencia" (score=NEUTRAL=70) apenas reste.
        size_factor = 0.55 + 0.45 * (size_score / 100)
        energy_factor = 0.75 + 0.25 * (energy_score / 100)
        return size_factor * energy_factor

    def total_score(
        self, prefs: Mapping[str, Any], breed: Breed
    ) -> Tuple[float, Dict[str, float]]:
        category_scores = {
            cat_id: self.category_score(cat_id, prefs, breed)
            for cat_id in self.category_weights
        }
        weighted = sum(
            score * self.category_weights[cat_id]
            for cat_id, score in category_scores.items()
        )
        weighted *= self.alignment_multiplier(prefs, breed)
        return clamp(weighted), category_scores

    def dealbreakers(self, prefs: Mapping[str, Any], breed: Breed) -> List[str]:
        """Incompatibilidades críticas. Cada una resta DEALBREAKER_PENALTY."""
        found: List[str] = []

        if (
            str(prefs.get("household_allergies")) in {"moderate", "severe"}
            and not breed.hypoallergenic
        ):
            found.append("No es hipoalergénica y hay alergias en el hogar")

        if (
            str(prefs.get("housing_type")) == "apartamento_pequeno"
            and breed.size_category in {"large", "giant"}
        ):
            found.append("Demasiado grande para un apartamento pequeño")

        experience = _level(EXPERIENCE_LEVELS, prefs.get("dog_experience"), 2)
        if (
            _as_bool(prefs.get("first_time_owner"), fallback=experience <= 1)
            and breed["good_for_first_time"] <= 2
        ):
            found.append("No recomendada para dueños primerizos")

        # El 4º dealbreaker documentado en methodology.md, que faltaba.
        available = _as_number(prefs.get("daily_exercise_time_minutes"), 60)
        if available < breed.exercise_needs_daily_min * 0.6:
            found.append(
                f"Necesita al menos {breed.exercise_needs_daily_min} min "
                "de ejercicio al día"
            )

        if (
            str(prefs.get("has_children")) == "yes_0_3"
            and breed["good_with_children"] <= 2
        ):
            found.append("Poco tolerante con niños muy pequeños")

        return found

    def considerations(self, prefs: Mapping[str, Any], breed: Breed) -> List[str]:
        """Avisos que no descalifican pero conviene saber antes de decidir."""
        notes: List[str] = []
        if breed.special_needs:
            notes.append(breed.special_needs)
        if breed["grooming_needs"] >= 4:
            notes.append("Requiere cepillado frecuente o peluquería profesional")
        if breed["shedding"] >= 4:
            notes.append("Suelta bastante pelo")
        if breed["barking_level"] >= 4:
            notes.append("Tiende a ladrar")
        if breed["drooling"] >= 4:
            notes.append("Babea")
        if breed["wanderlust"] >= 4:
            notes.append("Tendencia a escaparse: necesita vallado seguro")
        if breed["prey_drive"] >= 4 and str(prefs.get("other_pets")) in {
            "cats",
            "both",
        }:
            notes.append(
                "Instinto de presa alto: la convivencia con gatos exige trabajo"
            )
        if breed["health_issues"] >= 4:
            notes.append("Raza con predisposición a problemas de salud")
        cold_needed, heat_needed = CLIMATE_DEMANDS.get(
            str(prefs.get("geographic_location")), (3, 3)
        )
        if breed["heat_tolerance"] < heat_needed:
            notes.append("Lleva mal el calor de tu zona")
        if breed["cold_tolerance"] < cold_needed:
            notes.append("Lleva mal el frío de tu zona")
        # dict.fromkeys preserva el orden y elimina duplicados.
        return list(dict.fromkeys(n for n in notes if n))

    def key_traits(self, breed: Breed) -> List[str]:
        size_labels = {
            "mini": "Tamaño mini",
            "small": "Tamaño pequeño",
            "medium": "Tamaño mediano",
            "large": "Tamaño grande",
            "giant": "Tamaño gigante",
        }
        energy_labels = {
            1: "Muy tranquilo",
            2: "Tranquilo",
            3: "Energía media",
            4: "Enérgico",
            5: "Muy enérgico",
        }
        traits = [
            size_labels.get(breed.size_category, breed.size_category),
            f"{breed.weight_kg_min:g}-{breed.weight_kg_max:g} kg",
            energy_labels.get(breed["energy_level"], "Energía media"),
            f"{breed.exercise_needs_daily_min}-{breed.exercise_needs_daily_max} "
            "min de ejercicio al día",
        ]
        traits.extend(breed.temperament[:3])
        if breed.hypoallergenic:
            traits.append("Hipoalergénica")
        return traits

    def score_breed(self, prefs: Mapping[str, Any], breed: Breed) -> BreedScore:
        prefs = self.normalize_prefs(prefs)
        total, category_scores = self.total_score(prefs, breed)
        dealbreakers = self.dealbreakers(prefs, breed)
        final = clamp(total - len(dealbreakers) * DEALBREAKER_PENALTY)
        return BreedScore(
            breed_id=breed.id,
            breed_name=breed.name,
            breed_name_es=breed.name_es,
            total_score=round(total, 1),
            category_scores={k: round(v, 1) for k, v in category_scores.items()},
            dimension_scores={
                k: round(v, 1) for k, v in self.dimension_scores(prefs, breed).items()
            },
            match_percentage=round(final, 1),
            key_traits=self.key_traits(breed),
            considerations=self.considerations(prefs, breed),
            dealbreakers=dealbreakers,
            rating=rating_for(final),
        )

    def score_all_breeds(self, prefs: Mapping[str, Any]) -> List[BreedScore]:
        prefs = self.normalize_prefs(prefs)
        scores = [self.score_breed(prefs, breed) for breed in self.breeds]
        # `breed_id` como criterio secundario: sin él, dos razas empatadas
        # cambiarían de orden según el orden del CSV.
        scores.sort(key=lambda s: (-s.match_percentage, s.breed_id))
        return scores
