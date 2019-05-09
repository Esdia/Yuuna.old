import src.modules.help as help_module
import src.modules.configuration as conf
import src.modules.moderation as moderation
import src.modules.disable_commands as disable_commands

import src.modules.game.tic_tac_toe as tic_tac_toe
import src.modules.game.blackjack.blackjack as black_jack
import src.modules.game.connect4.connect4 as connect4
import src.modules.game.chess.game as chess

import src.modules.levels as levels
import src.modules.bank as bank
import src.modules.shop as shop

import src.modules.autorole as autorole


async def ping(infos):
    t = await infos.client.send_message(
        infos.message.channel,
        'Pong!'
    )
    ms = (t.timestamp - infos.message.timestamp).total_seconds() * 1000
    await infos.client.edit_message(
        t,
        new_content="Pong! {}ms".format(
            int(ms)
        )
    )


async def interpret(infos):
    command_list = {
        "ping": ping,
        "help": help_module.interpret,
        "autorole": autorole.interpret,

        "prefix": conf.prefix,
        "language": conf.language,
        "enable": disable_commands.enable,
        "disable": disable_commands.disable,
        "master": conf.bot_master,
        "confirm": conf.confirm,

        "rank": levels.interpret,
        "ranktop": levels.ranktop,
        "reward": levels.rewards_interpret,

        "bank": bank.interpret,
        "banktop": bank.banktop,
        "shop": shop.interpret,

        "blackjack": black_jack.create,
        "bj": black_jack.create,
        "chess": chess.start,
        "tic-tac-toe": tic_tac_toe.entry,
        "ttt": tic_tac_toe.entry,
        "morpion": tic_tac_toe.entry,
        "connect4": connect4.start,

        "purge": moderation.purge,
        "mute": moderation.mute,
        "unmute": moderation.unmute,
        "kick": moderation.kick,
        "ban": moderation.ban
    }

    msg = infos.message.content.split()

    if len(msg) == 0:
        return True

    for c in command_list:
        if msg[0] == infos.prefix + c:
            if await disable_commands.is_disabled(infos, c):
                return False
            else:
                await command_list[c](infos)
                return True

    # prefix and help are the only commands which can always be executed with the default prefix, even if the prefix has been changed
    if msg[0] == "y!prefix":
        await conf.prefix(infos)
        return True
    elif msg[0] == "y!help":
        await help_module.interpret(infos)
        return True

    return False
