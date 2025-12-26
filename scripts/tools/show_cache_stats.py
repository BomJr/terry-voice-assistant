#!/usr/bin/env python3
"""
Muestra estadísticas del caché persistente
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from terry.core.utils.persistent_cache import get_persistent_cache

if __name__ == "__main__":
    cache = get_persistent_cache()
    cache.print_stats()
