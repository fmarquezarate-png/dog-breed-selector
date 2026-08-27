# Auditoría de datos — `database/breeds.csv`

**Agente:** Experto en Datos · **Fecha:** 2026-08-27 · **Alcance:** 29 razas × 39 columnas
**Modo:** solo auditoría. No se ha modificado ningún fichero de datos.
**Fuera de alcance (por instrucción):** corrupción de encoding / mojibake en los campos de texto. Se está corrigiendo en paralelo y **no se reporta aquí**.

---

## 0. Resumen ejecutivo

Comprobaciones automáticas ejecutadas sobre el CSV:

| Comprobación | Resultado |
|---|---|
| 29 filas × 39 columnas, sin filas malformadas | ✅ |
| Todas las escalas 1-5 son enteros dentro de `[1,5]` | ✅ **0 violaciones** |
| `min < max` en los 4 pares (`weight`, `height`, `life_expectancy`, `exercise`) | ✅ **0 violaciones** |
| `hypoallergenic` ∈ {True, False} | ✅ |
| `size_category` ∈ {mini, small, medium, large, giant} | ✅ |
| `breed_group` ∈ grupos AKC válidos y correcto por raza | ✅ **29/29 correctos** |

Es decir: **el fichero está limpio a nivel de formato y de dominio; los problemas son todos de contenido factual y de coherencia semántica entre columnas.** Se proponen **52 correcciones concretas**.

Los cuatro hallazgos de mayor impacto sobre las recomendaciones:

1. **`size_category` está mal en 5 razas** — Labrador (25-36 kg), Golden (25-34 kg) y Bóxer (25-32 kg) marcados `medium`; Cocker marcado `small`; Shiba marcado `medium`. Un usuario que filtre "quiero un perro mediano" recibe hoy tres perros de 30 kg.
2. **El dominio de `coat_type` está contaminado con valores de `coat_length`** (`long`, `medium` aparecen como *tipo* de pelo). 8 razas de doble capa están etiquetadas como `long`/`medium`/`short` en vez de `double`, que es lo que gobierna muda, tolerancia al frío y grooming.
3. **Dos esperanzas de vida claramente fuera de rango**: Boyero de Berna 6-8 años (real: 7-10) y Labrador 10-12 (real: 11-13).
4. **`origin_country` contiene entidades que no son países** (`Siberia`), y mezcla granularidades (`Inglaterra`/`Escocia` vs `Reino Unido`) — rompe cualquier agrupación o filtro por país.

### Criterio de corte aplicado a `size_category` (explícito y reproducible)

Se usa el **punto medio del rango de peso adulto**, `m = (weight_kg_min + weight_kg_max) / 2`, no el máximo (el máximo penaliza a razas con gran dimorfismo sexual como el Rottweiler o el Pastor Australiano y las empuja una categoría hacia arriba):

| Categoría | Criterio |
|---|---|
| `mini` | `m < 5 kg` |
| `small` | `5 ≤ m < 12 kg` |
| `medium` | `12 ≤ m < 27 kg` |
| `large` | `27 ≤ m < 50 kg` |
| `giant` | `m ≥ 50 kg` |

Con este corte, 24 de las 29 razas ya están bien clasificadas y las 5 reclasificaciones coinciden con la percepción estándar AKC/FCI. Distribución resultante: mini 4 · small 7 · medium 8 · large 8 · **giant 2** (ver "Razas que faltan").

---

## 1. Tabla de correcciones propuestas

Cada fila es directamente aplicable al CSV. `(opcional)` marca las de menor confianza — mejoran la coherencia pero no son errores flagrantes.

