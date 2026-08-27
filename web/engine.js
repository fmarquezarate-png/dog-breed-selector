/**
 * Motor de compatibilidad para el front estático.
 *
 * Espejo de src/calculator.py: mismas categorías, mismos pesos (leídos de
 * questions.json, no hardcodeados) y las mismas fórmulas de scoring,
 * incluyendo el multiplicador de alineación de tamaño/energía y la mezcla
 * apartamento×ejercicio. Si cambias una fórmula aquí y no en calculator.py
 * (o viceversa), el resultado del sitio y el de la CLI/API divergen sin
 * que salte ningún error — revisa ambos lados.
 */

const NEUTRAL = 70;
const DEALBREAKER_PENALTY = 15;

const clamp = (v, low = 0, high = 100) => Math.max(low, Math.min(high, v));

const SIZE_ORDER = ["mini", "small", "medium", "large", "giant"];
const SPACE_REQUIREMENTS = { mini: 30, small: 50, medium: 80, large: 120, giant: 150 };
const GARDEN_BONUS = { yes_large: 20, yes_medium: 15, yes_small: 10, terrace: 5, no: 0 };
const APARTMENT_TYPES = new Set(["apartamento_pequeno", "apartamento_mediano", "apartamento_grande"]);
const ENERGY_LEVELS = { low: 1, medium: 3, high: 4, very_high: 5 };
const ACTIVITY_LEVELS = { sedentary: 1, light: 2, moderate: 3, active: 4, very_active: 5 };
const TOLERANCE_LEVELS = { none: 1, low: 2, medium: 3, high: 5 };
const GROOMING_LEVELS = { minimal: 1, moderate: 3, high: 4, professional: 5 };
const BUDGET_LEVELS = { low: 1, medium: 3, high: 4, unlimited: 5 };
const EXPERIENCE_LEVELS = { none: 1, basic: 2, intermediate: 3, advanced: 4, expert: 5 };
const OBEDIENCE_LEVELS = { basic: 2, good: 3, excellent: 4, competition: 5 };
const KIDS_IMPORTANCE = { essential: 1.0, important: 0.8, nice_to_have: 0.5, not_important: 0.2 };
// Mismo calibrado que CLIMATE_DEMANDS en calculator.py: heat_tolerance no
// pasa de 4 en el CSV real, así que exigir 5 marcaría a casi todas las razas.
const CLIMATE_DEMANDS = {
  frio: [5, 1],
  continental: [4, 2],
  atlantico: [3, 2],
  mediterraneo: [2, 3],
  calido: [1, 4],
};
const PURPOSE_TRAITS = {
  companion: { good_with_children: 0.3, trainability: 0.3, energy_level: 0.4 },
  family: { good_with_children: 0.6, trainability: 0.4 },
  sport: { energy_level: 0.5, trainability: 0.5 },
  guard: { protectiveness: 0.6, trainability: 0.4 },
  therapy: { good_with_children: 0.4, trainability: 0.6 },
};
const PURPOSE_INVERTED = new Set(["companion:energy_level"]);

function level(map, value, fallback) {
  if (typeof value === "number") return clamp(value, 1, 5);
  return map[value] ?? fallback;
}

function asBool(value, fallback = false) {
  if (typeof value === "boolean") return value;
  if (value === "true") return true;
  if (value === "false") return false;
  return fallback;
}

function asNumber(value, fallback) {
  const n = Number(value);
  return Number.isFinite(n) ? n : fallback;
}

function toleranceMatch(userLevel, breedLevel, step) {
  if (userLevel >= breedLevel) return 100;
  return clamp(100 - (breedLevel - userLevel) * step);
}

function capacityMatch(userLevel, breedLevel) {
  if (userLevel >= breedLevel) return 100;
  return clamp((userLevel / breedLevel) * 100);
}

const matchSize = (p, b) => {
  const preferred = p.preferred_size || "no_preference";
  if (preferred === "no_preference") return NEUTRAL;
  if (preferred === b.size_category) return 100;
  const distance = Math.abs(SIZE_ORDER.indexOf(preferred) - SIZE_ORDER.indexOf(b.size_category));
  return clamp(100 - distance * 30, 10);
};

