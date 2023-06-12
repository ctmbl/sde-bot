from os import getenv
import logging

import discord
from discord.ext import commands
from helloasso_api import HaApiV5

from dotenv import load_dotenv
load_dotenv()

# Set up global variables
BOT_TOKEN = getenv('BOT_TOKEN')
COMMAND_PREFIX = getenv('COMMAND_PREFIX')
# HelloAsso API
HA_CLIENT_ID = getenv("HA_CLIENT_ID")
HA_CLIENT_SECRET = getenv("HA_CLIENT_SECRET")

ORG_SLUG = "association-de-l-etang"
SUBSCRIPTION_SLUG = "adhesion-2023"
SHOP_SLUG = "boutique-2023"

# Set up logging
discord.utils.setup_logging(root=True, level=logging.INFO)
LOGGER = logging.getLogger(__name__)

# Set up the discord bot and its event and loop
intents = discord.Intents.default()
# privilegied intents
intents.message_content = True
intents.members = False
intents.presences = False
# disabled intents
intents.typing = False

bot = commands.Bot(command_prefix = COMMAND_PREFIX, intents = intents)

# Set up the API object
api = HaApiV5(
        api_base='api.helloasso.com',
        client_id=HA_CLIENT_ID,
        client_secret=HA_CLIENT_SECRET,
        timeout=60
    )

def get_guest(item):
    response = api.call(f"/v5/organizations/{ORG_SLUG}/forms/Membership/{SUBSCRIPTION_SLUG}/items", method="GET", params={"tierName":item, "pageSize":"1"})
    LOGGER.info("%s",response.json())
    return response.json()["pagination"]["totalCount"]


@bot.command()
async def sde(ctx):
    wk = get_guest("2 JOURS : Vendredi 7 & Samedi 8 Juillet")
    vendredi = get_guest("VENDREDI SEUL - 7 Juillet")
    samedi = get_guest("SAMEDI SEUL - 8 Juillet")
    await ctx.message.channel.send(f"- Wk complet: {wk}\n- Vendredi: {vendredi}\n- Samedi: {samedi}\nNous serons donc **{wk + vendredi} le Vendredi et {wk + samedi} le Samedi**.")

if __name__ == "__main__":
    try:
        # log_handler=None will prevent set up of the 'discord' logger all logs will be handled
        # by the root looger which has been set up
        LOGGER.info("Bot Token: %s", BOT_TOKEN)
        bot.run(BOT_TOKEN, log_handler=None)
    except discord.errors.LoginFailure:
        print("Invalid discord token")
        exit(1)

