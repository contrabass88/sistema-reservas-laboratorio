import unittest
from uuid import UUID

from src.models import Reservation, load_inventory
from src import models


class InventoryTests(unittest.TestCase):
    def test_inventory_contains_exactly_the_five_authorized_units(self):
        inventory = load_inventory()
        self.assertEqual(len(inventory), 5)
        self.assertEqual(
            {unit["id"] for unit in inventory},
            {"MIC-01", "MIC-02", "OSC-01", "MUL-01", "FUE-01"},
        )
        self.assertTrue(all(unit["name"].strip() for unit in inventory))


class ReservationTests(unittest.TestCase):
    def make_reservation(self, **changes):
        values = {
            "unit_id": "MIC-01",
            "requester": "Ana Pérez",
            "start_time": "2026-10-20T10:00:00",
            "end_time": "2026-10-20T11:00:00",
        }
        values.update(changes)
        return Reservation(**values)

    def test_valid_reservation_has_generated_unique_id_and_active_status(self):
        reservation = self.make_reservation()
        self.assertEqual(str(UUID(reservation.id)), reservation.id)
        self.assertNotEqual(reservation.id, self.make_reservation().id)
        self.assertEqual(reservation.unit_id, "MIC-01")
        self.assertEqual(reservation.requester, "Ana Pérez")
        self.assertEqual(reservation.start_time, "2026-10-20T10:00:00")
        self.assertEqual(reservation.end_time, "2026-10-20T11:00:00")
        self.assertEqual(reservation.status, "ACTIVE")

    def test_all_authorized_units_can_be_reserved(self):
        for unit_id in ("MIC-01", "MIC-02", "OSC-01", "MUL-01", "FUE-01"):
            with self.subTest(unit_id=unit_id):
                self.assertEqual(self.make_reservation(unit_id=unit_id).unit_id, unit_id)

    def test_unknown_unit_is_rejected(self):
        for unit_id in ("MIC-03", "", "mic-01", None):
            with self.subTest(unit_id=unit_id), self.assertRaises(ValueError):
                self.make_reservation(unit_id=unit_id)

    def test_empty_or_non_string_requester_is_rejected(self):
        for requester in ("", "   ", "\t\n", None, 123):
            with self.subTest(requester=requester), self.assertRaises(ValueError):
                self.make_reservation(requester=requester)

    def test_equal_or_reversed_times_are_rejected(self):
        for end_time in ("2026-10-20T10:00:00", "2026-10-20T09:00:00"):
            with self.subTest(end_time=end_time), self.assertRaises(ValueError):
                self.make_reservation(end_time=end_time)

    def test_invalid_iso_dates_are_rejected_in_either_field(self):
        for field in ("start_time", "end_time"):
            for value in ("", "not-a-date", "20/10/2026 10:00", "2026-02-30T10:00:00",
                          "2026-10-20T25:00:00", "2026-10-20", None):
                with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                    self.make_reservation(**{field: value})

    def test_space_separated_iso_dates_are_supported(self):
        reservation = self.make_reservation(
            start_time="2026-10-20 10:00", end_time="2026-10-20 11:00"
        )
        self.assertEqual(reservation.status, "ACTIVE")

    def test_times_are_compared_as_datetimes(self):
        with self.assertRaises(ValueError):
            self.make_reservation(
                start_time="2026-10-20 11:00", end_time="2026-10-20T10:00:00"
            )

    def test_mixed_timezone_awareness_is_rejected_with_value_error(self):
        with self.assertRaises(ValueError):
            self.make_reservation(end_time="2026-10-20T11:00:00+00:00")


class TestOverlaps(unittest.TestCase):
    def setUp(self):
        self.existing = self.make_reservation("10:00", "11:00")

    def make_reservation(self, start, end, unit_id="MIC-01", separator="T"):
        return Reservation(
            unit_id=unit_id,
            requester="Ana",
            start_time=f"2026-10-20{separator}{start}:00",
            end_time=f"2026-10-20{separator}{end}:00",
        )

    def test_direct_overlap_is_detected_on_both_sides(self):
        for start, end in (("09:30", "10:30"), ("10:30", "11:30")):
            with self.subTest(start=start, end=end):
                new_res = self.make_reservation(start, end)
                self.assertTrue(models.check_overlap(new_res, [self.existing]))

    def test_contained_intervals_are_detected_in_both_directions(self):
        for start, end in (("10:15", "10:45"), ("09:00", "12:00")):
            with self.subTest(start=start, end=end):
                new_res = self.make_reservation(start, end)
                self.assertTrue(models.check_overlap(new_res, [self.existing]))

    def test_identical_intervals_on_same_unit_overlap(self):
        new_res = self.make_reservation("10:00", "11:00")
        self.assertTrue(models.check_overlap(new_res, [self.existing]))

    def test_exact_consecutive_boundaries_are_allowed_in_both_directions(self):
        for start, end in (("09:00", "10:00"), ("11:00", "12:00")):
            with self.subTest(start=start, end=end):
                new_res = self.make_reservation(start, end)
                self.assertFalse(models.check_overlap(new_res, [self.existing]))

    def test_simultaneous_reservations_on_different_units_are_allowed(self):
        new_res = self.make_reservation("10:00", "11:00", unit_id="MIC-02")
        self.assertFalse(models.check_overlap(new_res, [self.existing]))

    def test_separated_intervals_are_allowed(self):
        for start, end in (("08:00", "09:00"), ("12:00", "13:00")):
            with self.subTest(start=start, end=end):
                new_res = self.make_reservation(start, end)
                self.assertFalse(models.check_overlap(new_res, [self.existing]))

    def test_empty_list_has_no_overlap(self):
        self.assertFalse(models.check_overlap(self.existing, []))

    def test_cancelled_reservation_does_not_block(self):
        self.existing.status = "CANCELLED"
        new_res = self.make_reservation("10:00", "11:00")
        self.assertFalse(models.check_overlap(new_res, [self.existing]))

    def test_conflict_after_non_conflicting_reservation_is_detected(self):
        other_unit = self.make_reservation("10:00", "11:00", unit_id="MIC-02")
        new_res = self.make_reservation("10:30", "11:30")
        reservations = [other_unit, self.existing]
        before = [vars(res).copy() for res in [new_res, *reservations]]
        self.assertTrue(models.check_overlap(new_res, reservations))
        self.assertEqual(reservations, [other_unit, self.existing])
        self.assertEqual([vars(res) for res in [new_res, *reservations]], before)

    def test_mixed_iso_formats_are_compared_chronologically(self):
        new_res = self.make_reservation("10:30", "11:30", separator=" ")
        self.assertTrue(models.check_overlap(new_res, [self.existing]))


if __name__ == "__main__":
    unittest.main()
