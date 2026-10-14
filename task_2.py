import random
import time
from collections import deque
from typing import Dict


class SlidingWindowRateLimiter:
    def __init__(
        self,
        window_size: int = 10,
        max_requests: int = 1
    ):
        if window_size <= 0:
            raise ValueError(
                "window_size must be greater than 0"
            )

        if max_requests <= 0:
            raise ValueError(
                "max_requests must be greater than 0"
            )

        self.window_size = window_size
        self.max_requests = max_requests

        # user_id -> deque of message timestamps
        self.user_requests: Dict[str, deque] = {}

    def _cleanup_window(
        self,
        user_id: str,
        current_time: float
    ) -> None:
        """
        Removes messages that are outside
        the current sliding window.
        """

        if user_id not in self.user_requests:
            return

        requests = self.user_requests[user_id]

        while (
            requests
            and current_time - requests[0]
            >= self.window_size
        ):
            requests.popleft()

        # Remove user completely if no active messages remain
        if not requests:
            del self.user_requests[user_id]

    def can_send_message(
        self,
        user_id: str
    ) -> bool:
        """
        Checks whether user can send a new message.
        """

        current_time = time.time()

        self._cleanup_window(
            user_id,
            current_time
        )

        # First message is always allowed
        if user_id not in self.user_requests:
            return True

        return (
            len(self.user_requests[user_id])
            < self.max_requests
        )

    def record_message(
        self,
        user_id: str
    ) -> bool:
        """
        Records a message if it is allowed.
        """

        if not self.can_send_message(user_id):
            return False

        current_time = time.time()

        if user_id not in self.user_requests:
            self.user_requests[user_id] = deque()

        self.user_requests[user_id].append(
            current_time
        )

        return True

    def time_until_next_allowed(
        self,
        user_id: str
    ) -> float:
        """
        Returns waiting time in seconds until
        the next message can be sent.
        """

        current_time = time.time()

        self._cleanup_window(
            user_id,
            current_time
        )

        if user_id not in self.user_requests:
            return 0.0

        requests = self.user_requests[user_id]

        if len(requests) < self.max_requests:
            return 0.0

        oldest_request = requests[0]

        wait_time = (
            self.window_size
            - (current_time - oldest_request)
        )

        return max(0.0, wait_time)


def test_rate_limiter():
    # Window 10 seconds, one message
    limiter = SlidingWindowRateLimiter(
        window_size=10,
        max_requests=1
    )

    print("\n=== Симуляція потоку повідомлень ===")

    for message_id in range(1, 11):
        user_id = message_id % 5 + 1

        result = limiter.record_message(
            str(user_id)
        )

        wait_time = (
            limiter.time_until_next_allowed(
                str(user_id)
            )
        )

        print(
            f"Повідомлення {message_id:2d} | "
            f"Користувач {user_id} | "
            f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}"
        )

        time.sleep(
            random.uniform(0.1, 1.0)
        )

    print("\nОчікуємо 4 секунди...")
    time.sleep(4)

    print(
        "\n=== Нова серія повідомлень після очікування ==="
    )

    for message_id in range(11, 21):
        user_id = message_id % 5 + 1

        result = limiter.record_message(
            str(user_id)
        )

        wait_time = (
            limiter.time_until_next_allowed(
                str(user_id)
            )
        )

        print(
            f"Повідомлення {message_id:2d} | "
            f"Користувач {user_id} | "
            f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}"
        )

        time.sleep(
            random.uniform(0.1, 1.0)
        )


if __name__ == "__main__":
    test_rate_limiter()