| breed_id | columna | valor actual | valor propuesto | por qué |
|---|---|---|---|---|
| chihuahua | barking_level | 4 | 5 | Raza con el ladrido más reportado del catálogo (alerta constante); hoy empata con Beagle y Pomerania, que son los otros extremos. Debe ser el techo de la escala. |
| pomeranian | height_cm_min | 18 | 15 | Estándar AKC/FCI: 15-18 cm a la cruz. 18 cm como *mínimo* es el máximo real de la raza. |
| pomeranian | height_cm_max | 28 | 20 | 28 cm es altura de Shih Tzu / Bulldog Francés, no de Pomerania. Con 1,5-3,5 kg, 28 cm es anatómicamente imposible. |
| pomeranian | coat_type | long | double | Spitz alemán enano: doble capa con lanilla densa. Es lo que explica `shedding=4` y `cold_tolerance=4`, que hoy quedan sin justificar por el `coat_type`. |
| pomeranian | coat_length | medium | long | El manto exterior es largo y profuso; contradice a `coat_type=long` que ya tenía. |
| pomeranian | barking_level | 4 | 5 | Ladrido agudo y muy frecuente, uno de los motivos de queja vecinal más citados. Incoherente con `apartment_friendly=5`. |
| maltes | barking_level | 3 | 4 | El Maltés es notoriamente vocal / territorial con el timbre; 3 lo iguala con Poodle y Cocker, claramente más silenciosos. *(opcional)* |
| french_bulldog | weight_kg_max | 14 | 13 | Estándar AKC: por debajo de 28 lb = 12,7 kg. 14 kg es sobrepeso, no rango adulto sano. |
| pug | — | — | — | Sin correcciones. Fila internamente coherente (braquicéfalo: `heat_tolerance=1`, `health_issues=5`, `shedding=4`). |
| beagle | barking_level | 4 | 5 | El aullido/baying del Beagle es la característica definitoria de la raza y el nº1 de devoluciones en piso. Debe ser 5. |
| beagle | wanderlust | 4 | 5 | Sabueso de rastro con `prey_drive=5`: se pierde siguiendo un olor, es el arquetipo de perro que no puede ir suelto. |
| cocker_spaniel | size_category | small | medium | 12-15 kg → punto medio 13,5 kg, por encima del corte de 12 kg. El Cocker Inglés se clasifica como raza mediana en AKC/FCI; hoy compite en los filtros con el Pug (7 kg). |
| boston_terrier | heat_tolerance | 2 | 1 | Braquicéfalo. El resto de braquicéfalos del fichero (Pug, Bulldog Francés, Bulldog Inglés) están en 1. Inconsistencia pura. |
| boston_terrier | health_issues | 3 | 4 | Braquicefalia + luxación rotuliana + problemas oculares (ya listados en `common_health_problems`). Los otros braquicéfalos están en 5; 3 lo pinta como raza sana. |
| border_collie | weight_kg_max | 20 | 25 | Estándar AKC: 30-55 lb (14-25 kg). El techo de 20 kg deja fuera a la mayoría de machos. |
| border_collie | coat_type | medium | double | Doble capa (variedad rough y smooth). `medium` es un valor de *longitud*, no de tipo (ver §2, incoherencia D). |
| labrador_retriever | size_category | medium | large | 25-36 kg → punto medio 30,5 kg. Error de referencia citado en el encargo. |
| labrador_retriever | life_expectancy_min | 10 | 11 | AKC: 11-13 años. 10-12 subestima a la raza casi un año. |
| labrador_retriever | life_expectancy_max | 12 | 13 | Ídem. |
| labrador_retriever | coat_type | short | double | Doble capa impermeable con subpelo denso: es lo que justifica `shedding=4` y `cold_tolerance=5`, hoy inexplicables desde `coat_type=short`. |
| labrador_retriever | barking_level | 2 | 3 | 2 lo sitúa como una de las razas más silenciosas del fichero, por debajo del Bóxer y el Gran Danés; el Labrador es vocal en el juego y con visitas. *(opcional)* |
| golden_retriever | size_category | medium | large | 25-34 kg → punto medio 29,5 kg. Error de referencia citado en el encargo. |
| golden_retriever | protectiveness | 4 | 2 | El Golden es el ejemplo canónico de perro que **no** sirve de guardián (recibe al intruso moviendo la cola). Contradice su propio `temperament` (amigable, devoto) y `good_with_dogs=5`. Con 4 hoy empata con el Bulldog Inglés y supera al Bóxer. |
| golden_retriever | coat_type | long | double | Doble capa con flecos. Coherente con `shedding=4`, `cold_tolerance=5`. |
| bulldog | protectiveness | 4 | 3 | Su propio `temperament` es "digno, tranquilo"; con `energy_level=2` y `barking_level=2` no ejerce de guardián. 4 lo empata con el Bóxer y el Boyero de Berna. *(opcional)* |
| boxer | size_category | medium | large | 25-32 kg → punto medio 28,5 kg, mismo peso que el Golden. |
| australian_shepherd | coat_type | medium | double | Doble capa de pastor. Coherente con `shedding=4` y `cold_tolerance=4`. |
| siberian_husky | origin_country | Siberia | Rusia | "Siberia" es una región, no un país. Rompe cualquier agrupación por país (ver regla V-19). |
| siberian_husky | coat_type | long | double | El doble manto ártico es *la* característica de la raza; es lo que sostiene `shedding=5` y `cold_tolerance=5`. |
| siberian_husky | prey_drive | 4 | 5 | Impulso de presa extremo (histórico de incidentes con gatos y animales pequeños); coherente con `good_with_cats=2` y `wanderlust=5`, que ya están en el extremo. |
| spanish_water_dog | energy_level | 4 | 5 | Perro de trabajo (pastoreo + agua) con `exercise=60-90`; su perfil de necesidades está más cerca del Border/Aussie que del Cocker. *(opcional)* |
| german_shepherd | shedding | 4 | 5 | Doble capa que muda todo el año más dos mudas estacionales masivas ("German shedder"). Debe empatar con el Husky en 5. |
| german_shepherd | coat_type | medium | double | Ídem, valor de longitud usado como tipo. |
| german_shepherd | good_for_first_time | 3 | 2 | `energy_level=5`, `protectiveness=5`, `exercise=90-120`, `apartment_friendly=2`: es una raza que exige experiencia. Con 3 hoy empata con el Chihuahua y el Bulldog Inglés. |
| rottweiler | coat_type | short | double | Pelo corto **con** subpelo; es lo que justifica `cold_tolerance=4`, imposible con capa simple corta. |
| rottweiler | life_expectancy_min | 8 | 9 | AKC/estudios de longevidad: 9-10 años. |
| great_dane | weight_kg_min | 45 | 50 | AKC: hembras 50-63 kg, machos 63-79 kg. 45 kg no es un adulto de la raza. |
| great_dane | weight_kg_max | 90 | 82 | 90 kg es peso de Mastín, no de Gran Danés; infla artificialmente el punto medio. |
| great_dane | drooling | 3 | 5 | Belfos colgantes: babea al nivel del Mastín (que está en 5). Con 3 empata con el Bóxer, que babea mucho menos. |
| bernese_mountain | life_expectancy_min | 6 | 7 | 6-8 años es demasiado pesimista incluso para una raza de vida corta; la referencia AKC/FCI es 7-10. |
| bernese_mountain | life_expectancy_max | 8 | 10 | Ídem. Con 8 años de techo, el Boyero queda por debajo del Mastín (10) y del Gran Danés (10), lo cual es falso. |
| bernese_mountain | trainability | 3 | 4 | Boyero de trabajo, muy dispuesto a colaborar; 3 lo iguala al Shih Tzu y al Bulldog. |
| bernese_mountain | coat_type | long | double | Doble capa larga suiza; sostiene `cold_tolerance=5` y `heat_tolerance=1`. |
| mastiff | height_cm_max | 91 | 86 | 91 cm supera al Gran Danés (86), que es más alto que el Mastín. El Mastín es más *masivo*, no más alto. |
| mastiff | apartment_friendly | 3 | 2 | 54-100 kg (punto medio 77 kg): el perro más pesado del catálogo empatado en aptitud para piso con el Gran Danés y el Dóberman. |
| poodle_standard | energy_level | 4 | 5 | El Caniche Standard es un perro de cobro de agua con `trainability=5`/`intelligence=5` y `exercise=60-90`; su percepción de "perro de peluquería" no refleja sus necesidades. *(opcional)* |
| cavalier_king_charles | barking_level | 2 | 3 | Spaniel de compañía, alerta con el timbre. 2 lo pone entre los más silenciosos del fichero. *(opcional)* |
| shiba_inu | size_category | medium | small | 8-11 kg → punto medio 9,5 kg, por debajo del corte de 12 kg. Hoy aparece en el mismo grupo que el Bóxer y el Husky. |
| shiba_inu | shedding | 4 | 5 | Spitz japonés: "blowing coat" dos veces al año, es una de las razas que más pelo suelta del catálogo. |
| shiba_inu | coat_length | short | medium | Doble capa de longitud media; `coat_type=double` con `coat_length=short` y `grooming_needs=3` no describe la realidad. |
| shiba_inu | prey_drive | 4 | 5 | Raza de caza primitiva; el impulso de presa es la razón por la que no se recomienda suelto. Coherente con `good_with_cats=2`, `wanderlust=4`. |
| shiba_inu | life_expectancy_min | 12 | 13 | Es de las razas más longevas del fichero (13-16 años); 12-15 la infravalora. |
| shiba_inu | life_expectancy_max | 15 | 16 | Ídem. |
| vizsla | cold_tolerance | 3 | 2 | Capa **simple** corta sin subpelo ni grasa: es la raza de caza más sensible al frío del catálogo. Con 3 empata con el Rottweiler (que tiene subpelo). |
| weimaraner | cold_tolerance | 3 | 2 | Ídem: capa simple corta. El Dóberman, con exactamente la misma estructura de pelo, está en 2. |
| weimaraner | protectiveness | 3 | 4 | Raza notoriamente territorial y desconfiada con extraños ("velcro dog" con guarda); 3 lo iguala al Caniche. *(opcional)* |
| siberian_husky | good_for_first_time | 2 | 2 | Sin cambio — se confirma correcto (fuga, muda, adiestrabilidad 2). |

