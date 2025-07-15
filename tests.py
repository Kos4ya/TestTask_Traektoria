import unittest
from unittest.mock import patch
from a import ScheduleManager


class TestScheduleManager(unittest.TestCase):
    @patch('requests.get')
    def setUp(self, mock_get):
        # Мокаем API ответ
        mock_get.return_value.json.return_value = {
            "days": [
                {"id": 1, "date": "2024-10-10", "start": "09:00", "end": "18:00"},
                {"id": 2, "date": "2024-10-11", "start": "08:00", "end": "17:00"}
            ],
            "timeslots": [
                {"id": 1, "day_id": 1, "start": "11:00", "end": "12:00"},
                {"id": 2, "day_id": 1, "start": "14:00", "end": "15:30"},
                {"id": 3, "day_id": 2, "start": "09:30", "end": "16:00"}
            ]
        }
        self.manager = ScheduleManager()

    def test_get_busy_slots(self):
        # Тест для получения занятых слотов
        result = self.manager.get_busy_slots("2024-10-10")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["start"], "11:00")
        self.assertEqual(result[0]["end"], "12:00")

        # Тест для несуществующей даты
        result = self.manager.get_busy_slots("2024-10-12")
        self.assertEqual(len(result), 0)

    def test_get_free_time(self):
        # Тест для получения свободного времени
        result = self.manager.get_free_time("2024-10-10")
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["start"], "09:00")
        self.assertEqual(result[0]["end"], "11:00")
        self.assertEqual(result[1]["start"], "12:00")
        self.assertEqual(result[1]["end"], "14:00")
        self.assertEqual(result[2]["start"], "15:30")
        self.assertEqual(result[2]["end"], "18:00")

        # Тест для дня, когда занято все время
        result = self.manager.get_free_time("2024-10-11")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["start"], "08:00")
        self.assertEqual(result[0]["end"], "09:30")
        self.assertEqual(result[1]["start"], "16:00")
        self.assertEqual(result[1]["end"], "17:00")

    def test_is_time_available(self):
        # Тест доступного времени
        self.assertTrue(self.manager.is_time_available("2024-10-10", "10:00", "11:00"))
        self.assertTrue(self.manager.is_time_available("2024-10-10", "12:30", "13:30"))

        # Тест занятого времени
        self.assertFalse(self.manager.is_time_available("2024-10-10", "11:30", "12:30"))
        self.assertFalse(self.manager.is_time_available("2024-10-10", "10:30", "11:30"))

        # Тест времени вне рабочего дня
        self.assertFalse(self.manager.is_time_available("2024-10-10", "08:00", "09:00"))
        self.assertFalse(self.manager.is_time_available("2024-10-10", "18:00", "19:00"))

    def test_find_free_slot_for_duration(self):
        # Тест поиска слота по продолжительности
        result = self.manager.find_free_slot_for_duration("2024-10-10", 60)
        self.assertIsNotNone(result)
        self.assertEqual(result["start"], "09:00")
        self.assertEqual(result["end"], "10:00")

        result = self.manager.find_free_slot_for_duration("2024-10-10", 120)
        self.assertIsNotNone(result)
        self.assertEqual(result["start"], "09:00")
        self.assertEqual(result["end"], "11:00")

        # Тест для слишком долгой продолжительности
        result = self.manager.find_free_slot_for_duration("2024-10-11", 240)
        self.assertIsNone(result)

    def test_invalid_time_format(self):
        # Тест обработки неверного формата времени
        with self.assertRaises(ValueError):
            self.manager._time_to_minutes("25:00")

        with self.assertRaises(ValueError):
            self.manager._time_to_minutes("abc")


if __name__ == '__main__':
    unittest.main()