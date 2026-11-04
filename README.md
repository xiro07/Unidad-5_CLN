# Unidad 5

**Materia:** Componentes de Lógica de Negocios  
**Docente:** Miguel Angel Gomez Marroquin  
**Equipo:** Equipo 9  
**Integrantes:**
- Ivan Francisco Padron Macias 2150830
- María Ximena Rodarte Cuevas 2154111
- Angel Haziel Bernal Garza 2156444

---

## Resumen Ampliado del Proyecto
Este repositorio documenta el desarrollo, aseguramiento de la calidad, pruebas automatizadas y validación de reglas de negocio del sistema **Hotel Costa Azul**, diseñado bajo una arquitectura limpia y principios de Dominio (Domain-Driven Design / DDD) en Python. 

Durante el desarrollo del proyecto se ejecutaron las siguientes fases críticas:
1. **Modelado del Dominio y Reglas de Negocio:** Implementación estricta de validaciones corporativas como la regla de cancelación con penalización (`RN-04`), reglas de depósitos grupales (`RN-07`) y límites de ajuste financiero (`RN-10`).
2. **Estrategia de Pruebas Rigurosa:** Construcción de una suite completa de pruebas unitarias, de integración y de comportamiento para verificar el éxito, errores y casos límite de las entidades y servicios.
3. **Control de Calidad y Cobertura:** Auditoría de código mediante `pytest-cov`, alcanzando una **cobertura global del 96%** en todo el sistema.
4. **Verificación de Defectos (Pruebas de Mutación):** Introducción intencional de mutaciones lógicas en el código base (como cambiar operadores relacionales) para verificar que las pruebas fallen correctamente (`1 FAILED`), validando la solidez de la suite de pruebas.
5. **Integración Continua (CI/CD):** Configuración de un pipeline automatizado en GitHub Actions (`ci.yml`) para asegurar que cada cambio pase por las pruebas antes de integrarse al repositorio.
6. **Uso Responsable de la IA (Vibe Coding):** Análisis crítico y filtrado de propuestas de código y casos de prueba generados por asistentes de IA, validando que cada sugerencia cumpla estrictamente con las reglas de negocio del laboratorio.

---

## Matrices y Trazabilidad Aplicadas
Para garantizar la cobertura total de los requerimientos y reglas del negocio, se integraron herramientas de trazabilidad:
- **Matriz de Casos de Prueba (Archivo `matriz_casos_pia.csv`):** Documento estructurado que relaciona cada regla de negocio y caso de uso del Hotel Costa Azul con su respectiva prueba automatizada en `pytest`, clasificándolas por escenarios de éxito, error y límites operativos.
- **Trazabilidad de Requisitos:** Mapeo bidireccional entre los comandos de la capa de aplicación (`comandos.py`), los objetos de valor (`value_objects.py`), las entidades del dominio (`entidades.py`) y las pruebas unitarias correspondientes.

---

## Stack Tecnológico y Librerías
El proyecto hace uso de un entorno moderno y robusto enfocado en la calidad de software:
- **Lenguaje:** Python 3.15
- **Pruebas Unitarias y de Integración:** `pytest` (Framework principal de pruebas)
- **Cobertura de Código:** `pytest-cov` (plugin para medir el porcentaje de código evaluado por la suite)
- **Análisis Estático y Estilo:** `ruff` (herramienta de linting y formateo rápido para asegurar estándares de código limpio y orden de importaciones)
- **Control de Versiones y Automatización:** Git & GitHub Actions (CI/CD)

---

## Estructura del Repositorio

```text
├── .github/
│   └── workflows/
│       └── ci.yml                     # Pipeline de Integración Continua (GitHub Actions)
├── Paso 9/
│   ├── diagrams/                      # Diagramas de arquitectura, dominio y secuencia
│   ├── docs/                          # Documentación del proyecto, ADRs, bitácoras de IA e informes
│   ├── evidencias/                    # Archivos de texto con trazas de pruebas, cobertura y mutaciones
│   ├── src/                           # Código fuente principal de la aplicación
│   │   ├── aplicacion/                # Casos de uso, comandos, DTOs y servicios de aplicación
│   │   ├── dominio/                   # Entidades, reglas de negocio (RN-04, etc.), value objects y eventos
│   │   └── infraestructura/           # Persistencia, composición y servicios externos
│   ├── tests/                         # Suite completa de pruebas con pytest (dominio, aplicación, seguridad)
│   ├── .gitignore                     # Archivos y carpetas ignorados por Git (entornos, cachés, htmlcov)
│   ├── main.py                        # Punto de entrada principal
│   ├── matriz_casos_pia.csv           # Matriz de trazabilidad y casos de prueba
│   ├── pyproject.toml                 # Configuración de herramientas y pytest
│   └── requirements.txt               # Dependencias del proyecto
└── README.md                          # Documentación y guía general del proyecto
