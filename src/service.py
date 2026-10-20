"""Orquestación de reservas para uso local con un único escritor."""

from pathlib import Path

from src.models import Reservation, check_overlap
from src.storage import DEFAULT_PATH, load_reservations, save_reservations


class Service:
    """Lee el estado persistido en cada operación, sin mantener una caché."""

    def __init__(self, path: Path = DEFAULT_PATH) -> None:
        self.path = Path(path)

    def create_reservation(
        self, unit_id: str, requester: str, start_time: str, end_time: str
    ) -> Reservation:
        reservation = Reservation(unit_id, requester, start_time, end_time)
        reservations = load_reservations(self.path)
        if check_overlap(reservation, reservations):
            raise ValueError("La reserva se superpone con una reserva activa")
        reservations.append(reservation)
        save_reservations(reservations, self.path)
        return reservation

    def cancel_reservation(self, reservation_id: str) -> Reservation:
        """Cancela conservando el registro; repetir la cancelación es inocuo."""
        reservations = load_reservations(self.path)
        for reservation in reservations:
            if reservation.id == reservation_id:
                if reservation.status != "CANCELLED":
                    reservation.status = "CANCELLED"
                    save_reservations(reservations, self.path)
                return reservation
        raise ValueError("No existe una reserva con ese ID")
