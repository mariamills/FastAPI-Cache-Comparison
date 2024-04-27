import json
from datetime import datetime
from collections import OrderedDict, defaultdict
from log import setup_log

lfu_logger = setup_log("lfu_cache")


class LFUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}  # Key to {value, frequency}
        self.freq = defaultdict(OrderedDict)  # defaultdict is a dictionary that provides a default value for a key
        self.min_freq = 0  # minimum frequency of all keys in the cache (start at 0, use to track the least frequently used item)
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
        lfu_logger.info(json.dumps(log_entry))

    def get(self, key: int):
        self.accesses += 1
        if key not in self.cache:  # cache miss! key (item) not found in cache
            self.misses += 1
            self.log_event("miss", key)
            return "Not Found"
        else:  # cache hit!
            self.hits += 1
            value, freq = self.cache[key]  # get value and frequency of key
            del self.freq[freq][key]  # remove key from current frequency
            if not self.freq[freq]:  # if freq is not
                del self.freq[freq]
                if self.min_freq == freq:
                    self.min_freq += 1

            new_freq = freq + 1
            self.freq[new_freq][key] = None
            self.cache[key] = (value, new_freq)  # update frequency of key

            self.log_event("hit", key, {"new_freq": new_freq})
            return value

    def put(self, key: int, value: int):
        if key in self.cache:  # key already exists in cache
            _, freq = self.cache[key]
            self.cache[key] = (value, freq)
            self.get(key)  # update frequency of key
            return

        if len(self.cache) >= self.capacity:  # if the cache is full
            evict_key, _ = self.freq[self.min_freq].popitem(last=False)  # remove the least frequently used item
            if not self.freq[self.min_freq]:  # if the frequency is empty
                del self.freq[self.min_freq]  # remove the frequency
            del self.cache[evict_key]  # remove the key from the cache
            self.log_event("evict", evict_key, {"evicted_freq": self.min_freq})  # log the eviction

        self.cache[key] = (value, 1)
        self.freq[1][key] = None
        self.min_freq = 1 if len(self.cache) == 0 else self.min_freq
        self.log_event("add", key, {"initial_freq": 1})

    def calculate_statistics(self):
        hit_ratio = self.hits / self.accesses if self.accesses > 0 else 0
        miss_ratio = self.misses / self.accesses if self.accesses > 0 else 0
        return {"hit_ratio": hit_ratio, "miss_ratio": miss_ratio}


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
        lfu_logger.info(json.dumps(log_entry))  # log metrics
