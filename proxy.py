from fastapi import FastAPI, HTTPException
import requests
from consistent_hashing import ConsistentHashRing

app = FastAPI()

# Operational targets: Can be scaled to 3 or more
NODES = ["http://kv-1:8080", "http://kv-2:8080", "http://kv-3:8080"]
ring = ConsistentHashRing(NODES)

@app.get("/{key}")
def get_key(key: str):
    target_node = ring.get_node(key)
    try:
        # Forwards request to the existing GET /{key} endpoint 
        response = requests.get(f"{target_node}/{key}", timeout=1)
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Key not found")
        return response.json()
    except requests.exceptions.RequestException:
        raise HTTPException(status_code=503, detail="Backend node unreachable")

@app.post("/{key}")
def put_key(key: str, item: dict):
    target_node = ring.get_node(key)
    try:
        # Forwards request to the existing POST /{key} endpoint 
        response = requests.post(f"{target_node}/{key}", json=item, timeout=1)
        return response.json()
    except requests.exceptions.RequestException:
        raise HTTPException(status_code=503, detail="Backend node unreachable")

@app.delete("/{key}")
def delete_key(key: str):
    target_node = ring.get_node(key)
    try:
        # Forwards request to the existing DELETE /{key} endpoint 
        return requests.delete(f"{target_node}/{key}").json()
    except requests.exceptions.RequestException:
        raise HTTPException(status_code=503, detail="Backend node unreachable")