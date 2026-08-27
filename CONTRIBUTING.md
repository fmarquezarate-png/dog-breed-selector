# Guía de Contribuciones

!Gracias por tu interés en contribuir al Dog Breed Selector! 🐕

## Cómo Contribuir

### 1. Reportar Bugs

Si encuentras un bug, por favor crea un issue con:
- Descripción clara del problema
- Pasos para reproducir
- Comportamiento esperado vs. comportamiento actual
- Información del sistema (Python version, OS, etc.)

### 2. Sugerir Caracteristicas

Las sugerencias de características son bienvenidas. Por favor incluye:
- Descripción de la característica
- Casos de uso
- Ejemplos de cómo funcionaria

### 3. Enviar Pull Requests

#### Pasos:
1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-caracteristica`)
3. Haz tus cambios
4. Asegurate de que los tests pasan (`pytest tests/`)
5. Commit tus cambios (`git commit -m 'Add: nueva caracteristica'`)
6. Push a la rama (`git push origin feature/nueva-caracteristica`)
7. Abre un Pull Request

#### Convenciones de Commits:
- `Add:` para nuevas características
- `Fix:` para correcciones de bugs
- `Update:` para actualizaciones
- `Refactor:` para refactorizacion de codigo
- `Docs:` para documentacion
- `Test:` para tests

### 4. Estilo de Codigo

#### Python:
- Usar Python 3.9+
- Seguir PEP 8
- Usar type hints
- Docstrings en funciones y clases
- Nombres de variables descriptivos en español

```python
def calcular_compatibilidad(usuario: Dict, raza: Dict) -> float:
    """
    Calcula el score de compatibilidad entre usuario y raza.
    
    Args:
        usuario: Diccionario con preferencias del usuario
        raza: Diccionario con caracteristicas de la raza
    
    Returns:
        Score de compatibilidad (0-100)
    """
    pass
```

#### JavaScript/HTML:
- Usar ES6+
- Indentacion con 2 espacios
- Nombres de variables en camelCase

### 5. Tests

Todos los PRs deben incluir tests:
- Tests unitarios para nuevas funciones
- Tests de integracion para nuevas caracteristicas
- Coverage minimo del 80%

```bash
# Ejecutar tests
pytest tests/ -v

# Con coverage
pytest tests/ --cov=src --cov-report=html
```

## Areas de Contribucion

### Prioritarias:
- [ ] Anadir mas razas a la base de datos
- [ ] Mejorar algoritmo de recomendacion
- [ ] Anadir mas preguntas al cuestionario
- [ ] Mejorar interfaz web
- [ ] Traducciones a otros idiomas
- [ ] Documentacion

### Secundarias:
- [ ] Optimizacion de rendimiento
- [ ] Refactorizacion de codigo
- [ ] Mejoras de UX/UI
- [ ] Tests adicionales

## Codigo de Conducta

- Ser respetuoso con otros contribuidores
- Comentarios constructivos
- Incluir a todos, sin importar experiencia
- Enfocarse en lo mejor para el proyecto

## Preguntas?

Si tienes preguntas, abre un issue o contacta al maintainer:
- GitHub: @fmarquezarate-png
- Email: [tu-email@ejemplo.com]

!Gracias por contribuir! 🎉