const matchEnergy = (p, b) => {
  const desired = level(ENERGY_LEVELS, p.desired_energy, 3);
  const activity = level(ACTIVITY_LEVELS, p.activity_level, 3);
  const target = (desired * 2 + activity) / 3;
  const diff = b.energy_level - target;
  const penalty = diff > 0 ? diff * 22 : Math.abs(diff) * 14;
  return clamp(100 - penalty);
};

const matchExercise = (p, b) => {
  const available = asNumber(p.daily_exercise_time_minutes, 60);
  const min = Math.max(1, b.exercise_needs_daily_min);
  const max = Math.max(min, b.exercise_needs_daily_max);
  if (available >= max) return 100;
  if (available >= min) return 90;
  return clamp((available / min) * 100);
};

const matchAloneTime = (p, b) => {
  const hoursByHousing = {
    home_full: 1, home_partial: 4, office_8h: 9, office_10h_plus: 11, frequent_travel: 12,
  };
  const hours = hoursByHousing[p.work_schedule] ?? 9;
  const strain = (b.energy_level + b.barking_level) / 2;
  if (hours <= 4) return 100;
  return clamp(100 - (hours - 4) * (strain * 2.2));
};

/** `apartment_friendly` mezcla tamaño/ruido (fijo) con necesidad de
 * actividad (no lo es); se corrige mezclándolo con `matchExercise` para
 * que un perro muy exigente pero bien paseado no cargue el castigo entero.
 */
const matchApartment = (p, b) => {
  const housing = p.housing_type || "casa_mediana";
  if (APARTMENT_TYPES.has(housing)) {
    const base = clamp((b.apartment_friendly / 5) * 100);
    const exerciseMet = matchExercise(p, b);
    return clamp(base * 0.6 + exerciseMet * 0.4);
  }
  return 100;
};

const matchSpace = (p, b) => {
  const sqm = asNumber(p.housing_size_sqm, 100);
  const bonus = GARDEN_BONUS[p.has_garden || "no"] ?? 0;
  const required = SPACE_REQUIREMENTS[b.size_category] ?? 80;
  const base = sqm >= required ? 80 : (sqm / required) * 80;
  return clamp(base + bonus);
};

const matchClimate = (p, b) => {
  const [coldNeeded, heatNeeded] = CLIMATE_DEMANDS[p.geographic_location] ?? [3, 3];
  const coldGap = Math.max(0, coldNeeded - b.cold_tolerance);
  const heatGap = Math.max(0, heatNeeded - b.heat_tolerance);
  return clamp(100 - (coldGap + heatGap) * 15);
};

const matchChildren = (p, b) => {
  const hasChildren = p.has_children || "no";
  const importanceKey = p.kids_compatibility || "not_important";
  let importance = KIDS_IMPORTANCE[importanceKey] ?? 0.5;
  if (hasChildren !== "no") importance = Math.max(importance, hasChildren === "yes_0_3" ? 0.9 : 0.7);
  if (hasChildren === "no" && importanceKey === "not_important") return NEUTRAL;
  const base = (b.good_with_children / 5) * 100;
  return clamp(base * importance + NEUTRAL * (1 - importance));
};

const matchOtherPets = (p, b) => {
  const pets = p.other_pets || "none";
  if (pets === "none") return NEUTRAL;
  const scores = [];
  if (pets === "dogs" || pets === "both") scores.push((b.good_with_dogs / 5) * 100);
  if (pets === "cats" || pets === "both") {
    const cats = (b.good_with_cats / 5) * 100;
    scores.push(clamp(cats - (b.prey_drive - 3) * 10));
  }
  return scores.length ? clamp(scores.reduce((a, x) => a + x, 0) / scores.length) : NEUTRAL;
};

const matchGrooming = (p, b) => capacityMatch(level(GROOMING_LEVELS, p.grooming_willingness, 3), b.grooming_needs);
const matchShedding = (p, b) => toleranceMatch(level(TOLERANCE_LEVELS, p.shedding_tolerance, 3), b.shedding, 25);
const matchDrooling = (p, b) => toleranceMatch(level(TOLERANCE_LEVELS, p.drooling_tolerance, 3), b.drooling, 25);
const matchBarking = (p, b) => toleranceMatch(level(TOLERANCE_LEVELS, p.barking_tolerance, 3), b.barking_level, 30);

const matchHypoallergenic = (p, b) => {
  const allergies = p.household_allergies || "none";
  if (allergies === "none") return NEUTRAL;
  if (allergies === "mild") return b.hypoallergenic ? 90 : 50;
  if (allergies === "moderate" || allergies === "severe") return b.hypoallergenic ? 100 : 20;
  return NEUTRAL;
};

