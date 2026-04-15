import json
import hashlib
import os
from typing import Any, Optional
from datetime import datetime, timedelta
from app.config import settings

class CacheService:
    def __init__(self, cache_dir: str = None, ttl_hours: int = None):
        self.cache_dir = cache_dir or settings.cache_dir
        self.ttl = timedelta(hours=ttl_hours or settings.cache_ttl_hours)
        os.makedirs(self.cache_dir, exist_ok=True)

    def _get_cache_key(self, key: str) -> str:
        """Generate cache key from input"""
        return hashlib.md5(key.encode()).hexdigest()

    def _get_cache_path(self, cache_key: str) -> str:
        """Get full path for cache file"""
        return os.path.join(self.cache_dir, f"{cache_key}.json")

    def get(self, key: str) -> Optional[Any]:
        """Get cached value if not expired"""
        cache_key = self._get_cache_key(key)
        cache_path = self._get_cache_path(cache_key)

        if not os.path.exists(cache_path):
            return None

        try:
            with open(cache_path, 'r') as f:
                data = json.load(f)

            cached_time = datetime.fromisoformat(data['timestamp'])
            if datetime.now() - cached_time > self.ttl:
                os.remove(cache_path)  # Remove expired cache
                return None

            return data['value']
        except (json.JSONDecodeError, KeyError, ValueError):
            return None

    def set(self, key: str, value: Any) -> None:
        """Cache a value with timestamp"""
        cache_key = self._get_cache_key(key)
        cache_path = self._get_cache_path(cache_key)

        data = {
            'timestamp': datetime.now().isoformat(),
            'value': value
        }

        with open(cache_path, 'w') as f:
            json.dump(data, f)

    def clear(self) -> None:
        """Clear all cache files"""
        for file in os.listdir(self.cache_dir):
            if file.endswith('.json'):
                os.remove(os.path.join(self.cache_dir, file))