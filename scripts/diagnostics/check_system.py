#!/usr/bin/env python3
"""
Script rápido para verificar el sistema antes de usar Home-Alexa
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from terry.core.utils.permissions_checker import PermissionsChecker

if __name__ == "__main__":
    checker = PermissionsChecker()
    checks = checker.check_all(verbose=True)

    print()
    if checker.are_critical_requirements_met():
        print("✅ SISTEMA LISTO PARA USAR")
        print()
        sys.exit(0)
    else:
        print("❌ FALTAN REQUISITOS CRÍTICOS")
        print()
        print(checker.get_installation_instructions())
        print()
        sys.exit(1)