const matchHealthBudget = (p, b) => capacityMatch(level(BUDGET_LEVELS, p.vet_budget_monthly, 3), b.health_issues);

const matchFirstTime = (p, b) => {
  let experience = level(EXPERIENCE_LEVELS, p.dog_experience, 2);
  if (asBool(p.first_time_owner, experience <= 1)) experience = Math.min(experience, 2);
  if (experience >= 4) return 100;
  return capacityMatch(experience, 6 - b.good_for_first_time);
};

const matchTrainability = (p, b) => {
  const expected = level(OBEDIENCE_LEVELS, p.obedience_expectations, 3);
  return capacityMatch(b.trainability, expected);
};

const matchPurpose = (p, b) => {
  const purpose = p.main_purpose || "companion";
  const traits = PURPOSE_TRAITS[purpose];
  if (!traits) return NEUTRAL;
  let total = 0;
  let weightSum = 0;
  for (const [trait, weight] of Object.entries(traits)) {
    let value = b[trait];
    if (PURPOSE_INVERTED.has(`${purpose}:${trait}`)) value = 6 - value;
    total += (value / 5) * 100 * weight;
    weightSum += weight;
  }
  return clamp(total / weightSum);
};

/** Categoría -> dimensiones que la componen (misma agrupación que calculator.py). */
const CATEGORY_DIMENSIONS = {
  hogar: { space: matchSpace, apartment: matchApartment, climate: matchClimate },
  estilo_vida: { energy: matchEnergy, exercise: matchExercise, alone_time: matchAloneTime },
  experiencia: { first_time: matchFirstTime, trainability: matchTrainability },
  preferencias_fisicas: { size: matchSize, shedding: matchShedding },
  salud: { hypoallergenic: matchHypoallergenic, health_budget: matchHealthBudget },
  personalidad: { children: matchChildren, barking: matchBarking, other_pets: matchOtherPets },
  cuidados: { grooming: matchGrooming, drooling: matchDrooling },
  objetivos: { obedience: matchTrainability, purpose: matchPurpose },
};

const DEALBREAKERS = [
  (p, b) => (["moderate", "severe"].includes(p.household_allergies) && !b.hypoallergenic
    ? "No es hipoalergénica y hay alergias en el hogar" : null),
  (p, b) => (p.housing_type === "apartamento_pequeno" && ["large", "giant"].includes(b.size_category)
    ? "Demasiado grande para un apartamento pequeño" : null),
  (p, b) => {
    const experience = level(EXPERIENCE_LEVELS, p.dog_experience, 2);
    const isFirstTime = asBool(p.first_time_owner, experience <= 1);
    return (isFirstTime || experience <= 1) && b.good_for_first_time <= 2
      ? "No recomendada para dueños primerizos" : null;
  },
  (p, b) => {
    const available = asNumber(p.daily_exercise_time_minutes, 60);
    return available < b.exercise_needs_daily_min * 0.6
      ? `Necesita al menos ${b.exercise_needs_daily_min} min de ejercicio al día` : null;
  },
  (p, b) => (p.has_children === "yes_0_3" && b.good_with_children <= 2
    ? "Poco tolerante con niños muy pequeños" : null),
];

const RATINGS = [
  [90, "Excelente match"],
  [80, "Muy buen match"],
  [70, "Buen match"],
  [60, "Match moderado"],
  [0, "Match bajo"],
];
const ratingFor = (score) => RATINGS.find(([threshold]) => score >= threshold)[1];

const SIZE_LABELS = { mini: "Tamaño mini", small: "Tamaño pequeño", medium: "Tamaño mediano", large: "Tamaño grande", giant: "Tamaño gigante" };
const ENERGY_LABELS = { 1: "Muy tranquilo", 2: "Tranquilo", 3: "Energía media", 4: "Enérgico", 5: "Muy enérgico" };

function keyTraits(b) {
  const traits = [
    SIZE_LABELS[b.size_category] || b.size_category,
    `${b.weight_kg_min}-${b.weight_kg_max} kg`,
    ENERGY_LABELS[b.energy_level] || "Energía media",
    `${b.exercise_needs_daily_min}-${b.exercise_needs_daily_max} min de ejercicio al día`,
    ...(b.temperament || []).slice(0, 3),
  ];
  if (b.hypoallergenic) traits.push("Hipoalergénica");
  return traits;
}

