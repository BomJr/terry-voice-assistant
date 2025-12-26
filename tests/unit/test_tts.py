#!/usr/bin/env python3
"""
Test de Text-to-Speech
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from terry.core.voice.tts import test_tts

if __name__ == "__main__":
    test_tts()
