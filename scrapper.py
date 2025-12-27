import socket
import requests
import os
import json
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

load_dotenv()

os.makedirs("pics", exist_ok=True)
os.makedirs("irls", exist_ok=True)

# We need to pre-cache the domains of the api, because we are downloading too fast and could fail.
def precache_dns(hostnames):
    pinned_map = {}
    for host in hostnames:
        try:
            ip = socket.gethostbyname(host)
            pinned_map[host] = ip
        except Exception as e:
            print(f"Could not resolve {host}: {e}")

    original_getaddrinfo = socket.getaddrinfo

    def cached_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
        if host in pinned_map:
            # Use the cached ip.
            return original_getaddrinfo(pinned_map[host], port, family, type, proto, flags)
        return original_getaddrinfo(host, port, family, type, proto, flags)

    socket.getaddrinfo = cached_getaddrinfo

precache_dns([
    "api.personality-database.com", 
    "static1.personalitydatabase.net"
])

session = requests.Session()
session.headers.update({
    "User-Agent": "PBD-Android 2.108.0(2204)",
    "X-Lang": "en",
    "X-Locale": "en",
    "X-Region": "US",
    "Authorization": os.environ["AUTH"],
    "X-Device": os.environ["XDEVICE"],
})

def get_feeds():
    url = "https://api.personality-database.com/api/v2/irl/feeds?attractiveUser=false"
    
    try:
        res = session.get(url, timeout=10)
        res.raise_for_status()
        return res.json().get("data", {}).get("results", [])
    except Exception as e:
        print(f"Error fetching feeds: {e}")
    
    return []
    

def download_file(url, filename):
    if not url:
        return
    
    try:
        # Stream to a file
        with session.get(url, stream=True, timeout=15) as r:
            r.raise_for_status()
            with open(filename, "wb") as f:
                for chunk in r.iter_content(chunk_size=32768):
                    f.write(chunk)
    except Exception as e:
        print(f"Error downloading \"{url}\": {e}")

def download_feed(feed):
    user = feed.get("user", {})
    user_id = user.get("id")

    irls = feed.get("irls")

    picURL = user.get("image").get("picURL")

    download_file(picURL, f"pics/{user_id}.jpeg")

    for irl in irls:
        irl_id = irl.get("id")
        irl_type = irl.get("type")

        if irl_type == "image":
            irl_picURL = irl.get("origin").get("picURL")

            download_file(irl_picURL, f"irls/{user_id}_{irl_id}.jpeg")

feeds = []

feeds_to_fetch = 1000

# Fetch multiple feeds
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(get_feeds) for _ in range(feeds_to_fetch)]
    for f in tqdm(as_completed(futures), total=feeds_to_fetch, desc="Fetching Feeds"):
        feeds.extend(f.result())

print(f"Downloading {len(feeds)} feeds")

# Download all feeds images
with ThreadPoolExecutor(max_workers=64) as executor:
    list(tqdm(executor.map(download_feed, feeds), total=len(feeds)))