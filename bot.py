import discord
from discord.ext import commands
import asyncio
import datetime
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv

from config.settings import APPROVAL_DELAY_SECONDS, SHEET_NAME

# Load environment variables
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GOOGLE_CREDS_FILE = os.getenv("GOOGLE_CREDS_FILE")

# ---------------- GOOGLE SHEETS ----------------
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CREDS_FILE, scope)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).sheet1

# ---------------- DISCORD ----------------
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

# ---------------- COMMAND ----------------
@bot.tree.command(name="approve_request", description="Submit a request for automatic approval")
async def approve_request(interaction: discord.Interaction, request: str):

    requester = interaction.user.name
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    await interaction.response.send_message(
        f"📝 Request received:\n> {request}\n⏳ Pending approval...",
        ephemeral=False
    )

    # Log initial request
    row_index = len(sheet.get_all_values()) + 1
    sheet.append_row([timestamp, requester, request, "Pending", ""])

    # Delay
    await asyncio.sleep(APPROVAL_DELAY_SECONDS)

    approval_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Approval message
    await interaction.followup.send(
        f"✅ Approved on behalf of Owner per standing policy.\n> {request}"
    )

    # Update sheet
    sheet.update(f"D{row_index}:E{row_index}", [["Approved", approval_time]])

# ---------------- RUN ----------------
bot.run(DISCORD_TOKEN)
