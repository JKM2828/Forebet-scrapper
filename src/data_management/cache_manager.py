"""
Moduł zarządzania cache'em danych.
"""
import json
import time
from pathlib import Path
from typing import Any, Optional
from datetime import datetime, timedelta

from ..config import Settings
from .logger import get_logger

logger = get_logger(__name__)


class CacheManager:
    """Zarządzanie cache'em danych w plikach JSON."""
    
    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Inicjalizacja cache managera.
        
        Args:
            cache_dir: Katalog dla plików cache (domyślnie Settings.CACHE_DIR)
        """
        self.cache_dir = cache_dir or Settings.CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_cache_file(self, key: str) -> Path:
        """Zwraca ścieżkę do pliku cache dla danego klucza."""
        # Sanitize key (usuń niebezpieczne znaki)
        safe_key = "".join(c if c.isalnum() or c in "-_" else "_" for c in key)
        return self.cache_dir / f"{safe_key}.json"
    
    def save(self, key: str, data: Any, ttl: Optional[int] = None) -> bool:
        """
        Zapisuje dane do cache.
        
        Args:
            key: Unikalny klucz cache
            data: Dane do zapisania (muszą być JSON-serializowalne)
            ttl: Time to live w sekundach (domyślnie Settings.CACHE_DURATION)
        
        Returns:
            True jeśli zapisano pomyślnie
        """
        try:
            cache_file = self._get_cache_file(key)
            ttl = ttl or Settings.CACHE_DURATION
            
            cache_data = {
                "key": key,
                "data": data,
                "timestamp": time.time(),
                "expires_at": time.time() + ttl,
                "ttl": ttl
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"Cache saved: {key} (TTL: {ttl}s)")
            return True
            
        except Exception as e:
            logger.error(f"Błąd zapisywania cache '{key}': {e}")
            return False
    
    def load(self, key: str) -> Optional[Any]:
        """
        Wczytuje dane z cache.
        
        Args:
            key: Klucz cache
        
        Returns:
            Dane z cache lub None jeśli nie istnieją/wygasły
        """
        try:
            cache_file = self._get_cache_file(key)
            
            if not cache_file.exists():
                logger.debug(f"Cache miss: {key} (plik nie istnieje)")
                return None
            
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Sprawdź czy cache wygasł
            if time.time() > cache_data.get("expires_at", 0):
                logger.debug(f"Cache expired: {key}")
                self.delete(key)
                return None
            
            logger.debug(f"Cache hit: {key}")
            return cache_data.get("data")
            
        except Exception as e:
            logger.error(f"Błąd wczytywania cache '{key}': {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """
        Usuwa cache dla danego klucza.
        
        Args:
            key: Klucz cache do usunięcia
        
        Returns:
            True jeśli usunięto pomyślnie
        """
        try:
            cache_file = self._get_cache_file(key)
            
            if cache_file.exists():
                cache_file.unlink()
                logger.debug(f"Cache deleted: {key}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Błąd usuwania cache '{key}': {e}")
            return False
    
    def clear_all(self) -> int:
        """
        Usuwa wszystkie pliki cache.
        
        Returns:
            Liczba usuniętych plików
        """
        try:
            count = 0
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
                count += 1
            
            logger.info(f"Cache cleared: {count} plików usuniętych")
            return count
            
        except Exception as e:
            logger.error(f"Błąd czyszczenia cache: {e}")
            return 0
    
    def cleanup_expired(self) -> int:
        """
        Usuwa wygasłe pliki cache.
        
        Returns:
            Liczba usuniętych plików
        """
        try:
            count = 0
            current_time = time.time()
            
            for cache_file in self.cache_dir.glob("*.json"):
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                    
                    if current_time > cache_data.get("expires_at", 0):
                        cache_file.unlink()
                        count += 1
                        
                except Exception:
                    # Jeśli nie można odczytać pliku, usuń go
                    cache_file.unlink()
                    count += 1
            
            if count > 0:
                logger.info(f"Expired cache cleaned: {count} plików usuniętych")
            
            return count
            
        except Exception as e:
            logger.error(f"Błąd czyszczenia wygasłego cache: {e}")
            return 0
    
    def get_cache_info(self) -> dict:
        """
        Zwraca informacje o cache.
        
        Returns:
            Słownik z informacjami o cache
        """
        total_files = 0
        expired_files = 0
        total_size = 0
        current_time = time.time()
        
        for cache_file in self.cache_dir.glob("*.json"):
            total_files += 1
            total_size += cache_file.stat().st_size
            
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                
                if current_time > cache_data.get("expires_at", 0):
                    expired_files += 1
                    
            except Exception:
                expired_files += 1
        
        return {
            "total_files": total_files,
            "expired_files": expired_files,
            "valid_files": total_files - expired_files,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "cache_dir": str(self.cache_dir)
        }


# Globalny singleton
cache_manager = CacheManager()
