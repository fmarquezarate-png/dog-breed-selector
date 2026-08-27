import pytest

from breeds import BreedDataError, SIZE_ORDER, load_breeds, load_questions


@pytest.fixture(scope="module")
def breeds():
    return load_breeds()


def test_loads_all_breeds(breeds):
    assert len(breeds) == 29


def test_unique_ids(breeds):
    ids = [b.id for b in breeds]
    assert len(ids) == len(set(ids))


def test_size_category_is_valid(breeds):
    for b in breeds:
        assert b.size_category in SIZE_ORDER


def test_size_category_matches_weight(breeds):
    mismatched = [b.id for b in breeds if b.size_category != b.expected_size_category]
    assert mismatched == [], f"size_category desalineado con el peso: {mismatched}"


@pytest.mark.parametrize(
    "low,high",
    [
        ("weight_kg_min", "weight_kg_max"),
        ("height_cm_min", "height_cm_max"),
        ("life_expectancy_min", "life_expectancy_max"),
        ("exercise_needs_daily_min", "exercise_needs_daily_max"),
    ],
)
def test_ranges_are_ordered(breeds, low, high):
    for b in breeds:
        assert b[low] <= b[high], f"{b.id}.{low} > {b.id}.{high}"


def test_scale_fields_in_range(breeds):
    for b in breeds:
        for field, value in b.scales.items():
            assert 1 <= value <= 5, f"{b.id}.{field} = {value}"


def test_hypoallergenic_implies_low_shedding(breeds):
    for b in breeds:
        if b.hypoallergenic:
            assert b["shedding"] <= 2, f"{b.id} es hipoalergénica pero shedding={b['shedding']}"


def test_no_double_coat_is_hypoallergenic(breeds):
    """V-16 (docs/auditoria-datos.md): ninguna raza de doble capa es hipoalergénica."""
    for b in breeds:
        if b.coat_type == "double":
            assert not b.hypoallergenic, f"{b.id} es de doble capa pero hypoallergenic=True"


def test_double_coat_implies_cold_tolerant(breeds):
    """V-18: doble capa exige tolerancia al frío media-alta y muda apreciable."""
    for b in breeds:
        if b.coat_type == "double":
            assert b["cold_tolerance"] >= 3, f"{b.id}: double coat con cold_tolerance={b['cold_tolerance']}"
            assert b["shedding"] >= 3, f"{b.id}: double coat con shedding={b['shedding']}"


def test_each_size_category_has_breeds(breeds):
    """V-28: ninguna categoría de tamaño debe quedarse sin representación mínima."""
    from collections import Counter

    counts = Counter(b.size_category for b in breeds)
    for size in SIZE_ORDER:
        assert counts[size] >= 2, f"{size} solo tiene {counts[size]} raza(s)"


def test_load_questions_weights_positive():
    questions = load_questions()
    for cat_id, cat in questions["categories"].items():
        assert cat["weight"] > 0, cat_id


def test_load_breeds_rejects_bad_scale(tmp_path):
    bad_csv = tmp_path / "breeds.csv"
    header = "id,name,name_es,size_category,weight_kg_min,weight_kg_max,height_cm_min,height_cm_max,life_expectancy_min,life_expectancy_max,energy_level,exercise_needs_daily_min,exercise_needs_daily_max,trainability,intelligence,good_with_children,good_with_dogs,good_with_cats,shedding,grooming_needs,barking_level,drooling,coat_type,coat_length,hypoallergenic,apartment_friendly,good_for_first_time,cold_tolerance,heat_tolerance,prey_drive,wanderlust,protectiveness,health_issues,origin_country,breed_group,temperament,special_needs,common_health_problems,description_es\n"
    row = "x,X,X,mini,1,2,10,20,10,12,9,10,20,3,3,3,3,3,3,3,3,3,short,short,False,3,3,3,3,3,3,3,3,Pais,Toy,[a],n,[a],d\n"
    bad_csv.write_text(header + row, encoding="utf-8")
    with pytest.raises(BreedDataError):
        load_breeds(bad_csv)
