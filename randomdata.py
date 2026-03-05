import asyncio
import websockets
import json
import random
from datetime import datetime

async def send_test_data():
    # Replace '8765' with the port your other script is listening on
    uri = "ws://localhost:8765"
    
    print(f"Attempting to connect to {uri}...")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected! Sending data...")
            
            while True:
                # Prepare the data payload
                data = {
                    "timestamp": datetime.now().isoformat(),
                    "random_value": random.randint(1, 100),
                    "status": "testing"
                }
                
                # Convert to JSON string and send
                await websocket.send(json.dumps(data))
                print(f"Sent: {data}")
                
                # Wait 1 second before sending the next packet
                await asyncio.sleep(1)
                
    except ConnectionRefusedError:
        print("Error: Could not connect. Is your server script running?")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(send_test_data())