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
                    "task_id": int(task_id),  # Convert task_id to int
                    "message": message_text
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
{"1": {"role": "user", "content": "Hi"},
 "2": {"role": "assistant", "content": "{\n  \"reasoning\": \"Starting the conversation on a positive note to engage the user and establish a friendly interaction.\",\n  \"response\": \"Hello! How can I assist you today?\"\n}"}, "3": {"role": "user", "content": "You tell me"}, "4": {"role": "assistant", "content": "{\n  \"reasoning\": \"Considering the user's open-ended query, I will provide guidance on finding the most suitable option based on their preferences and budget.\",\n  \"response\": \"Based on your preferences for reliability, accuracy, and stylish design, Option B would be a great fit for you. It offers advanced features, syncs seamlessly with iOS devices, and falls within your budget.\"\n}"},
 "5": {"role": "user", "content": "what is option B"},
 "6": {"role": "assistant", "content": "{\n  \"reasoning\": \"The user explicitly asked for Option B, indicating a specific interest in this choice.\",\n  \"response\": \"Option B offers cutting-edge features like AI-driven fitness insights, personalized workout suggestions, heart rate, sleep, and step tracking with a 10-day battery life. It syncs seamlessly with iOS devices, has a sleek design, and is available at a discounted price of 130$ with a high rating.\"\n}"}}