**Total: 52 correcciones accionables** (9 de ellas marcadas `(opcional)`).

---

## 2. Incoherencias entre columnas

Casos donde dos o más columnas de la **misma fila** se contradicen. Se ordenan por impacto en las recomendaciones.

**A. `size_category` desalineada del peso (5 casos).**
Labrador (30,5 kg medio) y Golden (29,5 kg) como `medium`; Bóxer (28,5 kg) como `medium`; Cocker (13,5 kg) como `small`; Shiba (9,5 kg) como `medium`. Efecto directo: quien pide un perro mediano para un piso recibe tres retrievers/molosoides de 30 kg, y quien pide un perro pequeño recibe un Cocker. Es el bug de datos con mayor impacto del fichero.

**B. Braquicéfalos con distinta tolerancia al calor.**
Pug, Bulldog Francés y Bulldog Inglés → `heat_tolerance=1`. Boston Terrier → 2. Bóxer → 2. Shih Tzu → 2. No hay criterio detrás: o los cinco/seis comparten techo, o el campo no significa nada. Propuesta mínima en la tabla: Boston → 1. El Bóxer (braquicéfalo moderado, muy propenso al golpe de calor pese a su talla atlética) es candidato razonable a 1 también, pero se deja en 2 por prudencia. Mismo desalineamiento en `health_issues`: Pug/Frenchie/Bulldog = 5, Boston = 3.

