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
            if day["date"] == date:
                return day
        return None

    def _get_day_timeslots(self, day_id: int) -> List[Dict]:
        """Получение всех заявок для конкретного дня"""
        return [slot for slot in self.timeslots if slot["day_id"] == day_id]

    def get_busy_slots_for_date(self, date: str) -> List[Dict]:
        """Найти все занятые промежутки для указанной даты"""
        day = self._get_schedule_by_date(date)
        if not day: return []
        day_id = day["id"]
        return self._get_day_timeslots(day_id)


if __name__ == "__main__":
    tracker = TaskTracker()
    pprint(tracker.data)
    pprint(tracker.get_busy_slots_for_date('2025-02-18'))