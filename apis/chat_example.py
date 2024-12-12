import asyncio
import websockets
import json

# Run this script to test the WebSocket server
async def websocket():
    uri = "ws://localhost:8000/chat"

    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to WebSocket server.")

            user_id = input("Enter user_id: ")
            task_id = input("Enter task_id: ")

            while True:
                message_text = input("USER -> ")
                if message_text.lower() == "exit":
                    print("Exiting WebSocket client.")
                    break

                message = {
                    "user_id": user_id,
                    "task_id": task_id,
                    "message": message_text,
                    "map":["B","C","D","A"]
                }

                print(f"COMMUNICATION || Sending: {message}")
                await websocket.send(json.dumps(message))

                response = await websocket.recv()
                print(f"COMMUNICATION || Received: {response}")
                print("Assistant ->", json.loads(response)["response"])

    except websockets.exceptions.ConnectionClosedError as e:
        print(f"WebSocket connection closed with error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    asyncio.run(websocket())
