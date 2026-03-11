import json
import redis

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def get_cached(key):
    data = r.get(key)
    if data:
        return json.loads(data)
    return None

def set_cached(key, value, ttl=300):
    try:
        r.setex(key, ttl, json.dumps(value))
        print(f"✅ Cached: {key}")
    except Exception as e:
        print(f"❌ Cache failed: {e}")

def delete_cached(*keys):
    for key in keys:
        r.delete(key)