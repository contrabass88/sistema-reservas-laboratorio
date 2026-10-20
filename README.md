# Sistema de Reservas de Laboratorio

**Autor:** Gastón Osvaldo Rodríguez

**Carrera:** Licenciatura en Sistemas de la Información

**Materia:** Tópicos Avanzados

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