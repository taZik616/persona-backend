from datetime import datetime, timedelta

from django.core.cache import cache

# Можно было без blockUntil сделать но я об этом поздно задумался...


class ActionLimiter:
    """
    Интервалы указываются в секундах
    """

    def __init__(self, prefix: str, maxAttempts: int, blockInterval: int, resetInterval: int):
        self.prefix = prefix
        self.maxAttempts = maxAttempts
        self.blockInterval = blockInterval
        self.resetInterval = resetInterval

    def increment(self, identifier: str):
        key = f"{self.prefix}:{identifier}"
        state = cache.get(key)

        if state is None:
            cache.set(
                key,
                {'attempts': 1},
                timeout=self.resetInterval
            )
            return

        blockUntil = state.get('blockUntil')
        if blockUntil is not None and datetime.strptime(blockUntil, '%Y-%m-%d %H:%M:%S.%f') > datetime.now():
            return

        attempts = state.get('attempts', 0) + 1

        if attempts >= self.maxAttempts:
            blockUntil = (datetime.now(
            ) + timedelta(seconds=self.blockInterval)).strftime('%Y-%m-%d %H:%M:%S.%f')
            cache.set(
                key,
                {'attempts': attempts, 'blockUntil': blockUntil},
                timeout=self.resetInterval
            )
        else:
            cache.set(
                key,
                {'attempts': attempts},
                timeout=self.resetInterval
            )

    def getIsBlocked(self, identifier: str) -> bool:
        key = f"{self.prefix}:{identifier}"
        state = cache.get(key)
        if state is None:
            return False

        blockUntil = state.get('blockUntil')
        if blockUntil is not None and datetime.strptime(blockUntil, '%Y-%m-%d %H:%M:%S.%f') > datetime.now():
            return True

        return False
