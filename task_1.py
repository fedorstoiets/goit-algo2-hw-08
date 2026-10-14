import random
import time
from collections import OrderedDict


class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key):
        if key not in self.cache:
            return -1

        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)

        self.cache[key] = value

        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)


# LRU cache with required capacity K = 1000
cache = LRUCache(1000)


def range_sum_no_cache(array, left, right):
    """
    Returns sum of array[left:right + 1] without caching.
    """
    return sum(array[left:right + 1])


def update_no_cache(array, index, value):
    """
    Updates one array element without caching.
    """
    array[index] = value


def range_sum_with_cache(array, left, right):
    """
    Returns range sum using LRU cache.
    """
    key = (left, right)

    cached_value = cache.get(key)

    if cached_value != -1:
        return cached_value

    result = sum(array[left:right + 1])
    cache.put(key, result)

    return result


def update_with_cache(array, index, value):
    """
    Updates the array and invalidates all cached ranges
    containing the changed index.
    """
    array[index] = value

    # Linear scan through cache keys as required
    keys_to_delete = []

    for left, right in list(cache.cache.keys()):
        if left <= index <= right:
            keys_to_delete.append((left, right))

    for key in keys_to_delete:
        del cache.cache[key]


def make_queries(
    n,
    q,
    hot_pool=30,
    p_hot=0.95,
    p_update=0.03
):
    hot = [
        (
            random.randint(0, n // 2),
            random.randint(n // 2, n - 1)
        )
        for _ in range(hot_pool)
    ]

    queries = []

    for _ in range(q):
        if random.random() < p_update:
            # ~3% queries are updates
            idx = random.randint(0, n - 1)
            val = random.randint(1, 100)

            queries.append(
                ("Update", idx, val)
            )

        else:
            # ~97% queries are ranges
            if random.random() < p_hot:
                # 95% are hot ranges
                left, right = random.choice(hot)
            else:
                # 5% are random ranges
                left = random.randint(0, n - 1)
                right = random.randint(left, n - 1)

            queries.append(
                ("Range", left, right)
            )

    return queries


def process_queries_no_cache(array, queries):
    for query in queries:
        if query[0] == "Range":
            _, left, right = query
            range_sum_no_cache(
                array,
                left,
                right
            )

        elif query[0] == "Update":
            _, index, value = query
            update_no_cache(
                array,
                index,
                value
            )


def process_queries_with_cache(array, queries):
    for query in queries:
        if query[0] == "Range":
            _, left, right = query
            range_sum_with_cache(
                array,
                left,
                right
            )

        elif query[0] == "Update":
            _, index, value = query
            update_with_cache(
                array,
                index,
                value
            )


def main():
    random.seed(42)

    n = 100_000
    q = 50_000

    # Positive integers only
    original_array = [
        random.randint(1, 100)
        for _ in range(n)
    ]

    queries = make_queries(
        n=n,
        q=q
    )

    # Separate identical copies because Update mutates the array
    array_no_cache = original_array.copy()
    array_with_cache = original_array.copy()

    # Test without cache
    start = time.perf_counter()

    process_queries_no_cache(
        array_no_cache,
        queries
    )

    no_cache_time = (
        time.perf_counter() - start
    )

    # Reset global cache before second benchmark
    global cache
    cache = LRUCache(1000)

    # Test with LRU cache
    start = time.perf_counter()

    process_queries_with_cache(
        array_with_cache,
        queries
    )

    cache_time = (
        time.perf_counter() - start
    )

    speedup = (
        no_cache_time / cache_time
        if cache_time > 0
        else float("inf")
    )

    print("\nРезультати тестування:")
    print("-" * 45)

    print(
        f"Без кешу : {no_cache_time:.4f} с"
    )

    print(
        f"LRU-кеш  : {cache_time:.4f} с "
        f"(прискорення ×{speedup:.2f})"
    )


if __name__ == "__main__":
    main()