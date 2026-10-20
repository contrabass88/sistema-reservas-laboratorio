# Especificación del Sistema de Reservas de Laboratorio (v1.0)

## 1. Problema y Contexto
La coordinación del laboratorio registra préstamos de equipos mediante mensajes y planillas manuales, provocando asignaciones superpuestas para una misma unidad física y bloqueos fantasma cuando una reserva se cancela pero no se libera el horario. Se requiere una solución local, determinista y verificable que gestione la disponibilidad, creación y cancelación de reservas conservando el historial en disco.

## 2. Inventario Estático Autorizado
El sistema opera exclusivamente sobre 5 unidades físicas predefinidas (sin ABM/CRUD de inventario):
- MIC-01: Microscopio digital
- MIC-02: Microscopio digital
- OSC-01: Osciloscopio
- MUL-01: Multímetro
- FUE-01: Fuente de alimentación

## 3. Reglas de Negocio y Supuestos
1. **Identificación:** Cada reserva posee un id único, unit_id, equester (solicitante), start_time, end_time y status (ACTIVE o CANCELLED).
2. **Validación de Solicitante:** equester debe ser una cadena no vacía (se rechazan cadenas vacías "" o compuestas solo por espacios en blanco).
3. **Validación de Unidad:** Solo se admiten reservas sobre los 5 IDs del inventario oficial.
4. **Consistencia Horaria:** Las fechas se procesan en formato ISO-8601 (YYYY-MM-DDTHH:MM:SS o YYYY-MM-DD HH:MM). El inicio debe ser estrictamente anterior al fin (start_time < end_time).
5. **Control de Superposición:** Una reserva ACTIVE ocupa el intervalo semiabierto [start_time, end_time). Dos reservas para la misma unidad se superponen si inicio_A < fin_B y inicio_B < fin_A.
6. **Límites Consecutivos y Simultaneidad:** Se permiten reservas consecutivas en la misma unidad (ej. 10:00-11:00 y 11:00-12:00) y reservas en el mismo horario para unidades distintas (MIC-01 y MIC-02).
7. **Cancelación e Historial:** Cancelar cambia el estado a CANCELLED, liberando el intervalo inmediatamente para consultas y nuevas reservas, pero conservando el registro y su ID en la persistencia.
8. **Persistencia:** Almacenamiento en archivo JSON local (data/reservations.json), recuperable tras detener y reiniciar el proceso.

## 4. Criterios de Aceptación (Verificaciones)
- Creación válida de reserva y persistencia en disco.
- Rechazo de superposición horaria en la misma unidad con reserva activa.
- Aceptación de reservas con límites consecutivos exactos.
- Aceptación de reservas simultáneas en unidades diferentes.
- Rechazo de entradas inválidas (unidad inexistente, solicitante vacío/espacios, start_time >= end_time).
- Cancelación efectiva que libera disponibilidad manteniendo el registro histórico.
- Recuperación íntegra del estado tras reinicio de la instancia del servicio.
