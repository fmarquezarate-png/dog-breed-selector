"""Carga y validación de la base de datos de razas.

`database/breeds.csv` es la única fuente de verdad. Todo lo demás
(`web/breeds.json`, la API, los tests) se deriva de aquí.

Un CSV es texto: sin este módulo, `energy_level` llega como `"3"` y
`hypoallergenic` como `"False"` (que en Python es *verdadero*). Ese casting
silencioso es la clase de bug que rompe un motor de scoring sin que salte
ninguna excepción, así que el parseo es explícito y validado.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parent.parent
BREEDS_CSV = ROOT / "database" / "breeds.csv"
QUESTIONS_JSON = ROOT / "questionnaire" / "questions.json"

SIZE_ORDER = ["mini", "small", "medium", "large", "giant"]

#: Corte por peso medio adulto (kg) que define `size_category`.
#: El límite superior es exclusivo; la última categoría no tiene techo.
#: Calibrado en la auditoría de docs/auditoria-datos.md (§0): con este corte,
#: 24 de las 29 razas del catálogo ya estaban bien clasificadas.
SIZE_THRESHOLDS = [
    ("mini", 0.0, 5.0),
    ("small", 5.0, 12.0),
    ("medium", 12.0, 27.0),
    ("large", 27.0, 50.0),
    ("giant", 50.0, float("inf")),
]

FLOAT_FIELDS = ["weight_kg_min", "weight_kg_max"]

INT_FIELDS = [
    "height_cm_min",
    "height_cm_max",
    "life_expectancy_min",
    "life_expectancy_max",
    "exercise_needs_daily_min",
    "exercise_needs_daily_max",
]

#: Columnas en escala Likert 1-5. El validador exige que estén en rango.
SCALE_FIELDS = [
    "energy_level",
    "trainability",
    "intelligence",
    "good_with_children",
    "good_with_dogs",
    "good_with_cats",
    "shedding",
    "grooming_needs",
    "barking_level",
    "drooling",
    "apartment_friendly",
    "good_for_first_time",
    "cold_tolerance",
    "heat_tolerance",
    "prey_drive",
    "wanderlust",
    "protectiveness",
    "health_issues",
]

BOOL_FIELDS = ["hypoallergenic"]

LIST_FIELDS = ["temperament", "common_health_problems"]

#: Pares (min, max) que deben cumplir min <= max.
RANGE_PAIRS = [
    ("weight_kg_min", "weight_kg_max"),
    ("height_cm_min", "height_cm_max"),
    ("life_expectancy_min", "life_expectancy_max"),
    ("exercise_needs_daily_min", "exercise_needs_daily_max"),
]


class BreedDataError(ValueError):
    """El CSV de razas no cumple el contrato de datos."""


@dataclass(frozen=True)
class Breed:
    """Una raza, con los tipos ya resueltos."""

    id: str
    name: str
    name_es: str
    size_category: str
    coat_type: str
    coat_length: str
    origin_country: str
    breed_group: str
    special_needs: str
    description_es: str
    hypoallergenic: bool
    weight_kg_min: float
    weight_kg_max: float
    height_cm_min: int
    height_cm_max: int
    life_expectancy_min: int
    life_expectancy_max: int
    exercise_needs_daily_min: int
    exercise_needs_daily_max: int
    scales: dict[str, int] = field(default_factory=dict)
    temperament: list[str] = field(default_factory=list)
    common_health_problems: list[str] = field(default_factory=list)

    def __getitem__(self, key: str) -> Any:
        """Acceso estilo dict, para que el calculador no tenga que saber
        si un campo es escalar o escala."""
        if key in self.scales:
            return self.scales[key]
        return getattr(self, key)

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self[key]
        except (AttributeError, KeyError):
            return default

    @property
    def weight_kg_avg(self) -> float:
        return (self.weight_kg_min + self.weight_kg_max) / 2

    @property
    def expected_size_category(self) -> str:
        """La categoría que le corresponde por peso, según SIZE_THRESHOLDS."""
        avg = self.weight_kg_avg
        for name, low, high in SIZE_THRESHOLDS:
            if low <= avg < high:
                return name
        return SIZE_ORDER[-1]

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            k: v for k, v in self.__dict__.items() if k != "scales"
        }
        data.update(self.scales)
        return data


def _parse_list(raw: str) -> list[str]:
    """`"[alerta, valiente]"` -> `["alerta", "valiente"]`."""
    raw = (raw or "").strip()
    if raw.startswith("[") and raw.endswith("]"):
        raw = raw[1:-1]
    return [item.strip() for item in raw.split(",") if item.strip()]


def _parse_bool(raw: str, breed_id: str, column: str) -> bool:
    value = (raw or "").strip().lower()
    if value in {"true", "1", "yes", "si", "sí"}:
        return True
    if value in {"false", "0", "no", ""}:
        return False
    raise BreedDataError(f"{breed_id}.{column}: booleano no reconocido {raw!r}")


def _parse_number(raw: str, breed_id: str, column: str, cast):
    try:
        return cast(str(raw).strip())
    except (TypeError, ValueError) as exc:
        raise BreedDataError(
            f"{breed_id}.{column}: se esperaba un número, se recibió {raw!r}"
        ) from exc


def _row_to_breed(row: dict[str, str]) -> Breed:
    breed_id = (row.get("id") or "").strip()
    if not breed_id:
        raise BreedDataError("Hay una fila sin `id` en breeds.csv")

    scales = {}
    for column in SCALE_FIELDS:
        value = _parse_number(row.get(column, ""), breed_id, column, int)
        if not 1 <= value <= 5:
            raise BreedDataError(
                f"{breed_id}.{column}: {value} fuera de la escala 1-5"
            )
        scales[column] = value

    breed = Breed(
        id=breed_id,
        name=(row.get("name") or "").strip(),
        name_es=(row.get("name_es") or "").strip(),
        size_category=(row.get("size_category") or "").strip(),
        coat_type=(row.get("coat_type") or "").strip(),
        coat_length=(row.get("coat_length") or "").strip(),
        origin_country=(row.get("origin_country") or "").strip(),
        breed_group=(row.get("breed_group") or "").strip(),
        special_needs=(row.get("special_needs") or "").strip(),
        description_es=(row.get("description_es") or "").strip(),
        hypoallergenic=_parse_bool(
            row.get("hypoallergenic", ""), breed_id, "hypoallergenic"
        ),
        **{
            column: _parse_number(row.get(column, ""), breed_id, column, float)
            for column in FLOAT_FIELDS
        },
        **{
            column: _parse_number(row.get(column, ""), breed_id, column, int)
            for column in INT_FIELDS
        },
        scales=scales,
        **{column: _parse_list(row.get(column, "")) for column in LIST_FIELDS},
    )

    if breed.size_category not in SIZE_ORDER:
        raise BreedDataError(
            f"{breed_id}.size_category: {breed.size_category!r} no está en {SIZE_ORDER}"
        )
    for low_col, high_col in RANGE_PAIRS:
        if breed[low_col] > breed[high_col]:
            raise BreedDataError(
                f"{breed_id}: {low_col} ({breed[low_col]}) > {high_col} ({breed[high_col]})"
            )
    return breed


def load_breeds(path: Path | str = BREEDS_CSV) -> list[Breed]:
    """Lee el CSV, castea los tipos y valida el contrato de datos.

    Lanza `BreedDataError` ante cualquier fila inválida: preferimos fallar
    al arrancar que recomendar sobre datos corruptos.
    """
    with open(path, encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        raise BreedDataError(f"{path} no contiene ninguna raza")

    breeds = [_row_to_breed(row) for row in rows]

    seen: set[str] = set()
    duplicates = {b.id for b in breeds if b.id in seen or seen.add(b.id)}
    if duplicates:
        raise BreedDataError(f"IDs de raza duplicados: {sorted(duplicates)}")
    return breeds


def load_questions(path: Path | str = QUESTIONS_JSON) -> dict[str, Any]:
    """Lee el cuestionario y comprueba que tenga categorías con peso."""
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    categories = data.get("categories")
    if not categories:
        raise BreedDataError(f"{path} no define ninguna categoría")
    for cat_id, cat in categories.items():
        if not isinstance(cat.get("weight"), (int, float)) or cat["weight"] <= 0:
            raise BreedDataError(f"Categoría {cat_id}: peso ausente o no positivo")
    return data


def default_answers(questions: dict[str, Any] | None = None) -> dict[str, Any]:
    """Respuestas por defecto para cada pregunta del cuestionario.

    Sirve para rellenar los huecos de un perfil parcial, de modo que el
    motor nunca dependa de defaults dispersos por el código.
    """
    questions = questions or load_questions()
    answers: dict[str, Any] = {}
    for category in questions["categories"].values():
        for question in category.get("questions", []):
            if "default" in question:
                answers[question["id"]] = question["default"]
    return answers


def breeds_to_json(breeds: Iterable[Breed]) -> str:
    """Serializa las razas para el front estático."""
    payload = {"breeds": [breed.to_dict() for breed in breeds]}
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
