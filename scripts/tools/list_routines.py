#!/usr/bin/env python3
"""
Muestra todas las rutinas disponibles
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from terry.core.actions.routines.routine_manager import get_routine_manager

if __name__ == "__main__":
    manager = get_routine_manager()
    manager.print_routines()
