# Bitácora de Progreso

## Estado actual
- 35 pruebas pasan (`python -m unittest discover -s tests -v`).
- Implementado: modelos y validaciones, superposición, persistencia atómica, servicio.
- Pendiente: `src/cli.py` (autorizado en `AGENTS.md`, no implementado).

## Historial
| Fecha | Commit | Hito |
|---|---|---|
| 2026-10-20 | `71b1cd8` | Especificación v1.0, inventario y harness |
| 2026-10-20 | `98c7f22` | Episodio 1: modelado y validación (TDD) |
| 2026-10-20 | `51da897` | Episodio 2: superposición y límites consecutivos |
| 2026-10-20 | `f05e8e0` | Episodio 3: persistencia atómica y servicio |
| 2026-10-20 | `32bf01c` | Documentación final |

## Decisiones técnicas
- **Intervalos semiabiertos** `[start, end)`: permiten reservas consecutivas exactas.
- **Borrado lógico** (`CANCELLED`): conserva trazabilidad y libera disponibilidad.
- **Escritura atómica** (archivo temporal + `replace`): evita corrupción ante interrupciones.
- **Servicio sin caché**: lee el estado del disco en cada operación (único escritor local).
- **Cancelación idempotente**: cancelar dos veces no falla ni reescribe.
- **Solo librería estándar**: entorno reproducible sin `pip`.
