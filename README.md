# 🐕 Dog Breed Selector - Sistema Inteligente de Recomendacion de Razas de Perros

## 📋 Descripcion del Proyecto

Dog Breed Selector es un sistema completo e inteligente diseñado para ayudar a personas, parejas y familias a encontrar la raza de perro perfecta segun sus circunstancias personales, espacio disponible, estilo de vida, preferencias y necesidades especificas.

El sistema utiliza un **algoritmo avanzado de compatibilidad multi-criterio** que evalua mas de 100 variables organizadas en 8 categorias principales, proporcionando recomendaciones personalizadas, fundamentadas y basadas en datos cientificos sobre comportamiento canino y caracteristicas de razas.

### ✨ Caracteristicas Principales

- **Cuestionario exhaustivo**: 50+ preguntas detalladas que cubren todos los aspectos relevantes
- **Base de datos completa**: 29 razas con 40+ caracteristicas cada una (expandible a 300+)
- **Algoritmo inteligente**: Scoring de compatibilidad 0-100% con pesos configurables
- **Filtros avanzados**: Dealbreakers automaticos para incompatibilidades criticas
- **Multi-plataforma**: API REST, interfaz web, scripts de Python
- **Documentacion completa**: Guias, ejemplos, tests unitarios
- **Codigo abierto**: Licencia MIT, contribuciones bienvenidas

### 🎯 Casos de Uso

1. **Familias con ninos**: Encontrar razas compatibles con ninos de diferentes edades
2. **Personas en apartamentos**: Identificar razas adecuadas para espacios reducidos
3. **Dueñ´´´os primerizos**: Recomendar razas faciles de cuidar y entrenar
4. **Personas con alergias**: Filtrar razas hipoalergenicas adecuadas
5. **Deportistas y activos**: Encontrar companeros para actividades fisicas intensas
6. **Adultos mayores**: Seleccionar razas tranquilas y de bajo mantenimiento
7. **Hogares con otras mascotas**: Identificar razas sociables con gatos/otros perros

## 📊 Metodologia de Evaluacion

El sistema evalua 8 categorias principales con diferentes pesos:

### 1. Perfil del Hogar (15%)
- Tipo de vivienda (casa, apartamento, piso)
- Metros cuadrados disponibles
- Acceso a espacios exteriores (jardin, terraza, patio)
- Ubicacion geografica y clima
- Composicion del hogar (numero de personas, edades)
- Presencia de ninos o adultos mayores

### 2. Estilo de Vida (20%)
- Nivel de actividad fisica del usuario
- Tiempo disponible para ejercicio diario
- Horarios laborales (presencial, remoto, viajes)
- Frecuencia de salidas y vacaciones
- Preferencias de actividades (senderismo, playa, ciudad)
- Horas que el perro permanecera solo

### 3. Experiencia y Conocimiento (10%)
- Experiencia previa con perros
- Conocimientos sobre entrenamiento canino
- Disponibilidad para entrenamiento profesional
- Tolerancia a comportamientos especificos (ladridos, destructividad)

### 4. Preferencias Fisicas (12%)
- Tamaño preferido (mini, pequeño, mediano, grande, gigante)
- Tipo de pelaje (corto, largo, rizado, sin pelo)
- Color preferido
- Tolerancia a la muda de pelo
- Disposicion para grooming/cepillado

### 5. Consideraciones de Salud (15%)
- Alergias de los miembros del hogar (caspa, saliva, orina)
- Presupuesto mensual para veterinario
- Tolerancia a razas con problemas de salud conocidos
- Expectativa de vida deseada
- Consideracion de seguro medico para mascotas

### 6. Personalidad y Comportamiento (18%)
- Nivel de energia deseado (bajo, medio, alto, muy alto)
- Independencia vs apego (perro autonomo vs companero constante)
- Tolerancia al ladrido
- Compatibilidad con otras mascotas (perros, gatos, animales pequeños)
- Instinto de presa
- Nivel de protectividad deseado
- Amabilidad con extrañ´´´os

### 7. Cuidados y Mantenimiento (10%)
- Tiempo semanal para grooming/cepillado
- Presupuesto para cuidados profesionales
- Tolerancia a olores y salivacion
- Frecuencia de banos
- Tolerancia a pelo en casa

### 8. Objetivos y Expectativas (10%)
- Proposito principal (compania, deporte, guardia, terapia, exposicion)
- Expectativas de obediencia
- Deseo de participacion en actividades especificas (agility, canicross, etc.)
- Presupuesto inicial para adquisicion

## 🚀 Instalacion y Uso

### Requisitos Previos

- Python 3.9 o superior
- pip (gestor de paquetes de Python)
- Navegador web moderno (para interfaz web)

### Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/fmarquezarate-png/dog-breed-selector.git
cd dog-breed-selector
```

### Paso 2: Instalar Dependencias

```bash
pip install -r requirements.txt
```

### Paso 3: Elegir Metodo de Uso

#### Opcion A: Interfaz Web (Recomendado para usuarios finales)

```bash
# Abrir directamente en el navegador
# Windows: start web/index.html
# Mac: open web/index.html
# Linux: xdg-open web/index.html

# O servir con Python
python -m http.server 8000
# Abrir http://localhost:8000/web/index.html
```

#### Opcion B: API REST (Recomendado para desarrolladores)

```bash
# Iniciar servidor API
cd api
python main.py

# O con uvicorn directamente
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Abrir documentacion Swagger
# http://localhost:8000/docs
```

#### Opcion C: Script de Python (Recomendado para testing/integracion)

```bash
# Ejecutar ejemplo basico
python examples/example_usage.py