**C. `protectiveness` sin relación con el temperamento declarado.**
Golden Retriever `protectiveness=4` con `temperament=[inteligente, amigable, devoto]` y `good_with_dogs=5` — el Golden es el ejemplo de manual de perro que no guarda. Bulldog Inglés `protectiveness=4` con `energy_level=2`/`barking_level=2`. En el otro extremo, Weimaraner en 3, por debajo del Bulldog. La columna no es comparable hoy entre filas.

**D. `coat_type` contiene valores de `coat_length` (8 razas).**
El dominio observado de `coat_type` es `{short, long, medium, curly, double}` — pero `long` y `medium` son longitudes, no texturas. Consecuencia: **ninguna raza de doble capa salvo el Shiba está etiquetada como `double`**, aunque `shedding`, `cold_tolerance` y `grooming_needs` sí reflejan que la tienen. Afectadas: Pomerania, Border Collie, Labrador, Golden, Pastor Australiano, Husky, Pastor Alemán, Rottweiler, Boyero de Berna. Es la incoherencia más sistémica del fichero: cualquier regla derivada del tipo de pelo (alergias, muda, frío) está hoy calculada sobre un campo mal poblado.

**E. `coat_length=long` / `coat_type=curly` con grooming coherente — ✅ sin fallos.**
Verificado: los 5 pelos largos (Yorkie 5, Maltés 5, Shih Tzu 5, Cocker 4, Boyero 3, Golden 3, Cavalier 3) y los 2 rizados (Caniche 5, Perro de Agua 4) tienen `grooming_needs ≥ 3`. No hay ningún `long`+`grooming=1`.

