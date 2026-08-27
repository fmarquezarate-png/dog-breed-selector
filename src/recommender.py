"""API de alto nivel del recomendador.

Es el único punto de entrada que deberían usar la CLI, la API HTTP y los
ejemplos: carga los datos una sola vez y expone `recommend()`.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence

from breeds import Breed, load_breeds, load_questions
from calculator import BreedScore, CompatibilityCalculator

DEFAULT_TOP_N = 5


@dataclass
class Recommendation:
    """Una raza recomendada, ya posicionada en el ranking."""

    rank: int
    score: BreedScore
    breed: Breed

    def to_dict(self) -> Dict[str, Any]:
        data = self.score.to_dict()
        data["rank"] = self.rank
        data["description_es"] = self.breed.description_es
        data["origin_country"] = self.breed.origin_country
        data["breed_group"] = self.breed.breed_group
        data["life_expectancy"] = [
            self.breed.life_expectancy_min,
            self.breed.life_expectancy_max,
        ]
        return data


class BreedRecommender:
    """Recomendador de razas. Instánciarlo una vez y reutilizarlo."""

    def __init__(
        self,
        breeds: Optional[Sequence[Breed]] = None,
        questions: Optional[Mapping[str, Any]] = None,
    ):
        self.breeds = list(breeds) if breeds is not None else load_breeds()
        self.questions = questions if questions is not None else load_questions()
        self.calculator = CompatibilityCalculator(self.breeds, self.questions)
        self._by_id = {breed.id: breed for breed in self.breeds}

    def get_breed(self, breed_id: str) -> Optional[Breed]:
        return self._by_id.get(breed_id)

    def recommend(
        self,
        answers: Mapping[str, Any],
        top_n: int = DEFAULT_TOP_N,
        exclude_dealbreakers: bool = False,
    ) -> List[Recommendation]:
        """Devuelve las `top_n` razas más compatibles.

        Con `exclude_dealbreakers=True` se descartan por completo las razas
        con alguna incompatibilidad crítica en lugar de solo penalizarlas.
        Si eso dejase la lista vacía, se devuelve el ranking penalizado: es
        preferible una recomendación con avisos que ninguna respuesta.
        """
        scores = self.calculator.score_all_breeds(answers)
        selected = scores
        if exclude_dealbreakers:
            clean = [s for s in scores if not s.dealbreakers]
            selected = clean or scores
        if top_n > 0:
            selected = selected[:top_n]
        return [
            Recommendation(rank=i, score=score, breed=self._by_id[score.breed_id])
            for i, score in enumerate(selected, start=1)
        ]

    def recommend_as_dicts(
        self, answers: Mapping[str, Any], **kwargs: Any
    ) -> List[Dict[str, Any]]:
        return [rec.to_dict() for rec in self.recommend(answers, **kwargs)]


def format_recommendations(recommendations: Sequence[Recommendation]) -> str:
    """Render de texto para la CLI y los ejemplos."""
    if not recommendations:
        return "No hay ninguna raza que encaje con ese perfil."
    lines: List[str] = []
    for rec in recommendations:
        score = rec.score
        lines.append(
            f"{rec.rank}. {score.breed_name_es} — {score.match_percentage}% "
            f"({score.rating})"
        )
        lines.append(f"   {', '.join(score.key_traits[:4])}")
        if score.considerations:
            lines.append(f"   Ten en cuenta: {'; '.join(score.considerations[:3])}")
        for dealbreaker in score.dealbreakers:
            lines.append(f"   ⚠ {dealbreaker}")
        lines.append("")
    return "\n".join(lines).rstrip()


def _load_answers(path: Optional[str]) -> Dict[str, Any]:
    if not path:
        return {}
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Recomienda razas de perro a partir de un perfil."
    )
    parser.add_argument(
        "--answers",
        help="Ruta a un JSON con las respuestas. Sin él se usan los valores "
        "por defecto del cuestionario.",
    )
    parser.add_argument("--top", type=int, default=DEFAULT_TOP_N)
    parser.add_argument(
        "--exclude-dealbreakers",
        action="store_true",
        help="Descarta las razas con incompatibilidades críticas.",
    )
    parser.add_argument(
        "--json", action="store_true", help="Salida en JSON en lugar de texto."
    )
    args = parser.parse_args(argv)

    recommender = BreedRecommender()
    recommendations = recommender.recommend(
        _load_answers(args.answers),
        top_n=args.top,
        exclude_dealbreakers=args.exclude_dealbreakers,
    )
    if args.json:
        print(
            json.dumps(
                [r.to_dict() for r in recommendations], ensure_ascii=False, indent=2
            )
        )
    else:
        print(format_recommendations(recommendations))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
