from discord import Embed

import src.modules.game.chess.board as board
from src.utils.game import wait_for_player


"""
    This module manages the creation of a game of chess
"""


async def init(infos):
    embed = Embed(title=infos.text_data["game.chess.name"],
                  description="",
                  color=0xD828D0)
    embed.add_field(name=infos.text_data["game.creator"],
                    value=infos.message.author.mention,
                    inline=False)
    embed.set_footer(text=infos.text_data["game.chess.entry.footer"])

    message = await infos.client.send_message(
        infos.message.channel,
        embed=embed
    )

    second_player = await wait_for_player(infos, message)
    if second_player is None:
        return None
    else:
        return (
            board.Board(
                [
                    infos.message.author,
                    second_player
                ],
                message,
            )
        )
