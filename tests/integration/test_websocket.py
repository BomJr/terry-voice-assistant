#!/usr/bin/env python3
"""
Test WebSocket connection for Terry Web UI
"""
import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8080/ws"

    print(f"🔌 Connecting to {uri}...")

    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected!")

            # Send ping
            print("\n📤 Sending ping...")
            await websocket.send(json.dumps({"type": "ping"}))

            # Wait for pong
            response = await websocket.recv()
            data = json.loads(response)
            print(f"📥 Received: {data}")

            # Subscribe
            print("\n📤 Sending subscribe...")
            await websocket.send(json.dumps({"type": "subscribe"}))

            # Wait for subscription confirmation
            response = await websocket.recv()
            data = json.loads(response)
            print(f"📥 Received: {data}")

            print("\n✅ WebSocket test passed!")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
