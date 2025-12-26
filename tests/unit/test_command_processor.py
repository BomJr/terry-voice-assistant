#!/usr/bin/env python3
"""Test CommandProcessor directly"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from terry.core.llm.processor import CommandProcessor
from terry.core.llm.ollama_client import OllamaClient
import json

async def test():
    llm = OllamaClient()
    processor = CommandProcessor(llm)

    commands = [
        "pon música",
        "sube volumen",
        "pausa",
        "qué hora es"
    ]

    for cmd in commands:
        print(f"\n{'='*60}")
        print(f"Testing: {cmd}")
        print('='*60)
        result = await processor.process_command(cmd, language="es")
        print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(test())
