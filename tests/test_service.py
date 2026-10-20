from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.service import Service
from src.storage import load_reservations


class TestService(unittest.TestCase):
    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.path = Path(directory.name) / "reservations.json"
        self.service = Service(self.path)

    def create(self, **changes):
        values = dict(unit_id="MIC-01", requester="Ana",
                      start_time="2026-10-20T10:00:00", end_time="2026-10-20T11:00:00")
        values.update(changes)
        return self.service.create_reservation(**values)

    def test_valid_creation_persists_reservation(self):
        reservation = self.create()
        self.assertEqual(reservation.status, "ACTIVE")
        self.assertEqual(load_reservations(self.path), [reservation])

    def test_overlap_raises_without_changing_disk(self):
        self.create()
        original = self.path.read_bytes()
        with self.assertRaises(ValueError):
            self.create(start_time="2026-10-20T10:30:00", end_time="2026-10-20T11:30:00")
        self.assertEqual(self.path.read_bytes(), original)

    def test_consecutive_and_different_units_are_persisted(self):
        first = self.create()
        second = self.create(start_time="2026-10-20T11:00:00", end_time="2026-10-20T12:00:00")
        third = self.create(unit_id="MIC-02")
        self.assertEqual(load_reservations(self.path), [first, second, third])

    def test_invalid_creation_does_not_create_file(self):
        with self.assertRaises(ValueError):
            self.create(requester="   ")
        self.assertFalse(self.path.exists())

    def test_cancellation_preserves_history_and_releases_interval_after_restart(self):
        first = self.create()
        other = self.create(unit_id="MIC-02")
        cancelled = self.service.cancel_reservation(first.id)
        self.assertEqual(cancelled.id, first.id)
        self.assertEqual(cancelled.status, "CANCELLED")
        self.assertEqual(load_reservations(self.path), [cancelled, other])
        self.service = Service(self.path)
        replacement = self.create()
        self.assertNotEqual(replacement.id, first.id)
        self.assertEqual(load_reservations(self.path), [cancelled, other, replacement])

    def test_restarted_service_rejects_persisted_overlap(self):
        self.create()
        self.service = Service(self.path)
        with self.assertRaises(ValueError):
            self.create()

    def test_unknown_cancellation_preserves_file(self):
        self.create()
        original = self.path.read_bytes()
        with self.assertRaises(ValueError):
            self.service.cancel_reservation("unknown")
        self.assertEqual(self.path.read_bytes(), original)

    def test_repeated_cancellation_is_idempotent(self):
        first = self.create()
        cancelled = self.service.cancel_reservation(first.id)
        self.assertEqual(self.service.cancel_reservation(first.id), cancelled)
        self.assertEqual(load_reservations(self.path), [cancelled])


if __name__ == "__main__":
    unittest.main()
