import discord
import os

from bot import aerialace
from bot import aerialace_data_manager
from bot import aerialace_init_manager
from bot import aerialace_cache_manager
from bot import aerialace_battle_manager
from bot import global_vars

# Intents
intents = discord.Intents.all()
intents.typing = False
intents.reactions = True

# init
client = discord.Client(intents=intents)

admin_user_id = os.environ['ADMIN_ID']
poketwo_user_id = os.environ['POKETWO_ID']

@client.event
async def on_guild_join(guild_joined):
    await aerialace_init_manager.register_guild(client, guild_joined)
    print("server was joined and registered")


@client.event
async def on_guild_remove(guild_removed):
    await aerialace_init_manager.remove_guild(client, guild_removed)
    print("server was removed")


@client.event
async def on_ready():
    print("Logged in as {0.user}".format(client))
    await aerialace_cache_manager.cache_data(init=True)
    await aerialace.start_rich_presence_cycle(client, 15)


@client.event
async def on_message(message):

    if str(message.author.id) == poketwo_user_id:
        catch_info = await aerialace.determine_rare_catch(message.content)
        if catch_info is None:
            return
        ping = catch_info[0]
        pokemon_caught = catch_info[2].lower()
        level = catch_info[1]

        if aerialace_cache_manager.cached_rarity_data[pokemon_caught] == "legendary" or aerialace_cache_manager.cached_rarity_data[pokemon_caught] == "mythical":
            rare_catch_embed = await aerialace.get_rare_catch_embd(ping, pokemon_caught, level)
            await message.channel.send(embed=rare_catch_embed)
            return
        else:
            return

    # ignore messages sent by the bot
    if message.author == client.user:
        return

    # ignore commands not meant for the bot
    if message.content.lower().startswith("-aa") is False and (message.content != "<@!908384747393286174>" and message.content != "<@908384747393286174>"):
        return

    # respond to pings
    if message.content == "<@!908384747393286174>" or message.content == "<@908384747393286174>":
        await message.channel.send("> Aerial Ace prefix is `-aa`.\n> Try `-aa help` :3")
        return

    guild = message.guild
    server_id = str(guild.id)

    # get the message details
    msg = ((message.content.lower()).replace("-aa", "")).strip()
    member = message.author
    user_id = str(message.author.id)
    user_name = member.display_name

    # help command
    if msg.startswith("help"):
        help_embed = aerialace.get_help_embed()
        await message.channel.send(embed=help_embed)

        return

    # say hello command
    hello_commands = ["hello", "alola", "hola", "henlu", "helu", "hi", "sup"]
    if msg in hello_commands:
        await message.channel.send("> Alola **{name}**".format(name=user_name))
        return

    # rolling command
    if msg.startswith("roll"):
        upper_limit = await aerialace.get_parameter(msg, ["roll"])
        reply = await aerialace.get_roll(user_name, upper_limit)
        await message.channel.send(reply)

        return

    # Random Pokemon command
    if (msg.startswith("rp")) or msg.startswith("rand_poke"):
        
        rand_poke = await aerialace.get_random_poke()

        reply = await aerialace.get_random_pokemon_embed(rand_poke, server_id, user_id)

        await message.channel.send(embed=reply)
        return

    # Dex search command
    if msg.startswith("dex"):

        poke = await aerialace.get_parameter(msg, ["dex"])

        try:
            poke_id = aerialace_cache_manager.cached_alt_name_data[poke]
        except:
            poke_id = poke

        try:
            poke_data = await aerialace.get_poke_by_id(poke_id)
        except:
            reply = await aerialace.get_info_embd("Pokemon not found", f"Dex entry for id : `{poke_id}` was not found in the pokedex.\n Most uncommon ids follow this format : \n```-aa dex gallade-mega\n-aa dex meowstic-female\n-aa dex deoxys-defense```", global_vars.ERROR_COLOR)
            await message.channel.send(embed=reply)
            return

        reply = await aerialace.get_dex_entry_embed(poke_data)

        await message.channel.send(embed=reply)

        return

    # Register Favourite Pokemon command
    if msg.startswith("set_fav") or msg.startswith("sf"):
        poke = await aerialace.get_parameter(msg, ["set_fav", "sf"])

        reply = await aerialace_data_manager.set_fav(server_id, user_id, poke)
        await message.channel.send(reply)
        return

    # View favourite pokemon command
    if msg.startswith("fav"):
        reply = await aerialace_data_manager.get_fav(server_id, user_id)
        await message.channel.send(reply)
        return

    # get duelish stats command
    if msg.startswith("stats"):
        poke = await aerialace.get_parameter(msg, ["stats"])
        reply = await aerialace_data_manager.get_stats_embed(poke)

        await message.channel.send(embed=reply)

        return

    # get duelish moveset command
    if msg.startswith("moveset") or msg.startswith("ms"):
        poke = await aerialace.get_parameter(msg, ["ms", "moveset"])
        reply = await aerialace_data_manager.get_moveset_embed(poke)
        await message.channel.send(embed=reply)

        return

    # get tierlist command
    if msg.startswith("tierlist") or msg.startswith("tl"):
        poke = await aerialace.get_parameter(msg, ["tierlist", "tl"])

        tl_link = await aerialace_data_manager.get_tl(poke)
        await message.channel.send(content="Source : P2HB \n {link}".format(link=tl_link))

        return

    # invite command
    if msg.startswith("invite"):
        reply = await aerialace.get_invite_embed(discord.Embed(), discord.Color.blue())
        await message.channel.send(embed=reply)

        return

    # register tags
    if msg.startswith("tag "):
        tag = await aerialace.get_parameter(msg, ["tag"])
        reply = await aerialace_data_manager.register_tag(server_id, user_id, user_name, tag)
        await message.channel.send(reply)

        return

    # ping user with tag command
    if msg.startswith("tag_ping") or msg.startswith("tp"):
        tag = await aerialace.get_parameter(msg, ["tp", "tag_ping"])
        hunters = await aerialace_data_manager.get_tag_hunters(server_id, tag)

        if hunters is None:
            reply = await aerialace.get_info_embd("Tag not found", "No one is assigned to `{tag}` tag".format(tag=tag.capitalize()), global_vars.WARNING_COLOR)
            await message.channel.send(embed=reply)
        else:
            hunter_pings = ""
            number_of_hunters = len(hunters)

            for i in range(0, number_of_hunters):
                hunter_pings = hunter_pings + "<@{user}>".format(user=str(hunters[i]))
                if i <= number_of_hunters - 2:
                    hunter_pings += " | "

            reply = "> Pinging users assigned to `{tag}` tag \n\n {users}".format(tag=tag.capitalize(), users=hunter_pings)

            await message.channel.send(reply)

        return

    # see user assigned to tag
    if msg.startswith("tag_show ") or msg.startswith("ts "):
        tag = await aerialace.get_parameter(msg, ["tag_show", "ts"])
        hunters = await aerialace_data_manager.get_tag_hunters(server_id, tag)
        reply = await aerialace_data_manager.get_show_hunters_embd(tag=tag, hunters=hunters)
        await message.channel.send(embed=reply)
        return

    # logs the battle and update the leaderboard
    if msg.startswith("log_battle ") or msg.startswith("lb "):
        players = await aerialace.get_winner_looser(msg)
        info = await aerialace.get_battle_acceptance(client, message, players[0], players[1])

        if info == "accepted":
            reply = await aerialace_battle_manager.register_battle_log(server_id, players[0], players[1])
        elif info == "notaccepted":
            reply = "> Battle Log was not accepted"
        else:
            return

        await message.channel.send(reply)

        return

    # Display the battle score of the user
    if msg.startswith("battle_score") or msg.startswith("bs"):
        reply = await aerialace_battle_manager.get_battle_score(server_id, member)

        await message.channel.send(reply)
        return

    if msg.startswith("battle_lb") or msg.startswith("blb"):
        reply = await aerialace_battle_manager.get_battle_leaderboard_embed(client, guild)
        await message.channel.send(embed=reply)
        return

    if msg.startswith("sleep"):
        await message.channel.send("Waiting....")
        await aerialace.waiter(30)
        await message.channel.send("Times up....")
        return

    # Admins Only
    # returns the json files of the data
    if msg.startswith("fetch_data_files") or msg.startswith("fdf"):
        if user_id == admin_user_id:
            await aerialace_data_manager.send_data_files(client)
            await message.channel.send("> Data files were sent to admins :}")
        else:
            await message.channel.send("You are not supposed to use that command :/")

        return

    # command not found
    await message.channel.send("> -aa what? That command doesn't exist! \n"
                               "> See all the available commands by using ```-aa help```")

token = os.environ['TOKEN']

client.run(token)
