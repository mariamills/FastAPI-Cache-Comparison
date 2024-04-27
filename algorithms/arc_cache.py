import json
from datetime import datetime
from collections import OrderedDict
from log import setup_log

arc_logger = setup_log("arc_cache")


class ARCCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.p = 0  # adaptive parameter, balances use between LRU-like (T1) and LFU-like (T2) caches
        self.T1 = OrderedDict()  # cache for recently accessed items (LRU behavior)
        self.T2 = OrderedDict()  # cache for frequently accessed items (LFU behavior)
        self.B1 = OrderedDict()  # tracks recently evicted items from T1
        self.B2 = OrderedDict()  # tracks recently evicted items from T2
        self.cache = {}  # combined view of all cache entries (T1, T2, B1, B2)
        self.accesses = 0
        self.hits = 0
        self.misses = 0

    def log_event(self, event_type, key, extra=None):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "key": key,
            "cache_size": len(self.T1) + len(self.T2),
            "capacity": self.capacity
        }
        if extra:  # if extra is not None, extra is a dictionary for any additional stuff we might want to log
            log_entry.update(extra)
        arc_logger.info(json.dumps(log_entry))  # log the event

    def get(self, key: int):
        self.accesses += 1  # increment the total number of accesses
        if key in self.T1:  # if key is in T1, (promote it to T2)
            value = self.T1.pop(key)  # remove from T1 (pop, removes from the dictionary)
            self.T2[key] = value  # promote to T2 due to repeated access
            self.cache[key] = (value, 'T2')  # update unified cache view
            self.hits += 1  # increment the number of hits
            self.log_event("hit", key, {"sub_cache": "T1 to T2"})  # log the event
            return value
        elif key in self.T2:  # if key is in T2, (move it to the end of T2)
            value = self.T2[key]  # get the value
            self.T2.move_to_end(key)  # reinforce its status by marking it as recently used within T2
            self.cache[key] = (value, 'T2')  # update cache view
            self.hits += 1
            self.log_event("hit", key, {"sub_cache": "T2"})
            return value
        else:
            self.misses += 1
            self.log_event("miss", key)  # log the event, cache miss (not found in T1 or T2)
            return "Not Found"

    def put(self, key: int, value: int):
        if key in self.T1 or key in self.T2:  # if key is already in cache (T1 or T2)
            self.get(key)  # update the key's position in the cache
            self.cache[key] = (value, 'T1' if key in self.T1 else 'T2')  # update unified cache view
            self.log_event("update", key)  # log the event
            return

        self.evict_if_needed()  # evict an entry if the cache is full

        self.T1[key] = value
        self.cache[key] = (value, 'T1')  # Add to unified cache view
        self.log_event("add", key, {"sub_cache": "T1"})

    def evict_if_needed(self):
        # Decide which entry to evict based on the full state of cache and ghost lists (B1, B2)
        if len(self.T1) + len(self.B1) >= self.capacity:  # if the cache is full (T1 + B1)
            if len(self.T1) < self.capacity:  # if T1 is not full, evict from B1
                evicted_key, _ = self.B1.popitem(last=False)  # evict the least recently used item from B1
                self.replace()  # replace the evicted item from B1 with an item from T2
                self.log_event("evict", evicted_key, {"sub_cache": "B1"})  # log the event (eviction from B1)
            else:  # if T1 is full, evict from T1
                evicted_key, _ = self.T1.popitem(last=False)  # evict the least recently used item from T1
                del self.cache[evicted_key]  # remove the evicted item from the unified cache view
                self.log_event("evict", evicted_key, {"sub_cache": "T1"})  # log the event (eviction from T1)

    # Replace the evicted item from T1 with an item from T2 or vice versa
    def replace(self):
        if len(self.T1) > 0 and (len(self.T1) > self.p or (len(self.B2) > 0 and len(self.T1) == self.p)):  # if T1 is larger than p (adaptive parameter) or B2 is not empty and T1 is equal to p
            evicted_key, evicted_value = self.T1.popitem(last=False)  # evict the least recently used item from T1
            self.B1[evicted_key] = evicted_value  # add the evicted item to B1
            del self.cache[evicted_key]  # remove the evicted item from the unified cache view
            self.log_event("replace", evicted_key, {"sub_cache": "T1 to B1"})
        else:  # if T2 is larger than p or B1 is not empty and T2 is equal to p
            evicted_key, evicted_value = self.T2.popitem(last=False)  # evict the least recently used item from T2
            self.B2[evicted_key] = evicted_value  # add the evicted item to B2
            del self.cache[evicted_key]  # remove the evicted item from the unified cache view
            self.log_event("replace", evicted_key, {"sub_cache": "T2 to B2"})

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
        arc_logger.info(json.dumps(log_entry))  # log metrics
