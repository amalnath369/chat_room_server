import asyncio
import websockets
import json
import sys
import time


async def chat_client(username: str, topic: str, server_url: str = "ws://localhost:8000/ws"):
    """Simple chat client example"""
    
    async with websockets.connect(server_url) as websocket:
        # Send initial connection data
        await websocket.send(json.dumps({
            "username": username,
            "topic": topic
        }))
        
        print(f"Connected as {username} to topic {topic}")
        
        # Start receiving messages
        async def receive_messages():
            while True:
                try:
                    message = await websocket.recv()
                    data = json.loads(message)
                    
                    if data.get("type") == "topic_list":
                        print("\nActive Topics:")
                        for topic_info in data.get("topics", []):
                            print(f"  - {topic_info}")
                    elif data.get("type") == "acknowledgment":
                        print(f"Message delivered at {data.get('timestamp')}")
                    else:
                        print(f"\n{data.get('username')}: {data.get('message')}")
                except websockets.exceptions.ConnectionClosed:
                    print("\nConnection closed")
                    break
        
        # Start sending messages
        async def send_messages():
            while True:
                try:
                    message = await asyncio.get_event_loop().run_in_executor(
                        None, input, "You: "
                    )
                    
                    if message.lower() == '/quit':
                        break
                    
                    if message.strip() == '/list':
                        await websocket.send('/list')
                    else:
                        await websocket.send(message)
                        
                except (EOFError, KeyboardInterrupt):
                    break
        
        # Run both tasks concurrently
        receive_task = asyncio.create_task(receive_messages())
        send_task = asyncio.create_task(send_messages())
        
        await asyncio.gather(receive_task, send_task)


async def test_scenario():
    """Test multiple clients interacting"""
    print("Testing chat server functionality...")
    
    # Test 1: Two users in same topic
    print("\n=== Test 1: Two users in sports topic ===")
    
    async def user1():
        print("\nUser1 (alice) joining sports topic...")
        await asyncio.sleep(1)
        await chat_client("alice", "sports", "ws://localhost:8000/ws")
    
    async def user2():
        print("\nUser2 (bob) joining sports topic...")
        await asyncio.sleep(2)
        await chat_client("bob", "sports", "ws://localhost:8000/ws")
    
    # Run tests
    await asyncio.gather(user1(), user2(), return_exceptions=True)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="WebSocket Chat Client")
    parser.add_argument("--username", default="user", help="Username")
    parser.add_argument("--topic", default="general", help="Topic/room")
    parser.add_argument("--server", default="ws://localhost:8000/ws", help="Server URL")
    parser.add_argument("--test", action="store_true", help="Run test scenario")
    
    args = parser.parse_args()
    
    if args.test:
        asyncio.run(test_scenario())
    else:
        try:
            asyncio.run(chat_client(args.username, args.topic, args.server))
        except KeyboardInterrupt:
            print("\nDisconnected")
        except Exception as e:
            print(f"Error: {e}")