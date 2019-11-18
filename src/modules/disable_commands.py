from discord import Embed

from src.utils.perm import allowed

command_list = [
    "ping",
    "autorole",

    "config",

    "xp",

    "bank",

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

cannot_disable = [
    "help",
    "prefix",
    "language",
    "enable",
    "disable"
]

aliases_blackjack = [
    "blackjack",
    "bj"
]

aliases_tic_tac_toe = [
    "tic-tac-toe",
    "ttt",
    "morpion"
]

aliases = [
    aliases_blackjack,
    aliases_tic_tac_toe
]


async def is_disabled(infos, command):
    disabled = await infos.storage.smembers("disabled_commands")
    if not disabled:
        return False

    return command in disabled


async def check_format_command(infos):
    if not await allowed(infos, "manage_server"):
        return False

    msg = infos.message.content.split()
    if len(msg) == 1:
        await infos.client.send_message(
            infos.message.channel,
            infos.text_data["info.error.syntax"]
        )
        return False

    command = msg[1]

    if command in cannot_disable:
        await infos.client.send_message(
            infos.message.channel,
            infos.text_data["enable.cannot_disable"]
        )
        return False

    if command not in command_list:
        await infos.client.send_message(
            infos.message.channel,
            infos.text_data["enable.not_found"]
        )
        return False
    return True


async def enable(infos):
    if not await check_format_command(infos):
        return

    command = infos.message.content.split()[1]
    for al in aliases:
        if command in al:
            for al2 in al:
                await infos.storage.srem(
                    "disabled_commands",
                    al2
                )
            await infos.client.send_message(
                infos.message.channel,
                infos.text_data["enable.enabled"]
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


async def print_list(infos):
    disabled = "\n".join(await infos.storage.smembers("disabled_commands"))
    if disabled == "":
        disabled = infos.text_data["enable.no_disabled"]

    embed = Embed(
        title="",
        description="",
        color=0xD828D0
    )
    embed.add_field(
        name=infos.text_data["enable.disabled_list"],
        value=disabled,
        inline=False
    )

    await infos.client.send_message(
        infos.message.channel,
        embed=embed
    )


async def disable(infos):
    command = infos.message.content.split()[1]
    if command == "list":
        await print_list(infos)
        return

    if not await check_format_command(infos):
        return

    for al in aliases:
        if command in al:
            for al2 in al:
                await infos.storage.sadd(
                    "disabled_commands",
                    al2
                )
            await infos.client.send_message(
                infos.message.channel,
                infos.text_data["enable.disabled"]
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
