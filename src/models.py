"""Entidades y validaciones del dominio de reservas del laboratorio."""

from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path
from uuid import uuid4


INVENTORY_PATH = Path(__file__).resolve().parent.parent / "data" / "inventory.json"


def load_inventory() -> list[dict[str, str]]:
    """Lee el inventario oficial sin modificarlo, independientemente del cwd."""
    with INVENTORY_PATH.open(encoding="utf-8-sig") as inventory_file:
        return json.load(inventory_file)


def _parse_time(value: str) -> datetime:
    """Procesa una fecha ISO-8601 que incluya fecha y hora."""
    if not isinstance(value, str) or len(value) < 16 or value[10] not in ("T", " "):
        raise ValueError("La fecha debe incluir fecha y hora en formato ISO-8601")
    try:
        return datetime.fromisoformat(value)
    except ValueError as error:
        raise ValueError("Fecha ISO-8601 inválida") from error


@dataclass
class Reservation:
    """Reserva nueva y activa para el intervalo semiabierto [inicio, fin)."""

    unit_id: str
    requester: str
    start_time: str
    end_time: str
    id: str = field(default_factory=lambda: str(uuid4()), init=False)
    status: str = field(default="ACTIVE", init=False)

    def __post_init__(self) -> None:
        if self.unit_id not in [unit["id"] for unit in load_inventory()]:
            raise ValueError("La unidad no pertenece al inventario autorizado")
        if not isinstance(self.requester, str) or not self.requester.strip():
            raise ValueError("El solicitante debe ser una cadena no vacía")

        start = _parse_time(self.start_time)
        end = _parse_time(self.end_time)
        try:
            valid_interval = start < end
        except TypeError as error:
            raise ValueError("Las fechas deben usar zonas horarias compatibles") from error
        if not valid_interval:
            raise ValueError("El inicio debe ser estrictamente anterior al fin")