**F. `hypoallergenic=True` vs `shedding` — ✅ sin fallos.**
Los 5 `True` (Yorkshire 1, Maltés 1, Shih Tzu 2, Perro de Agua Español 1, Caniche Standard 1) cumplen `shedding ≤ 2`, y todos tienen pelo tipo pelo/rizado, no manto de muda. Los `False` sospechosos también se verificaron: Pomerania (`shedding=4`, doble capa) correctamente `False`; Bichón Frisé no está en el catálogo (ver §3). **La columna `hypoallergenic` es la más limpia del fichero.** Único apunte: Shih Tzu en el límite (`shedding=2`); es correcto, pero cualquier subida futura a 3 debe invalidar el `True`.

**G. Talla `giant` con `apartment_friendly` alto.**
Mastín Inglés (77 kg medio) tiene `apartment_friendly=3`, igual que el Dóberman (38 kg) y el Gran Danés. El caso del Gran Danés es defendible (perro de baja energía, "sofá gigante", `energy_level=3`), el del Mastín no lo es en la misma medida con 100 kg de techo y `drooling=5`.

**H. `energy_level` vs `exercise_needs_daily_*` — coherente en bloque, con dispersión dentro de cada nivel.**
No hay ninguna contradicción dura (ningún `energy=5` con poco ejercicio ni `energy=1-2` con mucho). Pero dentro de `energy_level=4` conviven bandas muy distintas: Pomerania y Yorkshire 30-45, Cocker y Shiba 45-60, Beagle/Golden/Perro de Agua/Caniche/Rottweiler 60-90. Parte se explica por el tamaño (un Pomerania de 3 kg no necesita los mismos minutos que un Rottweiler), pero conviene documentar esa dependencia en vez de dejarla implícita. Igual con `energy_level=5`: Labrador y Bóxer en 60-90 frente a Border/Aussie/Husky/Dóberman/Vizsla/Weimaraner/Pastor Alemán en 90-120.

**I. `cold_tolerance` sin relación con la estructura del pelo.**
Vizsla y Weimaraner (capa simple corta, sin subpelo) en 3; Dóberman (idéntica estructura) en 2; Rottweiler (corto **con** subpelo) en 4. Los tres primeros deberían ser 2 y el Rottweiler 4 — la propuesta de la tabla los alinea y la corrección de `coat_type` a `double` deja el 4 del Rottweiler justificado.

**J. `prey_drive` alto vs `good_with_cats` — ✅ sin fallos.**
Verificado: las 12 razas con `prey_drive ≥ 4` tienen todas `good_with_cats ≤ 3` (Husky 2, Weimaraner 2, Shiba 2, Beagle 3, Border 3, Vizsla 3…). La relación se mantiene tras aplicar las subidas propuestas a 5 en Husky y Shiba.

**K. Granularidad inconsistente en `origin_country`.**
`Siberia` (región, no país), y `Inglaterra` / `Escocia` frente a `Reino Unido` para razas del mismo Estado (Beagle=Inglaterra, Border Collie=Reino Unido, Golden=Escocia, Cavalier=Reino Unido). Un filtro "razas británicas" hoy devuelve resultados distintos según cómo se escribió cada fila. Notas menores de atribución, no corregidas por ser convención discutible: Maltés → Malta (FCI asigna el patrocinio a Italia); Shih Tzu → China (FCI: Tíbet, patrocinio Reino Unido); Labrador → Canadá (FCI: Reino Unido, aunque el origen es Terranova).

---

## 3. Razas que faltan

Con 29 razas hay tres sesgos estructurales: **el grupo Terrier no tiene ni un solo representante**, solo hay **2 razas `giant`** (Gran Danés y Mastín) y hay **5 hipoalergénicas pero ninguna pequeña que no sea de pelo largo Toy**. Ocho candidatas, por prioridad:

