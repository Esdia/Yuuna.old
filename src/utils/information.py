import json
import asyncio


class Infos:
    def __init__(self, client, message, database):
        self.client = client
        self.message = message
        self.database = database
        # Sometimes the bot tries to delete reactions. In order to do that, the bot need the manage_message permission
        # We will use this variable to see if the bot can do what it si trying to do
        self.manage_messages = message.server.me.server_permissions.manage_messages
        self.storage = None
        self.prefix = None
        self.text_data = None

    async def get_storage(self):
        storage = await self.database.get_storage(self.message.server)
        return storage

    async def get_prefix(self):
        prefix = await self.storage.get("prefix")

        prefix = "y!" if prefix is None else str(prefix)
        return prefix

    async def get_language(self, is_heroku):
        lang = await self.storage.get("language")

        lang = "en" if lang is None else str(lang)

        path = "lang/{}.lang"
        if is_heroku:
            path = "src/{}".format(
                path
            )

        data = open(
            path.format(lang)
        ).read()
        language_data = json.loads(data)

        return language_data


async def init(client, message, database, is_heroku):
    infos = Infos(
        client,
        message,
        database
    )
    infos.storage = await infos.get_storage()
    infos.prefix = await infos.get_prefix()
    infos.text_data = await infos.get_language(is_heroku)

    return infos


async def push_commands(database):
    command_list = [
        "ping",
        "autorole",

        "master",
        "confirm",

        "rank",
        "ranktop",
        "rewards",

        "bank",
        "banktop",
        "shop",

        "blackjack",
        "bj",
        "chess",
        "tic-tac-toe",
        "ttt",
        "morpion",
        "connect4",

        "purge",
        "mute",
        "unmute",
        "kick",
        "ban",
    ]

    await database.connect()
    await asyncio.sleep(2)

    await database.redis.delete("commands")

    for c in command_list:
        await database.redis.sadd(
            "commands",
            c
        )
        print('Pushed command : ' + c)
