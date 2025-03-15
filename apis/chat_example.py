import asyncio
import websockets
import json
import sys


async def receive_messages(websocket, user_id):
    """Listens for messages and processes turns properly."""
    user_id = str(user_id)  # ✅ Garantee user_id is a string
    can_speak = False

    try:
        while True:
            response = await websocket.recv()
            response_data = json.loads(response)

            # ✅ Handle turn change messages
            if response_data.get("type") == "TURN_CHANGE":
                current_speaker = response_data.get("current_speaker")

                # ✅ Garantir que current_speaker é string
                if not isinstance(current_speaker, str):
                    current_speaker = str(current_speaker)

                # ✅ If it's an agent, wait for the server to respond
                if current_speaker.startswith("/agent"):
                    print(f"\n🤖 {current_speaker} is thinking...")
                    continue  # ✅ O servidor cuidará da resposta automaticamente

                # ✅ Check if it's the user's turn
                can_speak = current_speaker == user_id
                print(f"current speaker is {current_speaker} || user ID {user_id}  speaking now.")
                if can_speak:
                    print(f"\n🟢 It's your turn, {user_id}! Type a message.")
                    await send_message(websocket, user_id)
                else:
                    print("⏳ Waiting for your turn...")

            # ✅ Handle error messages
            elif response_data.get("type") == "ERROR":
                print(f"⚠️ {response_data.get('message')}")

            # ✅ Handle normal chat messages
            else:
                sender = response_data.get("user", "Unknown")
                message = response_data.get("message", "")
                timestamp = response_data.get("timestamp", "")
                print(f"\n[{timestamp}] {sender} → {message}")

    except websockets.exceptions.ConnectionClosedError:
        print("\n⚠️ Disconnected from server.")
    except Exception as e:
        print(f"⚠️ An error occurred: {e}")


async def send_message(websocket, user_id):
    """Handles user input when allowed."""
    message_text = await asyncio.to_thread(input, f"\n💬 {user_id} → ")

    if message_text.lower() == "exit":
        print("🚪 Exiting chat.")
        return

    await websocket.send(message_text)


async def websocket_client(room_id, user_id):
    """Manages the WebSocket connection and message handling."""
    uri = f"ws://localhost:8000/join/{room_id}/{user_id}"

    try:
        async with websockets.connect(uri) as websocket:
            print(f"✅ Connected to chat room {room_id} as {user_id}.")
            await receive_messages(websocket, user_id)

    except websockets.exceptions.ConnectionClosedError as e:
        print(f"⚠️ WebSocket connection closed with error: {e}")
    except Exception as e:
        print(f"⚠️ An unexpected error occurred: {e}")


if __name__ == "__main__":
    if len(sys.argv) == 3:
        room_id = sys.argv[1]
        user_id = sys.argv[2]
    else:
        room_id = input("Enter room ID: ")
        user_id = input("Enter your user ID: ")
        if user_id == "1":
            user_id = "f3d3825d-937c-46c2-a1b1-665417cdbc6e"
        if user_id == "2":
            user_id = "dcd6fec4-7e88-4f44-96b3-66b0351f83c2"

    asyncio.run(websocket_client(room_id, user_id))