1. **Bichón Frisé** — Hipoalergénico pequeño de pelo rizado. Hoy, quien pide "pequeño + hipoalergénico" solo recibe Yorkshire, Maltés y Shih Tzu, los tres con `grooming_needs=5` y pelo largo; falta la alternativa de manto rizado.
2. **Caniche Miniatura / Toy** — El Caniche solo existe en el catálogo como Standard (`medium`, 20-32 kg). Es la raza hipoalergénica más recomendada del mundo para pisos y ahora mismo está *excluida* de todos los filtros de talla mini/small.
3. **Dachshund / Teckel** — Top-10 mundial en popularidad y perfil morfológico único (condrodistrófico, con implicaciones de salud propias: hernias discales). El grupo Hound está representado por una sola raza, el Beagle.
4. **Schnauzer Miniatura** — Hipoalergénico, tamaño pequeño, muy demandado en Europa continental y España, y cubre el hueco de "perro pequeño con carácter de guarda" que hoy no existe.
5. **Jack Russell Terrier** — **El grupo Terrier de AKC está vacío** (Yorkshire está en Toy y Boston en Non-Sporting). El Jack Russell aporta además el arquetipo "perro pequeño de altísima energía", inexistente: hoy toda raza con `energy_level=5` pesa más de 14 kg, lo que hace imposible recomendar un perro pequeño a alguien activo.
6. **Galgo Español o Whippet** — No hay ningún lebrel/sighthound. Es un perfil contraintuitivo y muy valioso para el recomendador ("atleta en la calle, sofá en casa": `energy_level` alto con `exercise` corto e intenso y `apartment_friendly` alto), que ningún patrón actual del CSV puede producir. Además, en España el galgo domina la adopción.
7. **San Bernardo o Terranova** — Solo hay 2 razas `giant` frente a 8 `large`, y las dos existentes son de pelo corto. Falta el gigante de pelo largo, alta tolerancia al frío y babeo extremo.
8. **Cane Corso** — Molosoide de guarda moderno, en fuerte crecimiento. El segmento "guardián" hoy lo cubren Rottweiler, Dóberman y Pastor Alemán, los tres de perfil muy parecido; el Cane Corso añade una variante de menor energía y mayor necesidad de manejo experto.

*Alternativas de segundo nivel si se amplía más:* Pastor Belga Malinois (trabajo extremo), Akita Inu, Chow Chow, Basset Hound, Setter Irlandés, Bull Terrier.

---

## 4. Reglas de validación recomendadas

Invariantes para un test automático sobre el CSV. Cada una está redactada para ser comprobable sin ambigüedad. Las marcadas ✅ ya se cumplen hoy (son regresiones a prevenir); las marcadas ❌ fallan con los datos actuales y pasarían al aplicar la tabla de §1.

### Estructura e integridad
- **V-01** ✅ Toda fila tiene exactamente 39 campos; el fichero tiene cabecera y ≥1 fila.
- **V-02** ✅ `id` es único, no vacío, y cumple `^[a-z][a-z0-9_]*$` (ASCII, snake_case).
- **V-03** ✅ `name` y `name_es` no vacíos y únicos.
- **V-04** ✅ `size_category ∈ {mini, small, medium, large, giant}`.
- **V-05** ✅ `breed_group ∈ {Sporting, Hound, Working, Terrier, Toy, Non-Sporting, Herding}` (los 7 grupos AKC).
- **V-06** ❌ `coat_type ∈ {short, double, curly, wire, silky, long}` y `coat_length ∈ {short, medium, long}`. **Falla hoy**: `coat_type` toma el valor `medium` (Border Collie, Aussie, Pastor Alemán), que pertenece al dominio de `coat_length`. Regla adicional de disjunción: si `medium` se elimina de `coat_type`, ningún valor puede pertenecer a ambos dominios salvo `short`/`long` documentados como solapamiento intencional.
- **V-07** ✅ `hypoallergenic ∈ {True, False}` (exactamente esas cadenas, sin variantes).
- **V-08** ✅ `temperament` y `common_health_problems` parsean como lista y tienen ≥2 elementos.

