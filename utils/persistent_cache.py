"""
Home-Alexa - Caché Persistente
Almacena respuestas LLM en disco para acelerar comandos frecuentes
"""

import json
import hashlib
import time
from pathlib import Path
from typing import Optional, Dict, Any
from collections import defaultdict
from utils.logger import get_logger

logger = get_logger(__name__)


class PersistentCache:
    """Caché de respuestas LLM en disco."""

    def __init__(self, cache_dir: str = "cache"):
        """
        Inicializa el caché persistente.

        Args:
            cache_dir: Directorio donde guardar el caché
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

        self.cache_file = self.cache_dir / "llm_responses.json"
        self.stats_file = self.cache_dir / "cache_stats.json"

        # Cargar caché existente
        self.cache: Dict[str, Dict[str, Any]] = self._load_cache()
        self.stats = self._load_stats()

    def _load_cache(self) -> Dict[str, Dict[str, Any]]:
        """Carga el caché desde disco."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error cargando caché: {e}")
        return {}

    def _save_cache(self):
        """Guarda el caché a disco."""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error guardando caché: {e}")

    def _load_stats(self) -> Dict[str, Any]:
        """Carga estadísticas del caché."""
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error cargando stats: {e}")
        return {
            "hits": 0,
            "misses": 0,
            "total_queries": 0,
            "command_counts": defaultdict(int)
        }

    def _save_stats(self):
        """Guarda estadísticas a disco."""
        try:
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error guardando stats: {e}")

    def _get_cache_key(self, user_input: str) -> str:
        """
        Genera una clave única para el comando.

        Args:
            user_input: Texto del usuario

        Returns:
            Hash MD5 del texto normalizado
        """
        # Normalizar: lowercase, sin espacios extras
        normalized = " ".join(user_input.lower().strip().split())
        return hashlib.md5(normalized.encode('utf-8')).hexdigest()

    def get(self, user_input: str) -> Optional[Dict[str, Any]]:
        """
        Busca una respuesta en el caché.

        Args:
            user_input: Texto del usuario

        Returns:
            Respuesta cacheada o None
        """
        key = self._get_cache_key(user_input)
        self.stats["total_queries"] += 1

        if key in self.cache:
            # Verificar que no esté expirada (24 horas)
            entry = self.cache[key]
            age = time.time() - entry.get("timestamp", 0)

            if age < 86400:  # 24 horas
                self.stats["hits"] += 1
                entry["hit_count"] = entry.get("hit_count", 0) + 1
                logger.debug(f"Cache HIT: {user_input[:50]}")
                return entry["response"]
            else:
                # Expirado, eliminar
                del self.cache[key]
                self._save_cache()

        self.stats["misses"] += 1
        logger.debug(f"Cache MISS: {user_input[:50]}")
        return None

    def set(self, user_input: str, response: Dict[str, Any]):
        """
        Guarda una respuesta en el caché.

        Args:
            user_input: Texto del usuario
            response: Respuesta del LLM
        """
        key = self._get_cache_key(user_input)

        # Guardar entrada
        self.cache[key] = {
            "query": user_input,
            "response": response,
            "timestamp": time.time(),
            "hit_count": 0
        }

        # Actualizar estadísticas
        intent = response.get("intent", "unknown")
        if "command_counts" not in self.stats:
            self.stats["command_counts"] = {}
        self.stats["command_counts"][intent] = self.stats["command_counts"].get(intent, 0) + 1

        # Guardar a disco (solo si hay suficientes cambios)
        cache_size = len(self.cache)
        if cache_size % 10 == 0:  # Guardar cada 10 entradas
            self._save_cache()
            self._save_stats()

    def get_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del caché.

        Returns:
            Diccionario con estadísticas
        """
        total = self.stats["total_queries"]
        hits = self.stats["hits"]
        hit_rate = (hits / total * 100) if total > 0 else 0

        return {
            "total_queries": total,
            "cache_hits": hits,
            "cache_misses": self.stats["misses"],
            "hit_rate": f"{hit_rate:.1f}%",
            "cache_size": len(self.cache),
            "most_common": self._get_most_common()
        }

    def _get_most_common(self, limit: int = 5) -> list:
        """Obtiene los comandos más frecuentes."""
        if "command_counts" not in self.stats:
            return []

        sorted_commands = sorted(
            self.stats["command_counts"].items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_commands[:limit]

    def clear_expired(self):
        """Elimina entradas expiradas del caché."""
        current_time = time.time()
        expired_keys = []

        for key, entry in self.cache.items():
            age = current_time - entry.get("timestamp", 0)
            if age >= 86400:  # 24 horas
                expired_keys.append(key)

        for key in expired_keys:
            del self.cache[key]

        if expired_keys:
            logger.info(f"Eliminadas {len(expired_keys)} entradas expiradas")
            self._save_cache()

    def optimize(self):
        """
        Optimiza el caché:
        - Elimina entradas expiradas
        - Mantiene solo las más usadas si el caché es muy grande
        """
        self.clear_expired()

        # Si el caché es muy grande (>1000 entradas), mantener solo las más usadas
        if len(self.cache) > 1000:
            # Ordenar por hit_count
            sorted_entries = sorted(
                self.cache.items(),
                key=lambda x: x[1].get("hit_count", 0),
                reverse=True
            )

            # Mantener top 500
            self.cache = dict(sorted_entries[:500])
            logger.info(f"Caché optimizado: reducido a {len(self.cache)} entradas")
            self._save_cache()

    def print_stats(self):
        """Imprime estadísticas del caché."""
        stats = self.get_stats()

        print("\n📊 ESTADÍSTICAS DEL CACHÉ")
        print("=" * 50)
        print(f"  Total consultas: {stats['total_queries']}")
        print(f"  Cache hits: {stats['cache_hits']}")
        print(f"  Cache misses: {stats['cache_misses']}")
        print(f"  Tasa de aciertos: {stats['hit_rate']}")
        print(f"  Tamaño del caché: {stats['cache_size']} entradas")

        if stats['most_common']:
            print("\n  Comandos más frecuentes:")
            for intent, count in stats['most_common']:
                print(f"    • {intent}: {count} veces")
        print("=" * 50)

    def __del__(self):
        """Guardar caché al destruir el objeto."""
        try:
            # v6.0 - Verificar que builtins existan (fix para shutdown)
            if hasattr(__builtins__, 'open') or 'open' in dir(__builtins__):
                self._save_cache()
                self._save_stats()
        except:
            # Ignorar errores en destructor (Python shutdown)
            pass


# Instancia global
_cache_instance = None


def get_persistent_cache() -> PersistentCache:
    """Obtiene la instancia global del caché persistente."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = PersistentCache()
    return _cache_instance
