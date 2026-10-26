# Episodio 3: Persistencia atómica JSON y capa de servicio

- **Commit:** `f05e8e0`
- **Archivos:** src/storage.py, src/service.py, tests/test_storage.py, tests/test_service.py
- **Metodología:** TDD, pruebas primero en `tests/`.

## Objetivo
Persistir reservas en data/reservations.json y exponer crear/cancelar.

## Decisión y criterio
Escritura atómica con archivo temporal y replace; cancelación lógica que conserva el registro.

## Verificación
`python -m unittest discover -s tests -v` (estado final del proyecto: 35 tests OK).