# O usar en tu propio codigo
from src.calculator import CompatibilityCalculator, load_data

breeds, questions = load_data()
calculator = CompatibilityCalculator(breeds, questions)

user_prefs = {
    "housing_type": "apartamento_mediano",
    "housing_size_sqm": 75,
    # ... mas preferencias
}

scores = calculator.score_all_breeds(user_prefs)
print(f"Top raza: {scores[0].breed_name_es} ({scores[0].match_percentage}%)")
```

## 📊 Ejemplos de Uso

### Ejemplo 1: Familia con Ninos en Casa

```python
from src.recommender import DogBreedRecommender

recommender = DogBreedRecommender()

# Perfil: Familia con ninos, casa con jardin, activos
answers = {
    "housing_type": "casa_mediana",
    "housing_size_sqm": 150,
    "has_garden": "yes_medium",
    "household_size": 4,
    "has_children": "yes_4_8",
    "activity_level": "active",
    "daily_exercise_time_minutes": 90,
    "dog_experience": "intermediate",
    "first_time_owner": False,
    "preferred_size": "medium",
    "shedding_tolerance": "medium",
    "household_allergies": "none",
    "desired_energy": "high",
    "kids_compatibility": "essential"
}

results = recommender.get_recommendations(answers, top_n=5)

for rec in results:
    print(f"{rec['rank']}. {rec['breed_name_es']} - {rec['match_percentage']}%")
```

**Resultados esperados:**
1. Labrador Retriever - 92%
2. Golden Retriever - 90%
3. Boxer - 87%
4. Australian Shepherd - 85%
5. Vizsla - 83%

### Ejemplo 2: Persona Mayor en Apartamento

```python
# Perfil: Persona mayor, apartamento, actividad ligera
answers = {
    "housing_type": "apartamento_grande",
    "housing_size_sqm": 100,
    "has_garden": "no",
    "household_size": 1,
    "has_children": "no",
    "activity_level": "light",
    "daily_exercise_time_minutes": 30,
    "dog_experience": "advanced",
    "first_time_owner": False,
    "preferred_size": "small",
    "shedding_tolerance": "low",
    "household_allergies": "mild",
    "desired_energy": "low",
    "barking_tolerance": "none"
}

results = recommender.get_recommendations(answers, top_n=5)
```

**Resultados esperados:**
1. Cavalier King Charles Spaniel - 94%
2. Maltes - 92%
3. Shih Tzu - 90%
4. Boston Terrier - 87%
5. French Bulldog - 85%

## 🧪 Testing

### Ejecutar Tests Unitarios

```bash
# Instalar pytest
pip install pytest pytest-cov

# Ejecutar todos los tests
pytest tests/ -v

# Con coverage
pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

# Ver reporte HTML
# Abrir htmlcov/index.html en el navegador
```

## 📈 Roadmap

### Version 1.0 (Actual)
- ✅ Cuestionario basico (17 preguntas)
- ✅ Base de datos de 29 razas
- ✅ Algoritmo de scoring
- ✅ API REST basica
- ✅ Interfaz web funcional
- ✅ Tests unitarios

### Version 1.1 (En desarrollo)
- [ ] Ampliar a 50+ preguntas
- [ ] Expandir base de datos a 100+ razas
- [ ] Sistema de usuarios y guardar resultados
- [ ] Exportar resultados a PDF
- [ ] Comparador de razas lado a lado

### Version 2.0 (Planificado)
- [ ] Machine learning para mejorar recomendaciones
- [ ] Feedback de usuarios para ajustar algoritmo
- [ ] Integracion con redes sociales
- [ ] App movil (React Native/Flutter)
- [ ] Multi-idioma (ingles, frances, aleman)

## 🤝 Contribuciones

Las contribuciones son muy bienvenidas. Por favor:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-caracteristica`)
3. Haz tus cambios y asegurate de que los tests pasan
4. Commit tus cambios (`git commit -m 'Add: nueva caracteristica'`)
5. Push a la rama (`git push origin feature/nueva-caracteristica`)
6. Abre un Pull Request

Para mas detalles, ver [CONTRIBUTING.md](CONTRIBUTING.md)

## 📄 Licencia

Este proyecto esta bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para mas detalles.

## 👤 Autor

**Francisco Marquez Arate**
- GitHub: [@fmarquezarate-png](https://github.com/fmarquezarate-png)
- Ubicacion: Valencia, Espana

## 🙏 Agradecimientos

- **Fuentes de datos**: American Kennel Club (AKC), Federation Cynologique Internationale (FCI), The Kennel Club (UK)
- **Informacion de salud**: Bases de datos veterinarias, estudios cientificos
- **Comunidad**: Amantes de los perros y contribuidores open source

## 📞 Contacto

- **Issues**: [GitHub Issues](https://github.com/fmarquezarate-png/dog-breed-selector/issues)
- **Discusiones**: [GitHub Discussions](https://github.com/fmarquezarate-png/dog-breed-selector/discussions)

## 🌟 Estadisticas del Proyecto

- **Razas en base de datos**: 29 (expandible a 300+)
- **Preguntas en cuestionario**: 17 (planificado: 50+)
- **Categorias de evaluacion**: 8
- **Variables evaluadas**: 100+
- **Endpoints de API**: 6
- **Tests unitarios**: 10+
- **Lineas de codigo**: 2500+

---

**!Encuentra tu companero ideal hoy mismo! 🐕**

*Ultima actualizacion: Agosto 2024*
*Version: 1.0.0*
