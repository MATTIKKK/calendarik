from datetime import datetime

class ConflictError(Exception):
    """Raised when a new event overlaps with an existing one.

    Сервис календаря использует это исключение вместо простого ValueError,
    чтобы слой общения (чат‑бот / API) сам выбирал, как сформулировать ответ
    пользователю.
    """

    def __init__(self, conflict_event):
        self.event = conflict_event
        super().__init__("Scheduling conflict")


class PastTimeError(Exception):
    """Raised when user tries to create an event in the past."""

    def __init__(self, when: datetime):
        self.when = when
        super().__init__("Time already passed")
