# Metodologí´´a de Evaluació´´´n

## Visiò´´´n General

El sistema Dog Breed Selector utiliza un algoritmo de **compatibilidad ponderada multi-criterio** para determinar la raza de perro ideal para cada usuario.

## Categorí´´as de Evaluació´´´n

### 1. Perfil del Hogar (15%)
- Tipo y tamaño de vivienda
- Espacios exteriores disponibles
- Composició´´´n del hogar
- Ubicació´´´n geográ´´fica y clima

### 2. Estilo de Vida (20%)
- Nivel de actividad fí´´sica
- Tiempo disponible para ejercicio
- Horarios y disponibilidad
- Frecuencia de viajes

### 3. Experiencia (10%)
- Experiencia previa con perros
- Conocimientos de entrenamiento
- Tolerancia a comportamientos

### 4. Preferencias Fí´´sicas (12%)
- Tamaño preferido
- Tipo de pelaje
- Tolerancia a muda
- Disposició´´´n para grooming

### 5. Salud (15%)
- Alergias
- Presupuesto veterinario
- Tolerancia a problemas de salud

### 6. Personalidad (18%)
- Nivel de energí´´a deseado
- Independencia vs apego
- Tolerancia al ladrido
- Compatibilidad con niños/mascotas

### 7. Cuidados (10%)
- Tiempo para grooming
- Tolerancia a salivació´´´n/olores
- Frecuencia de limpieza

### 8. Objetivos (10%)
- Propó´´´sito principal
- Expectativas de obediencia
- Actividades deseadas

## Fó ´rmula de Compatibilidad

```
Score(Raza) = Σ(Peso_Categorí´´a × Match_Categorí´´a) - Penalizaciones
```

Donde:
- **Peso_Categorí´´a**: Importancia relativa (0.0 - 1.0)
- **Match_Categorí´´a**: Porcentaje de coincidencia (0 - 100)
- **Penalizaciones**: Incompatibilidades crí´´ticas (-15 puntos cada una)

## Dealbreakers (Incompatibilidades Crí´´ticas)

Se aplican penalizaciones automáticas en los siguientes casos:

1. **Alergias + Raza no hipoalergé´´nica**: -15 puntos
2. **Apartamento pequeño + Raza gigante**: -15 puntos
3. **Dueñ´´´o primerizo + Raza difí´´cil**: -15 puntos
4. **Poco ejercicio + Raza muy activa**: -15 puntos

## Normalizació´´´n de Scores

Todos los scores se normalizan a una escala de 0-100:

```
Score_Normalizado = (Score_Raw / Score_Max_Possible) × 100
```

## Interpretació´´´n de Resultados

| Score | Interpretació´´´n | Recomendació´´´n |
|-------|------------|----------------|
| 90-100 | Excelente match | Altamente recomendada |
| 80-89 | Muy buen match | Recomendada |
| 70-79 | Buen match | Aceptable con consideraciones |
| 60-69 | Match moderado | Considerar con cuidado |
| <60 | Match bajo | No recomendada |

## Limitaciones

1. **Base de datos**: El sistema solo puede recomendar razas presentes en la base de datos
2. **Generalizaciones**: Los scores son promedios; individuos pueden variar
3. **Contexto**: Factores locales (disponibilidad, legislació´´´n) no se consideran
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

**Versió´´´n**: 1.0  
**Ú´¸ltima actualizació´´´n**: Agosto 2024
