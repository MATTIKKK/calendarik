from collections import defaultdict
from typing import List, Dict

class MemoryStore:
    """
    chat_id → список последних N сообщений вида
    {"role": "user" | "assistant", "content": "..."}
    """
    def __init__(self, max_messages: int = 10) -> None:
        self._data: Dict[int, List[dict]] = defaultdict(list)
        self.max_messages = max_messages

    def add(self, chat_id: int, role: str, content: str) -> None:
        self._data[chat_id].append({"role": role, "content": content})

        self._data[chat_id] = self._data[chat_id][-self.max_messages :]

    def get(self, chat_id: int) -> List[dict]:
        return self._data[chat_id]
