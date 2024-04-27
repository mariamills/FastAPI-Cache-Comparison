import os
from locust import HttpUser, task, between

class CacheTestingUser(HttpUser):
    wait_time = between(1, 2)
    endpoint = os.getenv('ENDPOINT', '/lru')  # default to LRU

    @task
    def access_cache(self):
        for item_id in range(1, 11):  # 1 to 10 (inclusive) items to access
            self.client.get(f"{self.endpoint}/{item_id}", name=f"{self.endpoint}/[item_id]")

# env variable to set the cache algorithm
# ENDPOINT='/lru'
# ENDPOINT='/lfu'
# ENDPOINT='/arc'
