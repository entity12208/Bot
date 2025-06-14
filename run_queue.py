import time
import json
from mcrcon import MCRcon

with open("config.json", "r") as f:
    config = json.load(f)

RCON_HOST = config.get("rcon_host", "127.0.0.1")
RCON_PORT = config.get("rcon_port", 25575)
RCON_PASSWORD = config.get("rcon_password")

QUEUE_FILE = "command_queue.txt"

def read_queue():
    with open(QUEUE_FILE, "r") as f:
        return [line.strip() for line in f if line.strip()]

def write_queue(queue):
    with open(QUEUE_FILE, "w") as f:
        f.write("\n".join(queue))

def run_rcon_command(command: str) -> str:
    try:
        with MCRcon(RCON_HOST, RCON_PASSWORD, port=RCON_PORT) as mcr:
            response = mcr.command(command)
            return response
    except Exception as e:
        return f"RCON error: {e}"

def process_queue():
    queue = read_queue()
    if not queue:
        print("Queue empty, waiting...")
        return

    current_player = queue[0]
    print(f"Processing player: {current_player}")

    # Example: run a command or notify player on server
    response = run_rcon_command(f"tell {current_player} You are now joining the server!")
    print(f"Server response: {response}")

    # Remove player from queue after processing
    queue.pop(0)
    write_queue(queue)

if __name__ == "__main__":
    while True:
        process_queue()
        time.sleep(30)  # Check queue every 30 seconds
