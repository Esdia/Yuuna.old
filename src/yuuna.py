import discord
import logging

import os
import sys
from asyncio import sleep

import src.utils.information as information
from src.utils.storage import Database

from src.modules.commands import interpret
from src.modules.levels import give_xp


client = discord.Client()
is_heroku = os.environ.get('IS_HEROKU', False)
database = None
logger = None


def get_redis_url():
    if is_heroku:
        redis_url = os.environ.get('REDISTOGO_URL', None)
    else:
        redis_url = sys.argv[2]
    return redis_url


# Every 150 seconds, the redis connection closes, so every 120 seconds, I close it and reconnect it
async def refresh_redis():
    global database
    while True:
        redis_url = get_redis_url()
        if redis_url is not None:
            database = Database(redis_url)
        else:
            print('ERROR : No database URL provided')
            sys.exit(2)
        await sleep(120)


@client.event
async def on_ready():
    global database
    await client.change_presence(game=discord.Game(name="y!help"))

    client.loop.create_task(
        refresh_redis()
    )

    redis_url = get_redis_url()
    database = Database(redis_url)

    await information.push_commands(database)

    print('\nDiscord API version :', discord.__version__)
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.event
async def on_message(message):
    if not (message.author.bot or message.channel.is_private):
        log = "Message received : {} : {}, {} : {}, {}".format(
            message.server.name,
            message.server.id,
            message.author.name,
            message.author.id,
            message.content
        )
        logger.info(log)
        infos = await information.init(
            client,
            message,
            database,
            is_heroku
        )
        # if True, then the message was a command
        command = await interpret(infos)
        if not command:
            await give_xp(infos)


@client.event
async def on_server_join(server):
    log = "I just joined the server {} : {}, owned by {} : {}".format(
        server.name,
        server.id,
        server.owner,
        server.owner.id
    )
    logger.info(log)


@client.event
async def on_server_remove(server):
    log = "I have left the server {} : {}, owned by {} : {}".format(
        server.name,
        server.id,
        server.owner,
        server.owner.id
    )
    logger.info(log)


@client.event
async def on_member_ban(member):
    log = "The member {} : {} have been banned from the server {} : {} owned by {} {}".format(
        member.name,
        member.id,
        member.server.name,
        member.server.id,
        member.server.owner.name,
        member.server.owner.id
    )
    logger.info(log)


@client.event
async def on_member_unban(server, user):
    log = "The user {} : {} have been unbanned from the server {} : {} owned by {} {}".format(
        user.name,
        user.id,
        server.name,
        server.id,
        server.owner.name,
        server.owner.id
    )
    logger.info(log)


@client.event
async def on_member_join(member):
    log = "{} : {} joined the server {} : {} owned by {} : {}".format(
        member.name,
        member.id,
        member.server.name,
        member.server.id,
        member.server.owner.name,
        member.server.owner.id
    )
    logger.info(log)

    storage = await database.get_storage(member.server)
    role_id = await storage.get(
        "autorole"
    )
    role = discord.utils.get(
        member.server.roles,
        id=role_id
    )
    if role is not None:
        await client.add_roles(
            member,
            role
        )
        log = "autorole given : {} : {}".format(
            role.name,
            role.id
        )
        logger.info(log)


@client.event
async def on_member_remove(member):
    log = "{} : {} left the server {} : {} owned by {} : {}".format(
        member.name,
        member.id,
        member.server.name,
        member.server.id,
        member.server.owner.name,
        member.server.owner.id
    )
    logger.info(log)
    storage = await database.get_storage(member.server)
    await storage.delete(
        "user:{}:bank".format(
            member.id
        )
    )
    await storage.srem(
        "users:bank",
        member.id
    )
    await storage.delete(
        "user:{}:xp".format(
            member.id
        )
    )
    await storage.srem(
        "users:xp",
        member.id
    )


if __name__ == "__main__":
    logger = logging.getLogger("discord")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)

    print("Logging in...")
    if is_heroku:
        token = os.environ.get('TOKEN', None)
    else:
        token = sys.argv[1]

    if token is not None:
        client.run(token)
    else:
        print("LOGIN ERROR : NO TOKEN PROVIDED")
        sys.exit(1)
