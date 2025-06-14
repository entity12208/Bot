import os
import json
import discord
from discord.ext import commands
from dotenv import load_dotenv
from mcrcon import MCRcon
import asyncio
from keep_alive import keep_alive
keep_alive()


load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not DISCORD_BOT_TOKEN:
    raise ValueError("Missing DISCORD_BOT_TOKEN in .env")

with open("config.json", "r") as f:
    config = json.load(f)

RCON_HOST = config.get("rcon_host", "127.0.0.1")
RCON_PORT = config.get("rcon_port", 25575)
RCON_PASSWORD = config.get("rcon_password")

if not RCON_PASSWORD:
    raise ValueError("Missing RCON password in config.json")

QUEUE_FILE = "command_queue.txt"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

def run_rcon_command(command: str) -> str:
    try:
        with MCRcon(RCON_HOST, RCON_PASSWORD, port=RCON_PORT) as mcr:
            response = mcr.command(command)
            return response
    except Exception as e:
        return f"RCON error: {e}"

def read_queue():
    if not os.path.exists(QUEUE_FILE):
        return []
    with open(QUEUE_FILE, "r") as f:
        return [line.strip() for line in f if line.strip()]

def write_queue(queue):
    with open(QUEUE_FILE, "w") as f:
        f.write("\n".join(queue))

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")

@bot.command()
async def status(ctx):
    """Check if server is online."""
    response = await asyncio.to_thread(run_rcon_command, "list")
    await ctx.send(f"Server response:\n```\n{response}\n```")

@bot.command()
@commands.has_permissions(administrator=True)
async def say(ctx, *, message: str):
    response = await asyncio.to_thread(run_rcon_command, f"say [Discord] {message}")
    await ctx.send(f"Sent message. Server response:\n```\n{response}\n```")

@bot.command()
@commands.has_permissions(administrator=True)
async def kick(ctx, player: str, *, reason: str = "No reason provided"):
    response = await asyncio.to_thread(run_rcon_command, f"kick {player} {reason}")
    await ctx.send(f"Kick sent. Server response:\n```\n{response}\n```")

@bot.command()
async def queue(ctx):
    """Join the player queue."""
    queue = read_queue()
    user = str(ctx.author)
    if user in queue:
        await ctx.send("You are already in the queue!")
    else:
        queue.append(user)
        write_queue(queue)
        await ctx.send(f"{user} added to the queue! Position: {len(queue)}")

@bot.command()
@commands.has_permissions(administrator=True)
async def dequeue(ctx):
    """Remove the first player from the queue (admin only)."""
    queue = read_queue()
    if not queue:
        await ctx.send("Queue is empty!")
        return
    player = queue.pop(0)
    write_queue(queue)
    await ctx.send(f"Removed {player} from the queue.")

bot.run(DISCORD_BOT_TOKEN)
