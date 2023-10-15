import asyncio
import websockets


class Message():
    def __init__(self, client_id, message):
        self.client_id = client_id
        self.message = message

    def __str__(self):
        return f"({self.client_id}, {self.message}"


banned_clients = set()  # Seznam zakázaných uživatelů
connected = {}
next_client_id = 1
messages = []


async def handle_client(websocket, path):
    global next_client_id
    client_id = next_client_id
    next_client_id += 1

    if websocket.remote_address[0] in banned_clients:
        await websocket.send("You are banned from the server.")
        await websocket.close()
        return

    connected[client_id] = websocket

    try:
        async for message in websocket:
            print(f"Client {client_id} sent: {message}")
            messages.append(Message(client_id, message))

            for id, client in connected.items():
                if id != client_id:
                    await client.send(f"Client {client_id}: {message}")

    except websockets.exceptions.ConnectionClosedError:
        pass

    finally:
        del connected[client_id]
        print(f"Client {client_id} disconnected")


start_server = websockets.serve(handle_client, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
