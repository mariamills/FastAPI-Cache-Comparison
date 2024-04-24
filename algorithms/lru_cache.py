from collections import OrderedDict
from log import setup_log

lru_logger = setup_log("lru_cache")

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key: int):
        if key not in self.cache:
            lru_logger.info(f"LRU CACHE MISS: Item {key} not found")
            return "Not Found"
        else:
            lru_logger.info(f"LRU CACHE HIT: Item {key} found in cache")
            self.cache.move_to_end(key)
            return self.cache[key]

    def put(self, key: int, value: any):
        if key in self.cache:
            self.cache.move_to_end(key)
            lru_logger.info(f"LRU UPDATE: Item {key} moved to end")
        else:
            lru_logger.info(f"LRU ADD: Item {key} added to cache")
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            popped_item = self.cache.popitem(last=False)
            lru_logger.info(f"LRU EVICT: Item {popped_item[0]} evicted from cache")
