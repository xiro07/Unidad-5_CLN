# Unidad 5

**Materia:** Componentes de Lógica de Negocios  
**Docente:** Miguel Ángel Gómez Marroquín  
**Equipo:** Equipo 9
**Integrantes:**
- Iván Francisco Padrón Macías (Matrícula: 2150830)
- María Ximena Rodarte Cuevas (Matrícula: 2154111)
- Ángel Haziel Bernal Garza (Matrícula: 2156444)

---

## Resumen General del Proyecto (Pasos 1 al 9)

Este repositorio documenta de manera integral el desarrollo, aseguramiento de la calidad, pruebas automatizadas y validación de reglas de negocio del sistema, abarcando desde el proyecto base de pedidos hasta su aplicación en el PMS (Property Management System) del **Hotel Costa Azul**, diseñado bajo una arquitectura limpia y principios de Dominio (*Domain-Driven Design / DDD*) en Python.

### Fases Ejecutadas en el Proyecto:
1. **Instalación y Verificación Base (Paso 1):** Configuración del entorno virtual aislado (`venv`), instalación de dependencias y ejecución de la suite inicial de pruebas con `pytest`.
2. **Pruebas Unitarias y Matriz (Paso 2):** Incorporación de pruebas para descuentos VIP (15%) y estructuración de la matriz de casos de éxito, error y límites.
3. **TDD Real - Red/Green/Refactor (Paso 3):** Desarrollo guiado por pruebas para la regla de no confirmar un pedido dos veces, validando la fase `RED` antes de escribir la lógica en el dominio.
4. **Persistencia y Transacciones (Paso 4):** Validación del comportamiento de repositorios mediante SQLite en memoria, comprobando el efecto de `commit` y `rollback`.
5. **Servicios Externos con Mocks (Paso 5):** Aislamiento de pasarelas de pago y servicios de cobro mediante `unittest.mock.Mock` para evitar transacciones reales y validar escenarios de aprobación y rechazo.
6. **Seguridad y Autorización (Paso 6):** Pruebas rigurosas sobre las políticas de cancelación y control de roles (propietario, administradores, tiempos límite de 24 horas con fechas fijas UTC).
7. **Calidad y Cobertura (Paso 7):** Auditoría estática de estilo con `ruff` (y corrección automática con `--fix`) y medición de cobertura de código mediante `pytest-cov`, alcanzando un **96% global**.
8. **Automatización CI/CD (Paso 8):** Configuración de un pipeline en GitHub Actions para la ejecución automática de linters, pruebas unitarias y validación de umbrales de cobertura en cada `push`.
9. **Aplicación al PIA - Hotel Costa Azul (Paso 9):** Implementación de reglas corporativas clave del sector hotelero (`RN-04` penalización por cancelación, `RN-07` depósitos grupales y `RN-10` límites de ajuste financiero con autorización gerencial), totalizando 23 casos de prueba específicos y pruebas de mutación.

---

## Matrices y Trazabilidad de Pruebas
Para garantizar el cumplimiento de los requerimientos, el repositorio incluye:
- **Matriz de Casos de Prueba (Archivo `matriz_casos_pia.csv`):** Relaciona cada regla de negocio y escenario de éxito, error y límite con sus respectivas pruebas automatizadas.
- **Pruebas de Mutación:** Verificación de la solidez de la suite mediante la alteración intencional de operadores lógicos (por ejemplo, cambiando umbrales de tiempo o montos), asegurando que las pruebas detecten fallos (`1 FAILED`).

---

## Stack Tecnológico y Librerías
- **Lenguaje:** Python 3.15
- **Framework de Pruebas:** `pytest`
- **Cobertura de Código:** `pytest-cov`
- **Análisis Estático y Estilo:** `ruff`
- **Control de Versiones y Automatización:** Git & GitHub Actions (CI/CD)

---

## Uso Responsable de la IA (Vibe Coding)
Se utilizó un asistente de inteligencia artificial como apoyo analítico para proponer casos de prueba bajo un prompt estricto: *"Analiza esta clase de dominio y estas reglas aprobadas. Propón casos de prueba pytest para éxito, error y límites. No inventes reglas nuevas..."*. 
* Toda sugerencia fue rigurosamente ejecutada, filtrada y comparada localmente.
* Propuestas que contravenían el dominio (como relajar los límites temporales de la regla de cancelación RN-04) fueron **rechazadas y corregidas** manualmente mediante pruebas strictly.

---

## Reflexión Final

> El defecto de negocio más costoso en producción para nuestro sistema sería confirmar una reserva o estancia sin que la garantía de pago o el depósito requerido hayan sido validados correctamente. El riesgo en este tipo de arquitecturas es real: si un flujo confirma el registro antes de consultar la pasarela o de verificar las reglas del dominio, un rechazo dejaría una reserva activa o un folio abierto sin cobro, lo que en un entorno hotelero real se traduce en habitaciones ocupadas sin respaldo financiero, pérdidas económicas directas y dolores de cabeza en las conciliaciones de recepción. Otro fallo grave sería permitir operaciones no autorizadas, como aplicar ajustes sin el límite gerencial establecido o cancelar fuera de tiempo sin penalización, generando reclamos y afectando la confianza del huésped.
> 
> La prueba clave para evitar esto es la simulación de rechazos o fallos mediante mocks y pruebas de mutación: comprobar que, si la validación o el cobro fallan, se lanza la excepción correcta de dominio (`DominioException`) y se impide que la reserva quede en un estado de éxito (`CONFIRMED`), lo que nos obliga a proteger el orden del flujo de negocio.
> 
> Al final, que un programa corra sin errores de sintaxis no demuestra que sus reglas sean correctas: hacen falta pruebas automatizadas estrictas que fallen cuando la lógica del negocio se rompe —como lo comprobamos con nuestras pruebas unitarias y de mutación— y un pipeline que las ejecute de forma automática en cada cambio.

---

## Estructura del Repositorio

```text
├── .github/
│   └── workflows/                     # Pipeline de Integración Continua (ci.yml)
├── Paso 9/                            # Subproyecto específico de la entrega final (PIA)
│   ├── diagrams/                      # Diagramas de arquitectura, dominio y secuencia
│   ├── docs/                          # Documentación detallada, ADRs e informes
│   ├── evidencias/                    # Trazas de salida de pruebas y coberturas
│   ├── src/                           # Código fuente del sistema Hotel Costa Azul
│   └── tests/                         # Pruebas unitarias y de integración del PIA
├── documentos/                        # Entregables y reportes finales (Unidad 5_Laboratorio_Eq9)
├── src/                               # Módulos base (application.py, domain.py, repository.py, security.py)
├── pruebas/                           # Suite de pruebas base (test_order.py, test_repository.py, etc.)
├── .gitignore                         # Exclusiones de Git (.venv, __pycache__, htmlcov)
├── LÉAME.md                           # Documentación principal del repositorio
├── pyproject.toml                     # Configuración global de herramientas (pytest, ruff)
└── requisitos.txt                     # Dependencias del proyecto
