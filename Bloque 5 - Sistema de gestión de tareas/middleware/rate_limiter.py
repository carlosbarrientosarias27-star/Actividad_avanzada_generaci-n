import time
from collections import deque
from config import RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW

_buckets: dict[str, deque] = {}

def is_rate_limited(ip: str) -> bool:
    now = time.time()
    if ip not in _buckets:
        _buckets[ip] = deque()
    bucket = _buckets[ip]
    # Evict old entries outside the sliding window
    while bucket and bucket[0] < now - RATE_LIMIT_WINDOW:
        bucket.popleft()
    if len(bucket) >= RATE_LIMIT_REQUESTS:
        return True
    bucket.append(now)
    return False