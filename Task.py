from pprint import pprint

import requests


class TaskTracker:
    def __init__(self, url: str = "https://ofc-test-01.tspb.su/test-task/"):
        self.url = url
        self.data = self.get_tasks_data()

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


if __name__ == "__main__":
    tracker = TaskTracker()
    pprint(tracker.data)
