"""Persistencia JSON con reemplazo atómico del archivo completo."""

from dataclasses import asdict
import json
from pathlib import Path
from uuid import uuid4

from src.models import Reservation


DEFAULT_PATH = Path(__file__).resolve().parent.parent / "data" / "reservations.json"


def load_reservations(path: Path = DEFAULT_PATH) -> list[Reservation]:
    """Recupera reservas con sus IDs y estados originales; no oculta corrupción."""
    try:
        with Path(path).open(encoding="utf-8-sig") as source:
            records = json.load(source)
    except FileNotFoundError:
        return []
    if not isinstance(records, list):
        raise ValueError("El archivo de reservas debe contener una lista")

    reservations = []
    for record in records:
        expected = {"id", "unit_id", "requester", "start_time", "end_time", "status"}
        if not isinstance(record, dict) or set(record) != expected:
            raise ValueError("Registro de reserva inválido")
        if not isinstance(record["id"], str) or not record["id"].strip():
            raise ValueError("ID de reserva inválido")
        if record["status"] not in ("ACTIVE", "CANCELLED"):
            raise ValueError("Estado de reserva inválido")
        reservation = Reservation(
            unit_id=record["unit_id"],
            requester=record["requester"],
            start_time=record["start_time"],
            end_time=record["end_time"],
        )
        reservation.id = record["id"]
        reservation.status = record["status"]
        reservations.append(reservation)
    return reservations


def save_reservations(reservations: list[Reservation], path: Path = DEFAULT_PATH) -> None:
    """Escribe en un temporal vecino y lo publica con un único reemplazo.

    El archivo previo queda intacto si falla la escritura o el reemplazo.
    El directorio destino debe existir. No coordina escritores concurrentes.
    """
    destination = Path(path)
    temporary = destination.with_name(f".{destination.name}.{uuid4().hex}.tmp")
    target = temporary.open("x", encoding="utf-8")
    try:
        with target:
            json.dump([asdict(reservation) for reservation in reservations], target,
                      ensure_ascii=False, indent=2)
        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)
