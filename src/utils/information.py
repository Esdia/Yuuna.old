import json


class Infos:
    def __init__(self, client, message, database):
        self.client = client
        self.message = message
        self.database = database
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

    async def get_language(self):
        lang = await self.storage.get("language")

        lang = "en" if lang is None else str(lang)

        data = open("lang/{}.lang".format(lang)).read()
        language_data = json.loads(data)

        return language_data


async def init(client, message, database):
    infos = Infos(
        client,
        message,
        database
    )
    infos.storage = await infos.get_storage()
    infos.prefix = await infos.get_prefix()
    infos.text_data = await infos.get_language()

    return infos
