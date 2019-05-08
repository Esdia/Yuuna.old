import discord
from src.utils.perm import allowed


# This function allows the user to change the server-local command prefix
async def prefix(infos):
    msg = infos.message.content.split()

    # There, the user wants to see the current prefix
    if len(msg) == 1:
        await infos.client.send_message(
            infos.message.channel,
            infos.text_data["config.prefix.get"].format(infos.prefix)
        )

    # The user should not be mentioning anything
    elif infos.message.mentions or infos.message.channel_mentions or infos.message.role_mentions:
        await infos.client.send_message(
            infos.message.channel,
            infos.text_data["infos.error.syntax"]
        )

    else:
        if not await allowed(infos, "manage_server"):
            await infos.storage.set(
                "prefix",
                msg[1]
            )
            await infos.client.send_message(
                infos.message.channel,
                infos.text_data["config.prefix.set"].format(
                    msg[1]
                )
            )
        else:
            await infos.client.send_message(
                infos.message.channel,
                infos.text_data["infos.error.permission.author.missing"]
            )


# This function allows the user to change the server-local language
async def language(infos):
    msg = infos.message.content.split()

    if not await allowed(infos, "manage_server"):
        await infos.client.send_message(
            infos.message.channel,
            infos.text_data["info.error.permission.author.missing"]
        )

    else:
        if len(msg) != 2 or infos.message.mentions or infos.message.channel_mentions or infos.message.role_mentions:
            await infos.client.send_message(
                infos.message.channel,
                infos.text_data["info.error.syntax"]
            )
        else:
            if msg[1] not in ["en", "fr"]:
                await infos.client.send_message(
                    infos.message.channel,
                    infos.text_data["config.language.not_found"]
                )
            else:
                await infos.storage.set(
                    "language",
                    msg[1]
                )
                await infos.client.send_message(
                    infos.message.channel,
                    infos.text_data["config.language.set"].format(
                        infos.text_data[
                            "language.{}".format(msg[1])
                        ]
                    )
                )


# Return the bot_master role
async def get_master(infos):
    master_id = await infos.storage.get("bot_master")
    if master_id:
        master = discord.utils.get(
            infos.message.server.roles,
            id=master_id
        )
        return master
    return None


# Delete the current bot master
async def del_master(infos):
    await infos.storage.delete("bot_master")


# Sets the bot master
async def set_master(infos, master):
    await infos.storage.set("bot_master", master.id)


# The bot master is a role that can bypass every permission check
async def bot_master(infos):
    msg = infos.message.content.split()

    if not await allowed(infos, "manage_server"):
        await infos.client.send_message(
            infos.message.channel,
            infos.text_data["info.error.permission.author.missing"]
        )
        return

    if len(msg) == 1:
        master = await get_master(infos)
        if not master:
            await infos.client.send_message(
                infos.message.channel,
                infos.text_data["bot_master.no_role"]
            )
        else:
            await infos.client.send_message(
                infos.message.channel,
                infos.text_data["bot_master.role"].format(
                    master.mention
                )
            )
    elif msg[1] in ['set', 'delete']:
        if (msg[1] == "delete" and len(msg) != 2) or (msg[1] == "set" and (len(msg) != 3 or not infos.message.role_mentions)):
            await infos.client.send_message(
                infos.message.channel,
                infos.text_data["info.error.syntax"]
            )
            return

        if msg[1] == "delete":
            if not infos.message.author.server_permissions.manage_server:
                await infos.client.send_message(
                    infos.message.channel,
                    infos.text_data['bot_master.self_del']
                )
                return

            await del_master(infos)
            await infos.client.send_message(
                infos.message.channel,
                infos.text_data["bot_master.del"]
            )
        else:
            master = infos.message.role_mentions[0]
            await set_master(infos, master)
            await infos.client.send_message(
                infos.message.channel,
                infos.text_data["bot_master.set"].format(
                    master.mention
                )
            )
    else:
        await infos.client.send_message(
            infos.message.channel,
            infos.text_data["info.error.syntax"]
        )


async def confirm(infos):
    if not await allowed(infos, "manage_server"):
        await infos.client.send_message(
            infos.message.channel,
            infos.text_data["info.error.permission.author.missing"]
        )
        return

    msg = infos.message.content.split()
    if len(msg) != 2 or msg[1] not in ["0", "1"]:
        await infos.client.send_message(
            infos.message.channel,
            infos.text_data["info.error.syntax"]
        )
        return

    if msg[1] == "1":
        await infos.storage.delete("ignore_confirm")
        await infos.client.send_message(
            infos.message.channel,
            infos.text_data["ignore_confirm.disable"]
        )
    else:
        await infos.storage.set("ignore_confirm", "1")
        await infos.client.send_message(
            infos.message.channel,
            infos.text_data["ignore_confirm.enable"]
        )