### Rangos numéricos
- **V-09** ✅ Toda escala 1-5 (`energy_level`, `trainability`, `intelligence`, `good_with_children`, `good_with_dogs`, `good_with_cats`, `shedding`, `grooming_needs`, `barking_level`, `drooling`, `apartment_friendly`, `good_for_first_time`, `cold_tolerance`, `heat_tolerance`, `prey_drive`, `wanderlust`, `protectiveness`, `health_issues`) es un **entero** con `1 ≤ v ≤ 5`. Sin decimales, sin vacíos, sin `0`.
- **V-10** ✅ `min < max` estricto en los 4 pares: `weight_kg`, `height_cm`, `life_expectancy`, `exercise_needs_daily`.
- **V-11** ✅ Límites físicos: `0.5 ≤ weight_kg_min`, `weight_kg_max ≤ 120`, `12 ≤ height_cm_min`, `height_cm_max ≤ 100`.
- **V-12** ✅ `5 ≤ life_expectancy_min`, `life_expectancy_max ≤ 20`, y `life_expectancy_max - life_expectancy_min ≤ 6` (evita rangos-cajón de sastre tipo "8-18").
- **V-13** ✅ `15 ≤ exercise_needs_daily_min`, `exercise_needs_daily_max ≤ 180`, y `exercise_max - exercise_min ≤ 60`.

### Derivación y coherencia entre columnas
- **V-14** ❌ **`size_category` debe derivarse del peso**, con `m = (weight_kg_min + weight_kg_max)/2`: `m<5 → mini`; `5≤m<12 → small`; `12≤m<27 → medium`; `27≤m<50 → large`; `m≥50 → giant`. **Falla hoy en 5 razas** (Labrador, Golden, Bóxer, Cocker, Shiba). Esta regla debe ser *dura*: la columna es redundante con el peso, así que cualquier divergencia es un bug por definición.
- **V-15** ✅ Coherencia talla↔altura, como cota de sanidad sobre `height_cm_max`: `mini ≤ 30`, `small ≤ 45`, `medium ≤ 65`, `large ≤ 78`, `giant ≥ 68`. Detecta pesos y alturas desincronizados (habría cazado el Pomerania de 28 cm y 2,5 kg si el corte mini fuera 25).
- **V-16** ❌ **`hypoallergenic = True` ⟹ `shedding ≤ 2` Y `grooming_needs ≥ 3` Y `coat_type ∈ {curly, wire, silky, long}`.** Las dos primeras condiciones se cumplen hoy; la tercera falla solo por el dominio contaminado de `coat_type` (V-06). Recíproca obligatoria: **`shedding ≥ 3` ⟹ `hypoallergenic = False`** y **`coat_type = double` ⟹ `hypoallergenic = False`** (no existe raza de doble capa hipoalergénica).
- **V-17** ✅ `coat_length = long` ⟹ `grooming_needs ≥ 3`; `coat_type = curly` ⟹ `grooming_needs ≥ 4`; `coat_type = short` ⟹ `grooming_needs ≤ 3`.
- **V-18** ❌ **`coat_type = double` ⟹ `cold_tolerance ≥ 3` Y `shedding ≥ 3`.** Y la recíproca de detección: `cold_tolerance ≥ 4` ⟹ `coat_type ∈ {double, long, curly}` — hoy la fallan Rottweiler (`short`, `cold=4`) y Labrador (`short`, `cold=5`), que es exactamente el síntoma del `coat_type` mal poblado. Simétricamente, **`coat_type = short` sin subpelo ⟹ `cold_tolerance ≤ 2`** (Vizsla, Weimaraner, Dóberman).
- **V-19** ❌ **`origin_country` debe ser un Estado soberano actual** validado contra una lista ISO-3166 en español. **Falla hoy** con `Siberia`, `Inglaterra` y `Escocia`. Si se decide conservar la granularidad subnacional, debe existir una columna separada `origin_region` y `origin_country` normalizado (`Rusia`, `Reino Unido`).
- **V-20** ❌ **Lista de braquicéfalos ⟹ `heat_tolerance ≤ 2` Y `health_issues ≥ 4`.** Manteniendo un conjunto explícito `BRACHYCEPHALIC = {pug, french_bulldog, bulldog, boston_terrier, shih_tzu, boxer}` en el test. **Falla hoy** en `boston_terrier` (`health_issues=3`). Recíproca útil: `heat_tolerance = 1` ⟹ la raza está en la lista de braquicéfalos **o** `coat_type = double` (razas árticas: Husky, Boyero de Berna).
- **V-21** ✅ **`prey_drive ≥ 4` ⟹ `good_with_cats ≤ 3`**, y `prey_drive = 5` ⟹ `good_with_cats ≤ 3`. Se cumple en las 12 razas afectadas.
- **V-22** ✅ **Monotonía energía↔ejercicio**: `energy_level = 5 ⟹ exercise_needs_daily_min ≥ 60`; `energy_level = 4 ⟹ exercise_min ≥ 30`; `energy_level ≤ 2 ⟹ exercise_max ≤ 60`. Además, como test global: la correlación de rangos (Spearman) entre `energy_level` y el punto medio de ejercicio debe ser `≥ 0.70`.
- **V-23** ❌ **`size_category = giant` ⟹ `apartment_friendly ≤ 3` Y `life_expectancy_max ≤ 11` Y `exercise_needs_daily_max ≤ 90`**; y **`size_category = mini` ⟹ `life_expectancy_max ≥ 12`**. Codifica la relación inversa talla↔longevidad, que es la regla biológica más robusta en cánidos. Hoy se cumple; con Mastín en `apartment_friendly=3` está en el límite exacto (se propone 2).
- **V-24** ❌ **`drooling ≥ 4` ⟹ `size_category ∈ {large, giant}` O la raza es braquicéfala.** Recíproca de detección: `size_category = giant` con belfo colgante ⟹ `drooling ≥ 4` — **falla hoy** en Gran Danés (`drooling=3`).
- **V-25** ✅ **`good_for_first_time ≥ 4` ⟹ `trainability ≥ 3`.** Complemento propuesto (falla hoy en Pastor Alemán, `good_for_first_time=3`): **`protectiveness = 5` Y `energy_level = 5` ⟹ `good_for_first_time ≤ 2`**.
- **V-26** ✅ **`apartment_friendly ≥ 4` ⟹ `size_category ∉ {large, giant}` Y `exercise_needs_daily_max ≤ 90`.**
- **V-27** ✅ `barking_level = 5` no puede coexistir con `apartment_friendly = 5` sin una nota explícita en `special_needs`. Tras las subidas propuestas de Chihuahua y Pomerania a `barking=5` con `apartment=5`, ambas requerirían dicha nota (es un aviso, no un error: son perros de piso *ruidosos*, y el recomendador debe poder decirlo).

