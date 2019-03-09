from discord import Embed
from discord import utils

from src.utils.confirm import confirm

"""
    This module manages the autorole
"""


async def get_autorole(infos):
    embed = Embed(
        title="",
        description="",
        color=0xD828D0
    )

    role_id = await infos.storage.get(
        "autorole"
    )

    if role_id is None:
        message = infos.text_data["autorole.not_set"]
    else:
        role = utils.get(
            infos.message.server.roles,
            id=role_id
        )
        if role is None:
            message = infos.text_data["autorole.deleted"]
        else:
            message = role.mention

    embed.add_field(
        name=infos.text_data["autorole.autorole"],
        value=message,
        inline=False
    )

    await infos.client.send_message(
        infos.message.channel,
        embed=embed
    )


async def set_autorole(infos, role):
    if await confirm(infos):
        await infos.storage.set(
            "autorole",
            role.id
        )
        await infos.client.send_message(
            infos.message.channel,
            infos.text_data["autorole.set"].format(
                role.name
            )
        )


async def del_autorole(infos):
    role_id = await infos.storage.get(
        "autorole"
    )
    if role_id is None:
        await infos.client.send_message(
            infos.message.channel,
            infos.text_data["autorole.not_set"]
        )
    elif await confirm(infos):
        await infos.storage.delete(
            "autorole"
        )
        await infos.client.send_message(
            infos.message.channel,
            infos.text_data["autorole.delete"]
        )


async def interpret(infos):
    if not infos.message.author.server_permissions.manage_server:
        await infos.client.send_message(
            infos.message.channel,
            infos.text_data["info.error.permission.author.missing"]
        )
    else:
        msg = infos.message.content.split()
        # If 1, msg = "y!autorole", i.e. we want to check it
        if len(msg) == 1:
            await get_autorole(infos)
        else:
            if msg[1] == "set":
                roles = infos.message.role_mentions
                if not roles:
                    await infos.client.send_message(
                        infos.message.channel,
                        infos.text_data["info.error.syntax"]
                    )
                else:
                    await set_autorole(
                        infos,
                        roles[0]
                    )
            elif msg[1] == "delete":
                await del_autorole(infos)
            else:
                await infos.client.send_message(
                    infos.message.channel,
                    infos.text_data["info.error.syntax"]
                )
