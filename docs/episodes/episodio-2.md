# Episodio 2: Superposición y límites consecutivos

- **Commit:** `51da897`
- **Archivos:** src/models.py, tests/test_reservations.py
- **Metodología:** TDD, pruebas primero en `tests/`.

## Objetivo
Detectar colisiones solo entre reservas ACTIVE de la misma unidad.

## Decisión y criterio
Función pura check_overlap con inicio_A < fin_B y inicio_B < fin_A, intervalos [start, end).

## Verificación
`python -m unittest discover -s tests -v` (estado final del proyecto: 35 tests OK).
