command_list = [
    "ping",
    "blackjack",
    "bj",
    "chess",
    "tic-tac-toe",
    "ttt",
    "morpion",
    "connect4",
    "rank",
    "ranktop",
    "reward",
    "bank",
    "banktop",
    "autorole",
    "shop",
    "purge",
    "mute",
    "unmute",
    "kick",
    "ban"
]

cannot_disable = [
    "help",
    "prefix",
    "language",
    "enable",
    "disable"
]


async def is_disabled(infos, command):
    disabled = await infos.storage.smembers("disabled_commands")
    if not disabled:
        return False

    return command in disabled


async def allowed(infos):
    if not infos.message.author.server_permissions.manage_server:
        await infos.client.send_message(
            infos.message.channel,
            infos.text_data["info.error.permission"]
        )
        return False

    return True


async def enable(infos):
    if not await allowed(infos):
        return

    msg = infos.message.content.split()
    if len(msg) == 1:
        await infos.client.send_message(
            infos.message.channel,
            infos.text_data["info.error.syntax"]
        )
        return

    command = msg[1]

    if command in cannot_disable:
        await infos.client.send_message(
            infos.message.channel,
            infos.text_data["enable.cannot_disable"]
        )
        return

    if command not in command_list:
        await infos.client.send_message(
            infos.message.channel,
            infos.text_data["enable.not_found"]
        )
        return

    await infos.storage.srem(
        "disabled_commands",
        command
    )
    await infos.client.send_message(
        infos.message.channel,
        infos.text_data["enable.enabled"]
    )


async def disable(infos):
    if not await allowed(infos):
        return

    msg = infos.message.content.split()
    if len(msg) == 1:
        await infos.client.send_message(
            infos.message.channel,
            infos.text_data["info.error.syntax"]
        )
        return

    command = msg[1]

    if command in cannot_disable:
        await infos.client.send_message(
            infos.message.channel,
            infos.text_data["enable.cannot_disable"]
        )
        return

    if command not in command_list:
        await infos.client.send_message(
            infos.message.channel,
            infos.text_data["enable.not_found"]
        )
        return

    await infos.storage.sadd(
        "disabled_commands",
        command
    )
    await infos.client.send_message(
        infos.message.channel,
        infos.text_data["enable.disabled"]
    )
