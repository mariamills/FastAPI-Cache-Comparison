# Caching Strategies in Distributed Systems - A Comparative Study (LRU, LFU, ARC)

## Introduction

This project demonstrates the implementation of various caching algorithms using FastAPI, orchestrated with Docker and balanced using Nginx as a load balancer. It is designed to benchmark the performance of different caching strategies under simulated load conditions.


## Project Overview

The core of this project is to explore and compare three different caching mechanisms:

1. **Least Recently Used (LRU)**
   - The LRU algorithm is a cache eviction policy that removes the least recently used items first. It is based on the idea that items that have been accessed recently are more likely to be accessed again in the near future.
2. **Least Frequently Used (LFU)**
    - The LFU algorithm is a cache eviction policy that removes the least frequently used items first. It is based on the idea that items that have been accessed frequently in the past are more likely to be accessed frequently in the future.
3. **Adaptive Replacement Cache (ARC)**
    - The ARC algorithm is a hybrid cache eviction policy that combines the LRU and LFU algorithms. It dynamically adjusts the cache size based on the access patterns of the items in the cache. 

These algorithms are implemented in a [FastAPI](https://fastapi.tiangolo.com/) environment, with scalability tested via load balancing managed by [Nginx](https://www.nginx.com/). Load testing is conducted using [Locust](https://docs.locust.io/en/stable/what-is-locust.html) to simulate traffic and measure the performance impact of each caching strategy.


## Setup

### Prerequisites

- [Python](https://www.python.org/downloads/)
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Getting Started

1. Clone the repository:

```bash
git clone https://github.com/mariamills/FastAPI-Cache-Comparison.git
cd FastAPI-Cache-Comparison
```

2. Build and run the Docker containers:

```bash
docker-compose up --build
```

### How to Use

- Access the API: The API is accessible via http://localhost:80 after Docker Compose has started the services.
- **API Endpoints**:
    - `/{cache}/{key}`: Get the value of a key from the specified cache (lru, lfu, arc).
      - Example: `http://localhost:80/lru/1`

#### Load Testing

1. Open a new terminal window and navigate to the `load_tests` directory.
2. Run the Locust load testing tool:

```bash
cd load_tests
locust
```

3. Open a web browser and navigate to http://localhost:8089 to access the Locust dashboard.
4. Configure the number of users and spawn rate to simulate traffic on the API.
5. Run the load test and observe the performance of the caching strategies.

## Metrics Logged

- **Response Time**: The time taken to process a request from the API.
- **Cache Hit Rate**: The percentage of requests that were served from the cache.
- **Cache Miss Rate**: The percentage of requests that were not found in the cache and had to be fetched from the database.
- **Cache Size**: The number of items stored in the cache at any given time.
- **Cache Hit Count**: The number of requests that were served from the cache.
- **Cache Miss Count**: The number of requests that were not found in the cache and had to be fetched from the database.
- **Total Requests**: The total number of requests made to the API.
- **Total Requests Served**: The total number of requests that were successfully served by the API.
- **Total Requests Failed**: The total number of requests that failed to be served by the API.

## Tooling and Libraries

- **FastAPI**: For the web framework and API.
- **Nginx**: Used as a reverse proxy and load balancer.
- **Docker**: Containerization and orchestration.
- **Locust**: For load testing and performance measurement.
- **Python Libraries**: collections, json, logging for caching logic and event logging.

## Findings

TODO

## Conclusion

This project provides a comprehensive setup for testing and comparing caching algorithms in a simulated distributed system environment. By using FastAPI, Docker, Nginx, and Locust, we can evaluate the performance of different caching strategies under varying load conditions. The results of the load tests can help us understand the strengths and weaknesses of each caching algorithm.




