import pytest

import calculator as calc
from breeds import load_breeds, load_questions
from calculator import CompatibilityCalculator


@pytest.fixture(scope="module")
def engine():
    breeds = load_breeds()
    questions = load_questions()
    return CompatibilityCalculator(breeds, questions), breeds


MATCH_FNS = [
    calc.match_size,
    calc.match_energy,
    calc.match_exercise,
    calc.match_alone_time,
    calc.match_apartment,
    calc.match_space,
    calc.match_climate,
    calc.match_children,
    calc.match_other_pets,
    calc.match_grooming,
    calc.match_shedding,
    calc.match_drooling,
    calc.match_barking,
    calc.match_hypoallergenic,
    calc.match_health_budget,
    calc.match_first_time,
    calc.match_trainability,
    calc.match_purpose,
]


@pytest.mark.parametrize("fn", MATCH_FNS, ids=lambda f: f.__name__)
def test_match_functions_stay_in_range(fn, engine):
    _, breeds = engine
    prefs = {}
    for b in breeds:
        assert 0 <= fn(prefs, b) <= 100, fn.__name__


def test_total_score_in_range(engine):
    calculator, breeds = engine
    for b in breeds:
        score = calculator.score_breed({}, b)
        assert 0 <= score.total_score <= 100
        assert 0 <= score.match_percentage <= 100


def test_weights_are_renormalized(engine):
    calculator, _ = engine
    assert sum(calculator.category_weights.values()) == pytest.approx(1.0)


def test_dealbreaker_penalizes_score(engine):
    calculator, breeds = engine
    giant = next(b for b in breeds if b.size_category == "giant")
    prefs = {"housing_type": "apartamento_pequeno"}
    score = calculator.score_breed(prefs, giant)
    assert "Demasiado grande para un apartamento pequeño" in score.dealbreakers
    without_penalty, _ = calculator.total_score(calculator.normalize_prefs(prefs), giant)
    expected = without_penalty - len(score.dealbreakers) * calc.DEALBREAKER_PENALTY
    assert score.match_percentage == pytest.approx(expected, abs=0.1)


def test_scoring_is_pure(engine):
    calculator, breeds = engine
    prefs = {"preferred_size": "small"}
    breed = breeds[0]
    first = calculator.score_breed(prefs, breed)
    second = calculator.score_breed(prefs, breed)
    assert first.match_percentage == second.match_percentage
    assert prefs == {"preferred_size": "small"}  # no debe mutar el input


def test_score_all_breeds_is_sorted_desc(engine):
    calculator, _ = engine
    scores = calculator.score_all_breeds({})
    percentages = [s.match_percentage for s in scores]
    assert percentages == sorted(percentages, reverse=True)


def test_severe_allergy_favors_hypoallergenic(engine):
    calculator, breeds = engine
    scores = {s.breed_id: s for s in calculator.score_all_breeds(
        {"household_allergies": "severe"}
    )}
    hypo = [b for b in breeds if b.hypoallergenic]
    non_hypo = [b for b in breeds if not b.hypoallergenic]
    avg_hypo = sum(scores[b.id].match_percentage for b in hypo) / len(hypo)
    avg_non_hypo = sum(scores[b.id].match_percentage for b in non_hypo) / len(non_hypo)
    assert avg_hypo > avg_non_hypo


def test_low_exercise_time_triggers_dealbreaker_for_high_energy_breed(engine):
    calculator, breeds = engine
    husky = next(b for b in breeds if b.id == "siberian_husky")
    score = calculator.score_breed({"daily_exercise_time_minutes": 15}, husky)
    assert score.dealbreakers, "un Husky con 15 min/día debería marcar dealbreaker"
