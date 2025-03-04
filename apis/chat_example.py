import asyncio
import websockets
import json

async def receive_messages(websocket):
    """Continuously receives messages from the server and prints them in real-time."""
    try:
        while True:
            response = await websocket.recv()
            response_data = json.loads(response)

            sender = response_data.get("user", "Unknown")
            received_message = response_data.get("message", "")

            print(f"\n{sender} -> {received_message}\n> ", end="", flush=True)

    except websockets.exceptions.ConnectionClosedError:
        print("\nDisconnected from server.")

async def websocket_client():
    """Handles user connection and message sending."""
    room_id = input("Enter room_id: ")  # Specific chat room
    user_name = input("Enter your name: ")  # User's name
    uri = f"ws://localhost:8000/join/{room_id}/{user_name}"  # Correct WebSocket URL

    try:
        async with websockets.connect(uri) as websocket:
            print(f"Connected to WebSocket server in room {room_id} as {user_name}.")

            # Create a task to listen for incoming messages
            receive_task = asyncio.create_task(receive_messages(websocket))

            while True:
                message_text = await asyncio.to_thread(input, f"{user_name} -> ")
                if message_text.lower() == "exit":
                    print("Exiting WebSocket client.")
                    receive_task.cancel()
                    break

                await websocket.send(message_text)  # Send only the message text

            receive_task.cancel()  # Cancel message listening when exiting

    except websockets.exceptions.ConnectionClosedError as e:
        print(f"WebSocket connection closed with error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(websocket_client())