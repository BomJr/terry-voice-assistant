#!/usr/bin/env python3
"""
Muestra estadísticas y comandos recientes del log de auditoría
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from terry.core.utils.audit_logger import get_audit_logger

if __name__ == "__main__":
    audit = get_audit_logger()

    # Mostrar estadísticas
    audit.print_stats()

    print()

    # Mostrar comandos recientes
    audit.print_recent(limit=10)
