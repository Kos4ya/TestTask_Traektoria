from pprint import pprint
from typing import List, Dict, Optional

import requests


class TaskTracker:
    def __init__(self, url: str = "https://ofc-test-01.tspb.su/test-task/"):
        self.url = url
        self.data = self.get_tasks_data()
        self.timeslots = self.data.get("timeslots", [])
        self.days = self.data.get("days", [])

    def get_tasks_data(self):
        """Получение данных о графике из API"""
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ошибка при запросе {e}")

    @staticmethod
    def _time_to_minutes(time_str: str) -> int:
        """Конвертация времени в формате 'ЧЧ:ММ' в минуты"""
        try:
            hours, minutes = map(int, time_str.split(':'))
            return hours * 60 + minutes
        except (ValueError, AttributeError):
            raise ValueError(f"Некорректный формат времени: {time_str}")

    @staticmethod
    def _minutes_to_time(minutes: int) -> str:
        """Конвертация минут в формат времени 'ЧЧ:ММ'"""
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours:02d}:{mins:02d}"

    def _get_schedule_by_date(self, date: str) -> Optional[Dict]:
        """Получение расписания для конкретного дня"""
        for day in self.days:
            if day.get("date") == date:
                return day
        return None

    def _get_day_timeslots(self, day_id: int) -> List[Dict]:
        """Получение всех заявок для конкретного дня"""
        return [slot for slot in self.timeslots if slot.get("day_id") == day_id]

    def get_busy_slots_for_date(self, date: str) -> List[Dict]:
        """Найти все занятые промежутки для указанной даты"""
        day = self._get_schedule_by_date(date)
        if not day: return []
        day_id = day.get("id")
        return self._get_day_timeslots(day_id)

    def get_free_time(self, date: str) -> List[Dict]:
        """Найти свободное время для заданной даты"""
        day = self._get_schedule_by_date(date)
        if not day:
            return []

        work_start = self._time_to_minutes(day.get("start"))
        work_end = self._time_to_minutes(day.get("end"))

        busy_slots = self.get_busy_slots_for_date(date)
        busy_intervals = []
        for slot in busy_slots:
            start = self._time_to_minutes(slot.get("start"))
            end = self._time_to_minutes(slot.get("end"))
            busy_intervals.append((start, end))

        busy_intervals.sort()

        free_intervals = []
        prev_end = work_start

        for start, end in busy_intervals:
            if start > prev_end:
                free_intervals.append({
                    "start": self._minutes_to_time(prev_end),
                    "end": self._minutes_to_time(start)
                })
            prev_end = max(prev_end, end)

        if prev_end < work_end:
            free_intervals.append({
                "start": self._minutes_to_time(prev_end),
                "end": day.get("end")
            })

        return free_intervals

    def is_time_available(self, date: str, start_time: str, end_time: str) -> bool:
        """Проверить доступен ли заданный промежуток времени для заданной даты"""
        day = self._get_schedule_by_date(date)
        if not day:
            return False

        work_start = self._time_to_minutes(day.get("start"))
        work_end = self._time_to_minutes(day.get("end"))
        req_start = self._time_to_minutes(start_time)
        req_end = self._time_to_minutes(end_time)

        if req_start >= req_end:
            return False
        if req_start < work_start or req_end > work_end:
            return False

        busy_slots = self.get_busy_slots_for_date(date)
        for slot in busy_slots:
            slot_start = self._time_to_minutes(slot.get("start"))
            slot_end = self._time_to_minutes(slot.get("end"))

            if not (req_end <= slot_start or req_start >= slot_end):
                return False

        return True

    def find_free_slot_for_duration(self, date: str, duration_minutes: int) -> Optional[Dict]:
        """Найти свободное время для указанной продолжительности заявки"""
        if duration_minutes <= 0:
            return None

        free_slots = self.get_free_time(date)
        for slot in free_slots:
            start = self._time_to_minutes(slot.get("start"))
            end = self._time_to_minutes(slot.get("end"))
            if (end - start) >= duration_minutes:
                return {
                    "start": slot.get("start"),
                    "end": self._minutes_to_time(start + duration_minutes)
                }
        return None


if __name__ == "__main__":
    tracker = TaskTracker()
    pprint(tracker.data)
    pprint(tracker.get_busy_slots_for_date('2025-02-18'))
    pprint(tracker.get_free_time('2025-02-18'))
    pprint(tracker.is_time_available('2025-02-18', "11:00", "12:00"))
    pprint(tracker.find_free_slot_for_duration('2025-02-18', 60))