function considerations(p, b) {
  const notes = [];
  if (b.special_needs) notes.push(b.special_needs);
  if (b.grooming_needs >= 4) notes.push("Requiere cepillado frecuente o peluquería profesional");
  if (b.shedding >= 4) notes.push("Suelta bastante pelo");
  if (b.barking_level >= 4) notes.push("Tiende a ladrar");
  if (b.drooling >= 4) notes.push("Babea");
  if (b.wanderlust >= 4) notes.push("Tendencia a escaparse: necesita vallado seguro");
  if (b.prey_drive >= 4 && ["cats", "both"].includes(p.other_pets)) {
    notes.push("Instinto de presa alto: la convivencia con gatos exige trabajo");
  }
  if (b.health_issues >= 4) notes.push("Raza con predisposición a problemas de salud");
  const [coldNeeded, heatNeeded] = CLIMATE_DEMANDS[p.geographic_location] ?? [3, 3];
  if (b.heat_tolerance < heatNeeded) notes.push("Lleva mal el calor de tu zona");
  if (b.cold_tolerance < coldNeeded) notes.push("Lleva mal el frío de tu zona");
  return [...new Set(notes)];
}

/** Crea un calculador ligado a `categoryWeights` (normalizados a 1.0). */
export function createCalculator(categories) {
  const rawWeights = Object.fromEntries(
    Object.entries(categories)
      .filter(([id]) => id in CATEGORY_DIMENSIONS)
      .map(([id, cat]) => [id, cat.weight || 0])
  );
  const total = Object.values(rawWeights).reduce((a, b) => a + b, 0) || 1;
  const weights = Object.fromEntries(Object.entries(rawWeights).map(([k, v]) => [k, v / total]));

  function categoryScore(categoryId, prefs, breed) {
    const dims = CATEGORY_DIMENSIONS[categoryId];
    if (!dims) return NEUTRAL;
    const values = Object.values(dims).map((fn) => fn(prefs, breed));
    return values.reduce((a, b) => a + b, 0) / values.length;
  }

  // Ver alignment_multiplier en calculator.py: un desajuste grave en UNA
  // dimensión (pedir "gigante" y recibir un Cocker) se diluye a un puñado
  // de puntos si solo cuenta como 1/8 de 1 categoría entre 8. El tamaño y
  // la energía deseados son preferencias explícitas y difíciles de
  // compensar en la vida real, así que multiplican el score entero.
  function alignmentMultiplier(prefs, breed) {
    const sizeScore = matchSize(prefs, breed);
    const energyScore = matchEnergy(prefs, breed);
    const sizeFactor = 0.55 + 0.45 * (sizeScore / 100);
    const energyFactor = 0.75 + 0.25 * (energyScore / 100);
    return sizeFactor * energyFactor;
  }

  function dealbreakers(prefs, breed) {
    return DEALBREAKERS.map((fn) => fn(prefs, breed)).filter(Boolean);
  }

  function scoreBreed(prefs, breed) {
    const categoryScores = {};
    let weighted = 0;
    for (const [id, weight] of Object.entries(weights)) {
      const score = categoryScore(id, prefs, breed);
      categoryScores[id] = score;
      weighted += score * weight;
    }
    weighted = clamp(weighted) * alignmentMultiplier(prefs, breed);
    const found = dealbreakers(prefs, breed);
    const matchPercentage = clamp(clamp(weighted) - found.length * DEALBREAKER_PENALTY);
    return {
      breed_id: breed.id,
      breed_name_es: breed.name_es,
      total_score: Math.round(clamp(weighted) * 10) / 10,
      match_percentage: Math.round(matchPercentage * 10) / 10,
      category_scores: categoryScores,
      dealbreakers: found,
      considerations: considerations(prefs, breed),
      key_traits: keyTraits(breed),
      rating: ratingFor(matchPercentage),
    };
  }

  function scoreAllBreeds(prefs, breeds) {
    return breeds
      .map((b) => scoreBreed(prefs, b))
      .sort((a, b) => b.match_percentage - a.match_percentage || a.breed_id.localeCompare(b.breed_id));
  }

  return { scoreBreed, scoreAllBreeds, weights };
}
