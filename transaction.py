import discord
from discord.ext import commands
from discord import app_commands, Attachment, Interaction
import os
from dotenv import load_dotenv 
import logging

from models import status_icons, Transaction


load_dotenv()   

MANAGER_CHANNEL_ID = int(os.getenv('MANAGER_CHANNEL_ID'))
GUILD_ID = int(os.getenv('GUILD_ID'))
MANAGER_ROLE_NAME = os.getenv('MANAGER_ROLE_NAME')  # Add this line

if MANAGER_CHANNEL_ID is None or GUILD_ID is None:
    raise ValueError("Error: Required environment variables not found. Please check the .env file.")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('discord')

intents = discord.Intents.default()
intents.members = True  # To access member information 

bot = commands.Bot(command_prefix = "!", intents=intents)

@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
    logger.info(f'Synced {len(synced)} commands.')

# Creating a new command named /txn
@bot.tree.command(
    name="txn",
    description="Request for a transaction to be recorded in the system.",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.describe(
    amount="Enter the amount for the Transaction in TK.",
    tx_type="Select the type of Transaction.",
    description="Please mention the payment method, sender info and transaction ID.",
    proof="Upload proof of payment (Receipt, Statement, or Screenshot)."
) 

@app_commands.choices(
    tx_type=[
        app_commands.Choice(name="IN", value="credit"),
        app_commands.Choice(name="OUT", value="debit"),
    ]
)
async def request_transaction(
    interaction: Interaction,
    amount: float,  # Added parameter
    tx_type: str,   # Added parameter
    description: str,  # Added parameter
    proof: Attachment = None  # Added parameter
):
    if interaction.channel_id != MANAGER_CHANNEL_ID:
        await interaction.response.send_message("This command can only be used in the #manager channel.", ephemeral=True)
        return
 
    # Log the transaction details
    logger.info(f'Command invoked by {interaction.user}: Amount={amount}, Type={tx_type}, Description={description}')

    # Create a new transaction object
    txn = Transaction(amount=amount, type=tx_type, description=description, proof=proof)
    await post_txn_record(interaction, txn)


async def post_txn_record(interaction: Interaction, txn: Transaction):
    status_message = status_icons.get(txn.status.lower())
    
    # Create an embed message
    message = discord.Embed(
        title="📄 Transaction Details",
        color=discord.Color.blue()
    )
    
    # Add fields to the embed    
    message.add_field(name="Status:", value = status_message, inline=True)
    message.add_field(name="Amount:", value = txn.amount, inline=True)
    message.add_field(name="Type:", value= txn.type, inline=True)
    message.add_field(name="Description:", value= txn.description, inline=True)

    if txn.proof:
        message.add_field(name="Proof:", value=txn.proof, inline=True)

    # Send the message to the channel
    await interaction.send(message)
 

# To be updated 
async def update_txn_status(ctx, status: str = "pending"):
    status_message = status_icons.get(status.lower())

bot.run(os.getenv('TOKEN'))