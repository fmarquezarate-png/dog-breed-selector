# Metodología de Evaluación

## Visión General

El sistema Dog Breed Selector utiliza un algoritmo de **compatibilidad ponderada multi-criterio** para determinar la raza de perro ideal para cada usuario.

## Categorías de Evaluación

### 1. Perfil del Hogar (15%)
- Tipo y tamaño de vivienda
- Espacios exteriores disponibles
- Composición del hogar
- Ubicación geográfica y clima

### 2. Estilo de Vida (20%)
- Nivel de actividad física
- Tiempo disponible para ejercicio
- Horarios y disponibilidad
- Frecuencia de viajes

### 3. Experiencia (10%)
- Experiencia previa con perros
- Conocimientos de entrenamiento
- Tolerancia a comportamientos

### 4. Preferencias Físicas (12%)
- Tamaño preferido
- Tipo de pelaje
- Tolerancia a muda
- Disposición para grooming

### 5. Salud (15%)
- Alergias
- Presupuesto veterinario
- Tolerancia a problemas de salud

### 6. Personalidad (18%)
- Nivel de energía deseado
- Independencia vs apego
- Tolerancia al ladrido
- Compatibilidad con niños/mascotas

### 7. Cuidados (10%)
- Tiempo para grooming
- Tolerancia a salivación/olores
- Frecuencia de limpieza

### 8. Objetivos (10%)
- Propósito principal
- Expectativas de obediencia
- Actividades deseadas

## Fórmula de Compatibilidad

```
Score(Raza) = [Σ(Peso_Categoría × Match_Categoría) × Multiplicador_Alineación] - Penalizaciones
```

Donde:
- **Peso_Categoría**: Importancia relativa (0.0 - 1.0)
- **Match_Categoría**: Porcentaje de coincidencia (0 - 100)
- **Multiplicador_Alineación**: corrección sobre tamaño y energía deseados (ver abajo)
- **Penalizaciones**: Incompatibilidades críticas (-15 puntos cada una)

### Por qué existe el multiplicador de alineación

Promediar 8 categorías diluye una preferencia explícita: un desajuste total
en tamaño (pedir "gigante" y evaluar un Cocker Spaniel) solo pesa 1/16 del
score final si se trata como una dimensión más, así que la raza mal
clasificada seguía ganando por tener buen puntaje mediocre en todo lo
demás. `preferred_size` y `desired_energy` son preferencias explícitas y
difíciles de compensar en la vida real (un piso no se hace más grande), así
que multiplican el score entero en vez de promediarse:

```
factor_tamaño  = 0.55 + 0.45 × (match_size / 100)     # rango: 0.55 - 1.0
factor_energía = 0.75 + 0.25 × (match_energy / 100)   # rango: 0.75 - 1.0
Multiplicador_Alineación = factor_tamaño × factor_energía
```

Con "sin preferencia" (match_size=70, neutro) el recorte es leve (~9%); con
un desajuste total (match_size=10) el score cae más de un 40%, suficiente
para que una raza del tamaño correcto la supere aunque sea débil en otras
categorías. Ver `docs/auditoria-datos.md` y los tests de
`tests/test_calculator.py::test_explicit_size_preference_dominates_the_ranking`
para la regresión que motivó este cambio.

## Dealbreakers (Incompatibilidades Críticas)

Se aplican penalizaciones automáticas en los siguientes casos:

1. **Alergias + Raza no hipoalergénica**: -15 puntos
2. **Apartamento pequeño + Raza gigante**: -15 puntos
3. **Dueño primerizo + Raza difícil**: -15 puntos
4. **Poco ejercicio + Raza muy activa**: -15 puntos

## Normalización de Scores

Todos los scores se normalizan a una escala de 0-100:

```
Score_Normalizado = (Score_Raw / Score_Max_Possible) × 100
```

## Interpretación de Resultados

| Score | Interpretación | Recomendación |
|-------|------------|----------------|
| 90-100 | Excelente match | Altamente recomendada |
| 80-89 | Muy buen match | Recomendada |
| 70-79 | Buen match | Aceptable con consideraciones |
| 60-69 | Match moderado | Considerar con cuidado |
| <60 | Match bajo | No recomendada |

## Limitaciones

1. **Base de datos**: El sistema solo puede recomendar razas presentes en la base de datos
2. **Generalizaciones**: Los scores son promedios; individuos pueden variar
3. **Contexto**: Factores locales (disponibilidad, legislación) no se consideran
4. **Salud**: No sustituye consejo veterinario profesional

## Fuentes de Datos

- American Kennel Club (AKC)
- Fédération Cynologique Internationale (FCI)
- The Kennel Club (UK)
- Bases de datos veterinarias
- Literatura científica sobre comportamiento canino

## Actualizaciones

La base de datos y algoritmos se actualizan periódicamente para incorporar:
- Nuevas investigaciones sobre comportamiento
- Datos de salud actualizados
- Feedback de usuarios
- Nuevas razas

---

**Versión**: 1.0  
**Última actualización**: Agosto 2024
