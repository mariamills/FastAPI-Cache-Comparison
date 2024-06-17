import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import json
import requests
from pathlib import Path

# Path to logs folder
log_folder = Path('../logs')

# Read JSON logs into pandas DataFrame
def read_logs(log_pattern):
    all_logs = pd.DataFrame()
    for log_file in log_folder.glob(log_pattern):
        with open(log_file, 'r') as file:
            data = [json.loads(line) for line in file]
            df = pd.DataFrame(data)
            # Only convert 'latency' to numeric if it exists in the DataFrame
            if 'latency' in df.columns:
                df['latency'] = pd.to_numeric(df['latency'], errors='coerce')
            all_logs = pd.concat([all_logs, df], ignore_index=True)
    return all_logs

# get all the logs
lru_logs = read_logs('fastapi*/lru_cache.log')
lfu_logs = read_logs('fastapi*/lfu_cache.log')
arc_logs = read_logs('fastapi*/arc_cache.log')

# Example plot: Cache hit rates over time
def plot_latency(logs, title):
    if 'latency' in logs.columns:
        logs['timestamp'] = pd.to_datetime(logs['timestamp'])
        logs.set_index('timestamp', inplace=True)
        latency_series = logs['latency'].resample('s').mean()
        latency_series.plot(title=title)
        plt.ylabel('Latency (s)')
        plt.xlabel('Time')
        plt.show()

plot_latency(lru_logs, 'LRU Cache Latency')
plot_latency(lfu_logs, 'LFU Cache Latency')
plot_latency(arc_logs, 'ARC Cache Latency')


# Function to fetch stats from the /stats endpoint
def fetch_stats():
    response = requests.get('http://localhost/stats')  # http://127.0.0.1:8000/stats when running locally, http://localhost/stats when running in Docker
    stats = response.json()
    print("Cache Stats:", stats)
    return stats


# Fetch and print stats
stats = fetch_stats()


# graph all the stats
def plot_stats(stats):
    algorithms = ['LRU', 'LFU', 'ARC']
    hit_ratios = [stats[algo]['hit_ratio'] for algo in algorithms]
    miss_ratios = [stats[algo]['miss_ratio'] for algo in algorithms]

    fig, ax = plt.subplots(figsize=(8, 6))

    bar_width = 0.35
    opacity = 0.8

    index = np.arange(len(algorithms))
    ax.bar(index, hit_ratios, bar_width, alpha=opacity, color='b', label='Hit Ratio')
    ax.bar(index + bar_width, miss_ratios, bar_width, alpha=opacity, color='r', label='Miss Ratio')

    ax.set_xlabel('Caching Algorithm')
    ax.set_ylabel('Ratio')
    ax.set_title('Cache Performance Comparison')
    ax.set_xticks(index + bar_width / 2)
    ax.set_xticklabels(algorithms)
    ax.legend()

    plt.tight_layout()
    plt.show()


plot_stats(stats)
