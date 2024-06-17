import json
from collections import OrderedDict
from datetime import datetime
from log import setup_log

lru_logger = setup_log("lru_cache")


class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = OrderedDict()  # use an OrderedDict to keep track of the order of items in the cache as they are accessed (most recently used items are at the end)
        self.hits = 0
        self.misses = 0
        self.accesses = 0

    def log_event(self, event_type, key, extra=None):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "key": key,
            "cache_size": len(self.cache),
            "capacity": self.capacity
        }
        if extra:  # if extra is not None, extra is a dictionary for any additional stuff we might want to log
            log_entry.update(extra)
        lru_logger.info(json.dumps(log_entry))

    def get(self, key: int):
        self.accesses += 1
        if self.accesses % 100 == 0:  # every 100 accesses, log statistics
            stats = self.calculate_statistics()
            #self.log_event("access_stats", None, stats)
        if key not in self.cache:  # cache miss
            self.misses += 1
            #self.log_event("miss", key)
            return "Not Found"
        else:  # cache hit
            self.hits += 1
            self.cache.move_to_end(key)  # move the item to the end of the cache (most recently used)
            #self.log_event("hit", key)
            return self.cache[key]

    def put(self, key: int, value: any):
        if key in self.cache:
            self.cache.move_to_end(key)
            #self.log_event("update", key)
        else:
            if len(self.cache) >= self.capacity:  # if the cache is full
                popped_item = self.cache.popitem(last=False)  # remove the least recently used item
                self.log_event("evict", popped_item[0], {"evicted_key": popped_item[0]})
            #self.log_event("add", key)
        self.cache[key] = value

    def calculate_statistics(self):
        hit_ratio = self.hits / self.accesses if self.accesses > 0 else 0  # calculate hit ratio (hits / total accesses if there are any accesses)
        miss_ratio = self.misses / self.accesses if self.accesses > 0 else 0  # calculate miss ratio (misses / total accesses if there are any accesses)
        cache_size = len(self.cache) # get the current size of the cache
        return {"hit_ratio": hit_ratio, "miss_ratio": miss_ratio, "cache_size": cache_size}

    def log_metrics(self, event_type, key, latency):
        hit_rate = self.hits / self.accesses if self.accesses > 0 else 0
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "key": key,
            "latency": latency,
            "hit_rate": hit_rate,
            "cache_size": len(self.cache),
            "capacity": self.capacity
        }
        lru_logger.info(json.dumps(log_entry))

