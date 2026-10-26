# Sistema de Reservas de Laboratorio

**Autor:** Gastón Osvaldo Rodríguez

**Carrera:** Licenciatura en Sistemas de la Información

**Materia:** Tópicos Avanzados

**Profesor:**  Emanuel Irrazabal

---

## 1. Especificación Breve

**Problema y Alcance:**

La coordinación del laboratorio requiere un sistema determinista para registrar y consultar préstamos de equipos físicos, solucionando las asignaciones superpuestas y los bloqueos de disponibilidad causados por cancelaciones mal gestionadas. El alcance se limita a la operación sobre un inventario estático de 5 unidades, excluyendo administración de inventario, interfaces gráficas, despliegue en la nube y manejo de usuarios reales.

**Reglas de Negocio y Supuestos:**

- **Identificación y Entidad:** Toda reserva posee un UUID, ID de unidad válido, nombre del solicitante (no vacío), marca temporal de inicio y fin (estrictamente `inicio < fin` en formato ISO-8601), y estado (`ACTIVE` o `CANCELLED`).

- **Superposición (Intervalo Semiabierto):** Una reserva `ACTIVE` ocupa el intervalo `[inicio, fin)`. Se permiten reservas con límites consecutivos exactos (ej. 10:00-11:00 y 11:00-12:00) y reservas simultáneas en distintas unidades físicas.

- **Historial:** La cancelación libera el intervalo horario para disponibilidad, pero mantiene el registro persistido en disco con estado `CANCELLED` para trazabilidad.

**Evolución e Historial:** 

La especificación base y el inventario estático fueron documentados en la inicialización del proyecto.

\*(Evidencia: Commit `71b1cd8` - docs: especificacion inicial v1.0)\*

---

## 2. Solución y Decisiones Técnicas

**Estructura y Decisiones Arquitecturales:**

- **Lenguaje:** Python 3.12 utilizando exclusivamente la librería estándar (`dataclasses`, `datetime`, `json`, `pathlib`, `uuid`, `unittest`). Esto garantiza un entorno 100% reproducible sin dependencias externas (`pip`).

- **Persistencia:** Almacenamiento local atómico en JSON (`data/reservations.json`). La escritura atómica (mediante `tempfile` y `replace`) evita la corrupción de datos ante interrupciones repentinas del servicio.

- **Validación Matemática:** La detección de colisiones se resuelve mediante una función pura evaluando `inicio_A < fin_B` y `inicio_B < fin_A` aislando la lógica de negocio de la capa de datos.

**Instrucciones de Ejecución:**

\*Requisitos previos:\* Python 3.12+

1. Clonar el repositorio.

2. Ejecutar la suite completa de pruebas (35 tests):

   \`\`\`bash

   python -m unittest discover -s tests -v
   ```

3. Uso programático de la capa de servicio (la CLI de `src/cli.py` figura en la estructura autorizada pero **aún no está implementada**):

   ```python
   from src.service import Service

   svc = Service()  # persiste en data/reservations.json
   r = svc.create_reservation("MIC-01", "Ana", "2026-10-26T10:00:00", "2026-10-26T11:00:00")
   svc.cancel_reservation(r.id)  # borrado lógico: status = "CANCELLED"
   ```

**Estructura del proyecto:**

```text
data/inventory.json         Inventario estático (5 equipos, solo lectura)
data/reservations.json      Persistencia de reservas (se genera al usar el servicio)
src/models.py               Entidades, validaciones y check_overlap
src/storage.py              Lectura y escritura atómica JSON
src/service.py              Creación y cancelación de reservas
tests/                      35 pruebas (models, storage, service)
docs/episodes/              Trazabilidad por episodio
PROGRESS.md                 Bitácora, verificación y decisiones
```

**Resultados de verificación:**

| Verificación | Resultado |
|---|---|
| `python -m unittest discover -s tests -v` | 35 tests, OK |
| Pruebas de dominio (`test_reservations.py`) | 20 |
| Pruebas de persistencia (`test_storage.py`) | 7 |
| Pruebas de servicio (`test_service.py`) | 8 |

---

## 3. Preparación del Agente

El comportamiento del agente se delimita en `AGENTS.md`: Python 3.12 con librería estándar, metodología TDD (pruebas antes que lógica de negocio), IDs de inventario inmutables, borrado lógico y comparación horaria con intervalos semiabiertos.

---

## 4. Registro de Decisiones y Episodios

| Episodio | Objetivo | Commit | Detalle |
|---|---|---|---|
| 1 | Modelado de inventario y validación de entidades | `98c7f22` | [docs/episodes/episodio-1.md](docs/episodes/episodio-1.md) |
| 2 | Superposición y límites consecutivos | `51da897` | [docs/episodes/episodio-2.md](docs/episodes/episodio-2.md) |
| 3 | Persistencia atómica JSON y capa de servicio | `f05e8e0` | [docs/episodes/episodio-3.md](docs/episodes/episodio-3.md) |

Bitácora completa y decisiones técnicas en [PROGRESS.md](PROGRESS.md).

**Limitaciones:** sin interfaz (CLI pendiente), sin autenticación, sin concurrencia entre procesos (único escritor), sin administración de inventario ni despliegue en la nube.
