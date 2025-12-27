# PDB Scrapper

PDB Scrapper is a blazingly fast feed scraper for Personality Database. It efficiently downloads images from user feeds at high speed—up to 1 gigabit per second—using techniques like DNS caching and thread pools.

# Features

- Ultra-fast scraping: Download hundreds of feeds concurrently using a thread pool.
- DNS caching: Pre-resolves API domains to prevent connection delays.
- Parallel downloads: Images from users and their associated IRLs are downloaded simultaneously.
- Resilient: Handles network errors gracefully with retries and timeouts.

# Requirements

- Python 3.10+
- requests
- tqdm
- python-dotenv

Install dependencies via pip:
```
pip install requests tqdm python-dotenv
```

# Setup

1. Clone the repository:

```
git clone https://github.com/yourusername/pdb-scrapper.git
cd pdb-scrapper
```

2. Create a .env file in the root folder with the following variables:

```
AUTH=<Your API Token>
XDEVICE=<Your Device ID>
```

# Usage

```
python scrapper.py
```

# Optimization Journey

After getting a working prototype of the script, I started optimizing it. Initially, I was using requests.get for every single request, which meant creating a new connection each time and redoing the DNS lookup. Switching to a requests.Session improved speed slightly because it reuses connections. However, that was still too slow—around 2 feeds per second.
To increase throughput, I implemented concurrency with thread pools, which dramatically boosted performance. This introduced a new problem: at high speeds (64 concurrent workers), DNS lookups started failing, causing most requests to error out. To solve this, I pre-cached the DNS of the API endpoints and forced requests to use the cached IPs.
With this technique, the scraper reached 50 feeds per second reliably, and in optimal network conditions it can download data at up to 1 gigabit per second.
