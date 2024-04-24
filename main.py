from typing import Union
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any
from algorithms.lru_cache import LRUCache
from algorithms.lfu_cache import LFUCache
from algorithms.arc_cache import ARCCache
from timeit import default_timer as timer
from log import setup_log
import json
import sys


# Set up loggers when the app starts
app_logger = setup_log("app")

# Define the Item class to be used in the requests
class Item(BaseModel):
    value: Any

app = FastAPI()  # Initialize the FastAPI app

# Load data at startup
with open('data.json', 'r') as f:
    data = json.load(f)

# Initialize the caches and set their capacity (number of items they can store at a time)
lru_cache = LRUCache(capacity=100)
lfu_cache = LFUCache(capacity=100)
arc_cache = ARCCache(capacity=100)

@app.get("/")
def read_root():
    app_logger.info("Root endpoint accessed")
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

# Generic function to handle cache operations
def handle_cache_request(cache, item_id: str):
    result = cache.get(item_id)
    if result == "Not Found":
        if item_id in data:
            start = timer()  # Start the timer to measure the time taken to fetch the item

            app_logger.info(f"Item {item_id} not found in {cache.__class__.__name__} cache")
            # Fetch the item from the data (acting as a database)
            item = data[item_id]
            # Put the fetched item into the cache
            cache.put(item_id, item)
            # Return the newly cached item
            app_logger.info(f"Item {item_id} fetched from data and added to {cache.__class__.__name__} cache")

            end = timer()  # Stop the timer

            app_logger.info(f"{cache.__class__.__name__} cache took {end - start} seconds to fetch the item with id {item_id}")
            return item
        else:
            # Item not found in the data, raise HTTP 404 error
            raise HTTPException(status_code=404, detail="Item not found")
    return result


# LRU Cache Endpoints
@app.get("/lru/{item_id}")
def get_using_lru(item_id: str):
    return handle_cache_request(lru_cache, item_id)

@app.put("/lru/{item_id}")
def update_using_lru(item_id: str, item: Item):
    lru_cache.put(item_id, item.dict())
    return {"item_id": item_id, "item": item.dict()}

# LFU Cache Endpoints
@app.get("/lfu/{item_id}")
def get_using_lfu(item_id: str):
    return handle_cache_request(lfu_cache, item_id)

# ARC Cache Endpoints
@app.get("/arc/{item_id}")
def get_using_arc(item_id: str):
    return handle_cache_request(arc_cache, item_id)

# Optionally, keep the separate endpoint for fetching data directly if needed
@app.get("/data/{item_id}")
def get_data(item_id: str):
    if item_id in data:
        return data[item_id]
    else:
        raise HTTPException(status_code=404, detail="Item not found")


def receive_signal(signalNumber, frame):
    print('Received:', signalNumber)
    sys.exit()


@app.on_event("startup")
async def startup_event():
    import signal
    signal.signal(signal.SIGINT, receive_signal)
    # startup tasks


