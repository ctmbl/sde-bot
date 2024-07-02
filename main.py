from os import getenv
import logging

import discord
from discord.ext import commands
from helloasso_api import HaApiV5

# Monkey patching issue in HaApiV5
from patch_HaApiV5 import call as fixed_call
HaApiV5.call = fixed_call

from dotenv import load_dotenv
load_dotenv()

# Set up global variables
BOT_TOKEN = getenv('BOT_TOKEN')
COMMAND_PREFIX = getenv('COMMAND_PREFIX')
# HelloAsso API
HA_CLIENT_ID = getenv("HA_CLIENT_ID")
HA_CLIENT_SECRET = getenv("HA_CLIENT_SECRET")

ORG_SLUG = "association-de-l-etang"
SUBSCRIPTION_SLUG = "adhesion-2024"
#SHOP_SLUG = "boutique-2023" # unused in 2024

# Set up logging
discord.utils.setup_logging(root=True, level=logging.INFO)
LOGGER = logging.getLogger(__name__)
#LOGGER.setLevel(logging.DEBUG)

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


@bot.command(help="donne les stats du nombre d'adhésions")
async def sde(ctx):
    samedi = get_guest("Samedi 27 Juillet")
    zorgas = "TODO" # TODO
    artistes = "TODO" # TODO
    total_money = "TODO" # TODO
    total_donation = "TODO" # TODO
    await ctx.send(f"\nSamedi: {samedi}\n- dont code ZORGA24: {zorgas}\n- dont code ARTISTES24: {artistes}\n\nArgent collecté: {total_money}\n- dont Dons: {total_donation}")

@bot.command(name="place", help="affiche les places prises correspondant à un certain nom/prenom/mail donné")
async def search_user(ctx, name):
    response = api.call(f"/v5/organizations/{ORG_SLUG}/forms/Membership/{SUBSCRIPTION_SLUG}/orders", method="GET", params={"userSearchKey" : name, "withDetails": "true"})
    nb_matches = response.json()["pagination"]["totalCount"]
    await ctx.send(f"Il y a {nb_matches} correspondances pour '{name}'")
    for match in response.json()["data"]:
        LOGGER.debug("Match for %s: %s", name, match)
        LOGGER.debug("Items for %s: %s", name, match["items"])
        items = match["items"]

        # Retrieve Membership informations:
        membership = next(filter(lambda item: item["type"] == "Membership", items), None)
        if membership is None:
            LOGGER.error("No membership found in items: %s", items)
            await ctx.send(f":x: Failed to retrieve informations about {name}")
            return
        LOGGER.debug("Found Membership for %s in items: %s", name, membership)

        first_name = membership["user"]["firstName"]
        last_name = membership["user"]["lastName"]
        payer_email = match["payer"]["email"]
        item = membership["name"]
        tombola = "OUI" if membership.get("options") is not None else "NON"
        reduction = membership["discount"]["code"] if membership.get("discount") is not None else "Aucun"

        # Retrieve additional informations:
        additional_infos = "Autres informations:\n"
        donation = next(filter(lambda item: item["type"] == "Donation", items), None)
        if donation is not None:
            donation_amount = int(donation["amount"])/100
            additional_infos += f"- Don: **{donation_amount} €**\n"

        custom_fields = membership["customFields"]
        mobile_field = next(filter(lambda field: field['name'].startswith("Téléphone"), custom_fields), None)
        if mobile_field is not None:
            mobile_answer = mobile_field["answer"]
            additional_infos += f"- Téléphone: {mobile_answer}\n"

        diet_field = next(filter(lambda field: field['name'].startswith("Précision alimentaire"), custom_fields), None)
        if diet_field is not None:
            diet_answer = diet_field["answer"]
            additional_infos += f'- Régime Alimentaire: "{diet_answer}"\n'

        comment_field = next(filter(lambda field: field['name'].startswith("Un commentaire"), custom_fields), None)
        if comment_field is not None:
            comment_answer = comment_field["answer"]
            additional_infos += f'- Commentaire: "{comment_answer}"\n'

        # Assemble informations
        membership_info = f"{first_name} {last_name} (email payeur: {payer_email}):\n- {item}\n- Tombola: {tombola}\n- Code Promo: {reduction}\n"
        await ctx.send(f"{membership_info}\n{additional_infos}")

@bot.event
async def on_message(message):
    if bot.user.mentioned_in(message):
        commands = ", ".join([cmd.name for cmd in bot.commands])
        await message.channel.send(f"Voici la liste des commandes existantes, **à préfixer par '{COMMAND_PREFIX}'**:\n{commands}\n\nExemple: '{COMMAND_PREFIX}gbesoindamour'")
    else:
        await bot.process_commands(message)

heart = ":heart: "

@bot.command(help="te donne de l'amour")
async def gbesoindamour(ctx):
    await ctx.send(":heart: N'oublie jamais que l'**on t'aime tous très fort** et que tu es le meilleur quoi qu'il arrive !!! :heart:")

@bot.command(help="envoie de l'amour aux autres")
async def keursurtoi(ctx, *args):
    name = " ".join(list(args))
    await ctx.send(f"{heart * 10}\n hey __**{name}**__, {ctx.author.display_name} t'envoie plein de keur et tout son amour ! \n{heart * 10}")

if __name__ == "__main__":
    try:
        # log_handler=None will prevent set up of the 'discord' logger all logs will be handled
        # by the root looger which has been set up
        LOGGER.info("Bot Token: %s", BOT_TOKEN)
        bot.run(BOT_TOKEN, log_handler=None)
    except discord.errors.LoginFailure:
        print("Invalid discord token")
        exit(1)

