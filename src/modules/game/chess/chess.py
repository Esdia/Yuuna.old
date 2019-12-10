from discord import Embed
from src.modules.game.chess.board import *
from src.utils.game import wait_for_player
from src.modules.game.chess.message import *

channel_list = []


class Game:
    def __init__(self, players, message):
        self.board = Board()
        self.players = players
        self.message = message


async def init_game(infos):
    embed = Embed(
        title=infos.text_data["game.chess.name"],
        description="",
        color=0xD828D0
    )
    embed.add_field(
        name=infos.text_data["game.creator"],
        value=infos.message.author.mention,
        inline=False
    )
    embed.set_footer(text=infos.text_data["game.chess.entry.footer"])

    message = await infos.client.send_message(
        infos.message.channel,
        embed=embed
    )

    second_player = await wait_for_player(infos, message)
    if second_player is None:
        return None
    return Game(
        [
            infos.message.author,
            second_player
        ],
        message
    )


def parse_input(infos, play, game_infos, color):
    promotion = None

    if play in ["O-O-O", "O-O"]:
        big_castle = (play == "O-O-O")
        can_castle = game_infos.board.can_castle(color, big_castle)
        if can_castle == 0:
            game_infos.board.castle(color, big_castle)
            return None
        elif can_castle == 1:
            return infos.text_data["game.chess.error.castle.king"]
        elif can_castle == 2:
            if big_castle:
                return infos.text_data["game.chess.error.castle.queen_rook"]
            else:
                return infos.text_data["game.chess.error.castle.king_rook"]
        elif can_castle == 3:
            if big_castle:
                return infos.text_data["game.chess.error.castle.not_empty_queen"]
            else:
                return infos.text_data["game.chess.error.castle.not_empty_king"]
        elif can_castle == 4:
            return infos.text_data["game.chess.error.castle.through_check"]
    else:
        if len(play) == 7:
            if color == "W":
                back_line = 0
            else:
                back_line = 7
            if play[5] != "=":
                return infos.text_data["game.chess.error.format"]
            if not play[4].isdigit() or 8 - int(play[4]) != back_line:
                return infos.text_data["game.chess.error.format"]
            if play[6] not in ["R", "N", "B", "Q"]:
                return infos.text_data["game.chess.error.promote.piece"]
            promotion = play[6]
            play = play[:5]
        if len(play) == 5:
            if not('a' <= play[0] <= 'h' and '1' <= play[1] <= '8' and play[2] == '-' and 'a' <= play[3] <= 'h' and '1' <= play[4] <= '8'):
                return infos.text_data["game.chess.error.format"]
            y_start = ord(play[0]) - ord('a')
            x_start = 8 - int(play[1])

            y_end = ord(play[3]) - ord('a')
            x_end = 8 - int(play[4])

            piece = game_infos.board.board[x_start][y_start]
            if piece is None:
                return infos.text_data["game.chess.error.no_piece"]
            elif piece.color != color:
                return infos.text_data["game.chess.error.opposite_piece"]
            elif (x_end, y_end) not in piece.legal_moves(game_infos.board):
                return infos.text_data["game.chess.error.illegal_move"]
            elif game_infos.board.in_check_after_play(piece, x_end, y_end):
                if game_infos.board.king_on_check(color):
                    return infos.text_data["game.chess.error.check"]
                else:
                    return infos.text_data["game.chess.error.go_to_check"]
            else:
                if promotion is not None and type(piece) is not Pawn:
                    return infos.text_data["game.chess.error.promote.from_piece"]
                piece.move(game_infos.board, x_end, y_end, promotion)
                return None
        else:
            return infos.text_data["game.chess.error.format"]


async def end(infos, winner=None, inactivity=False, forfeit=False, stalemate=False):
    if inactivity:
        await infos.client.send_message(
            infos.message.channel,
            infos.text_data["game.chess.inactivity.lost"].format(
                member=winner.mention
            )
        )
    elif forfeit:
        await infos.client.send_message(
            infos.message.channel,
            infos.text_data["game.chess.forfeit"].format(
                member=winner.mention
            )
        )
    elif winner is not None:
        await infos.client.send_message(
            infos.message.channel,
            "{}\n{}".format(
                infos.text_data["game.chess.checkmate"],
                infos.text_data["game.winner"].format(
                    member=winner.mention
                )
            )
        )
    elif stalemate:
        await infos.client.send_message(
            infos.message.channel,
            "{}\n{}".format(
                infos.text_data["game.chess.stalemate"],
                infos.text_data["game.tie"]
            )
        )
    else:
        await infos.client.send_message(
            infos.message.channel,
            infos.text_data["game.chess.lack_of_material"]
        )


async def game(infos, game_infos: Game):
    turn = 0
    colors = ["W", "B"]
    while game_infos.board.status() is None:
        parsed_play = ""
        while parsed_play is not None:
            play = await infos.client.wait_for_message(
                timeout=240,
                author=game_infos.players[turn],
                channel=infos.message.channel
            )
            if play is None:
                await infos.client.send_message(
                    infos.message.channel,
                    infos.text_data["game.chess.warning"].format(
                        member=game_infos.players[turn]
                    )
                )
                play = await infos.client.wait_for_message(
                    timeout=240,
                    author=game_infos.players[turn],
                    channel=infos.message.channel
                )
            if play is None:
                winner = game_infos.players[1-turn]
                await end(infos, winner=winner, inactivity=True)
                return
            elif play.content == "stop":
                winner = game_infos.players[1-turn]
                await end(
                    infos,
                    winner=winner,
                    forfeit=True
                )
                return
            else:
                parsed_play = parse_input(
                    infos,
                    play.content,
                    game_infos,
                    colors[turn]
                )
                if parsed_play is not None:
                    await infos.client.send_message(
                        infos.message.channel,
                        parsed_play
                    )
        turn = 1 - turn
        await update_message(infos, game_infos)
        if game_infos.board.status() is None:
            await infos.client.send_message(
                infos.message.channel,
                infos.text_data["game.chess.turn"].format(
                    member=game_infos.players[turn].mention,
                    color=infos.text_data[
                        "game.chess.color." + ("white" if turn == 0 else "black")
                    ]
                )
            )

    status = game_infos.board.status()
    if status == "STALEMATE":
        await end(
            infos,
            stalemate=True
        )
    elif status == "DRAW":
        await end(infos)
    else:
        if status == "W":
            winner = game_infos.players[1]  # White loses, black wins
        else:
            winner = game_infos.players[0]  # Black loses, white wins
        await end(
            infos,
            winner=winner
        )


async def start(infos):
    channel = infos.message.channel
    if channel.id not in channel_list:
        channel_list.append(channel.id)
        game_infos = await init_game(infos)

        if game_infos is None:
            await infos.client.send_message(
                channel,
                infos.text_data['game.chess.inactivity_cancel']
            )
        else:
            await update_message(infos, game_infos)
            await infos.client.send_message(
                infos.message.channel,
                infos.text_data["game.chess.turn"].format(
                    member=game_infos.players[0].mention,
                    color=infos.text_data["game.chess.color.white"]
                )
            )
            await game(infos, game_infos)

        channel_list.remove(channel.id)
    else:
        await infos.client.send_message(
            channel,
            infos.text_data["game.chess.already_launched"]
        )
