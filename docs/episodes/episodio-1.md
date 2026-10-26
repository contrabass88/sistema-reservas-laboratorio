# Episodio 1: Modelado de inventario y validación de entidades

- **Commit:** `98c7f22`
- **Archivos:** src/models.py, tests/test_reservations.py
- **Metodología:** TDD, pruebas primero en `tests/`.

## Objetivo
Definir la entidad Reservation y validar unidad, solicitante y rango horario.

## Decisión y criterio
Se valida en __post_init__ para que no exista una reserva inválida; inventario cargado de data/inventory.json sin modificar IDs.

## Verificación
`python -m unittest discover -s tests -v` (estado final del proyecto: 35 tests OK).
