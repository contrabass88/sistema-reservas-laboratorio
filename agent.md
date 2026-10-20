# Harness del Agente (agent.md)

## 1. Entorno y Metodología Obligatoria
- **Lenguaje y Runtime:** Python 3.12 (Librería estándar exclusivamente: dataclasses, datetime, json, pathlib, unittest, uuid). Prohibido instalar paquetes externos vía pip.
- **Metodología:** TDD (Test-Driven Development) e iteración acotada (ODD). Antes de implementar o modificar lógica de negocio en src/, debes crear o actualizar las pruebas unitarias en 	ests/test_reservations.py.
- **Ejecución de pruebas:** python -m unittest discover -s tests -v

## 2. Estructura del Proyecto Autorizada
- data/inventory.json: Inventario estático de solo lectura (5 equipos).
- data/reservations.json: Archivo de persistencia de reservas (activas y canceladas).
- src/models.py: Definición de entidades y validaciones de dominio.
- src/storage.py: Lectura y escritura atómica en disco (JSON).
- src/service.py: Lógica de disponibilidad, creación y cancelación de reservas.
- src/cli.py: Interfaz de línea de comandos para operar el sistema localmente.
- 	ests/test_reservations.py: Suite de pruebas automatizadas.

## 3. Restricciones Estrictas para el Agente
- NO modificar los IDs del inventario (MIC-01, MIC-02, OSC-01, MUL-01, FUE-01).
- NO eliminar físicamente registros al cancelar (usar borrado lógico status = "CANCELLED").
- NO agregar interfaces web, bases de datos externas ni autenticación.
- Toda comparación horaria debe tratar los intervalos como semiabiertos [start_time, end_time).