### Cobertura del catálogo (tests de conjunto, no de fila)
- **V-28** ❌ Cada `size_category` tiene **≥ 3 razas**. **Falla hoy**: `giant` tiene 2 (Gran Danés, Mastín). Sin esto, cualquier usuario que filtre por talla gigante recibe prácticamente el catálogo entero de esa categoría, sin capacidad de discriminación.
- **V-29** ❌ Cada `breed_group` de AKC tiene **≥ 1 raza**. **Falla hoy**: `Terrier` tiene 0.
- **V-30** ✅ Hay ≥ 3 razas con `hypoallergenic = True` (hoy 5) y ≥ 2 de ellas con `size_category ∈ {mini, small}` (hoy 3).
- **V-31** Ninguna escala 1-5 puede tener **varianza cero** ni concentrar >70% de las filas en un solo valor: detecta columnas rellenadas "a ojo" que no discriminan y por tanto no aportan nada al recomendador.

---

## 5. Cómo aplicar

1. Aplicar primero **V-14** (`size_category` derivada del peso) — es la corrección de mayor impacto y es puramente mecánica.
2. Después, normalizar el dominio de `coat_type` (incoherencia D / **V-06**): sin eso, las reglas **V-16** y **V-18** no pueden activarse.
3. Aplicar el resto de la tabla de §1, dejando las filas `(opcional)` para una segunda pasada con criterio de producto.
4. Codificar **V-01 … V-31** como test automático que corra en cada cambio del CSV. Las reglas ❌ deben quedar en verde tras aplicar §1; las ✅ son protección contra regresiones.
