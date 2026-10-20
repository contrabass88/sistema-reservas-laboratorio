from dataclasses import asdict
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from src.models import Reservation
from src.storage import load_reservations, save_reservations


class TestStorage(unittest.TestCase):
    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.path = Path(directory.name) / "reservations.json"
        self.reservation = Reservation(
            "MIC-01", "Ana Pérez", "2026-10-20T10:00:00", "2026-10-20T11:00:00"
        )

    def test_missing_file_returns_empty_list_without_creating_file(self):
        self.assertEqual(load_reservations(self.path), [])
        self.assertFalse(self.path.exists())

    def test_round_trip_preserves_all_fields_and_history(self):
        cancelled = Reservation(
            "MIC-02", "Luis", "2026-10-20T10:00:00", "2026-10-20T11:00:00"
        )
        cancelled.status = "CANCELLED"
        reservations = [self.reservation, cancelled]
        save_reservations(reservations, self.path)
        self.assertEqual(load_reservations(self.path), reservations)
        self.assertEqual(json.loads(self.path.read_text(encoding="utf-8")),
                         [asdict(res) for res in reservations])

    def test_empty_list_round_trip(self):
        save_reservations([], self.path)
        self.assertEqual(load_reservations(self.path), [])

    def test_atomic_replacement_publishes_complete_json(self):
        save_reservations([], self.path)
        original_replace = Path.replace

        def inspect_replace(temporary, target):
            self.assertEqual(target, self.path)
            self.assertEqual(temporary.parent, self.path.parent)
            self.assertNotEqual(temporary, target)
            self.assertEqual(json.loads(target.read_text(encoding="utf-8")), [])
            self.assertEqual(json.loads(temporary.read_text(encoding="utf-8")),
                             [asdict(self.reservation)])
            return original_replace(temporary, target)

        with patch.object(Path, "replace", autospec=True, side_effect=inspect_replace) as replace:
            save_reservations([self.reservation], self.path)
        replace.assert_called_once()
        self.assertEqual(load_reservations(self.path), [self.reservation])
        self.assertEqual(list(self.path.parent.iterdir()), [self.path])

    def test_failed_replacement_preserves_original_and_cleans_temporary(self):
        save_reservations([], self.path)
        original = self.path.read_bytes()
        with patch.object(Path, "replace", side_effect=OSError("disk error")):
            with self.assertRaises(OSError):
                save_reservations([self.reservation], self.path)
        self.assertEqual(self.path.read_bytes(), original)
        self.assertEqual(list(self.path.parent.iterdir()), [self.path])

    def test_failed_serialization_preserves_original(self):
        save_reservations([], self.path)
        with patch("src.storage.json.dump", side_effect=TypeError("serialization error")):
            with self.assertRaises(TypeError):
                save_reservations([self.reservation], self.path)
        self.assertEqual(load_reservations(self.path), [])
        self.assertEqual(list(self.path.parent.iterdir()), [self.path])

    def test_invalid_json_or_records_are_not_silently_discarded(self):
        record = asdict(self.reservation)
        for content in ("broken", "{}", '[{}]', json.dumps([{**record, "status": "UNKNOWN"}])):
            with self.subTest(content=content):
                self.path.write_text(content, encoding="utf-8")
                with self.assertRaises(ValueError):
                    load_reservations(self.path)
                self.assertEqual(self.path.read_text(encoding="utf-8"), content)


if __name__ == "__main__":
    unittest.main()
