"""Short-lived, server-side state for multi-step rounds (theory threads, DSA problems).

The Streamlit UI keeps this in `st.session_state`. Here it lives on the server and the browser
only holds an opaque id, so a visitor can never feed tampered graph state (such as another
user's interview id) back into the graphs. State is per process and expires, which is fine for
a single-instance deployment; a restart simply ends any round in progress.
"""

import threading
import time
import uuid
from collections import OrderedDict
from dataclasses import dataclass, field


@dataclass
class Entry:
    user_id: str
    session_id: str
    kind: str
    data: dict
    touched: float = field(default_factory=time.time)
    lock: threading.Lock = field(default_factory=threading.Lock)


class ThreadStore:
    def __init__(self, ttl_seconds: int = 2 * 3600, max_items: int = 500):
        self._items: OrderedDict[str, Entry] = OrderedDict()
        self._guard = threading.Lock()
        self._ttl = ttl_seconds
        self._max = max_items

    def _purge(self, now: float) -> None:
        for key in [k for k, e in self._items.items() if now - e.touched > self._ttl]:
            del self._items[key]
        while len(self._items) > self._max:
            self._items.popitem(last=False)

    def create(self, user_id: str, session_id: str, kind: str, data: dict) -> str:
        key = uuid.uuid4().hex
        now = time.time()
        with self._guard:
            self._purge(now)
            self._items[key] = Entry(user_id, session_id, kind, data, touched=now)
        return key

    def get(self, key: str, user_id: str, session_id: str, kind: str) -> Entry | None:
        """The entry, only if it belongs to this user, session and kind and has not expired."""
        now = time.time()
        with self._guard:
            self._purge(now)
            entry = self._items.get(key)
            if entry is None or (entry.user_id, entry.session_id, entry.kind) != (user_id, session_id, kind):
                return None
            entry.touched = now
            self._items.move_to_end(key)
            return entry

    def drop_user(self, user_id: str) -> None:
        with self._guard:
            for key in [k for k, e in self._items.items() if e.user_id == user_id]:
                del self._items[key]


store = ThreadStore()
