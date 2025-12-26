#!/usr/bin/env python3
"""
Test de Speech-to-Text
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from terry.core.voice.stt import test_stt

if __name__ == "__main__":
    test_stt()
