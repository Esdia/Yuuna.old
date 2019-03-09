from src.modules.game.chess.init import init
from src.modules.game.chess.pieces import Pieces
from src.modules.game.chess.message import update_message

channel_list = []

"""
    This module manage a game of chess
"""


# Given a player input, this function checks if the input is correct, and if the player is allowed to do whatever they are trying to do
# If the input is somehow incorrect, this function returns the correct phrase to send at this moment
# If the function returns none, it means that everything went fine
def parse_input(infos, play, game_infos, color):
    in_check = game_infos.in_check(color)
    board = game_infos.board
    promotion = None

    if play == "O-O-O":
        if in_check:
            return infos.text_data["game.chess.error.castle.check"]

        if color == "BLACK":
            line = 0
        else:
            line = 7

        # If the kind has not moved, he is on the 'e' column, the fifth one, hence the index 4
        # The long castle (queen-sided) is left-sided, so index 4 for the rook
        king = board[line][4]
        rook = board[line][0]
        if type(king) is Pieces.King and not king.has_moved:
            if type(rook) is Pieces.Rook and not rook.has_moved:
                if any(type(board[line][i]) is not str for i in range(1, 4)):
                    return infos.text_data["game.chess.error.castle.not_empty_queen"]
                else:
                    if any(game_infos.in_check(color, line, y) for y in range(2, 4)):
                        return infos.text_data["game.chess.error.castle.through_check"]
                    else:
                        # We move the king
                        game_infos.play_move(line, 4, line, 2)
                        # And we move the rook
                        game_infos.play_move(line, 0, line, 3)
                        return None
            else:
                return infos.text_data["game.chess.error.castle.queen_rook"]
        else:
            return infos.text_data["game.chess.error.castle.king"]
    elif play == "O-O":
        if in_check:
            return infos.text_data["game.chess.error.castle.check"]

        if color == "BLACK":
            line = 0
        else:
            line = 7

        # If the kind has not moved, he is on the 'e' column, the fifth one, hence the index 4
        # The long castle (queen-sided) is left-sided, so index 4 for the rook
        king = board[line][4]
        rook = board[line][7]
        if type(king) is Pieces.King and not king.has_moved:
            if type(rook) is Pieces.Rook and not rook.has_moved:
                if any(type(board[line][i]) is not str for i in range(5, 7)):
                    return infos.text_data["game.chess.error.castle.not_empty_king"]
                else:
                    if any(game_infos.in_check(color, line, y) for y in range(5, 7)):
                        return infos.text_data["game.chess.error.castle.through_check"]
                    else:
                        # We move the king
                        game_infos.play_move(line, 4, line, 6)
                        # And we move the rook
                        game_infos.play_move(line, 0, line, 5)
                        return None
            else:
                return infos.text_data["game.chess.error.castle.king_rook"]
        else:
            return infos.text_data["game.chess.error.castle.king"]
    else:
        if len(play) == 7:
            if play[5] == "=":
                # To promote, a pawn must reach the back line of the opposite camp
                if color == "WHITE":
                    back_line = 0
                else:
                    back_line = 7
                # If the input is correctly formatted, which is verified later, play[4] will contain the x coordinate (the line) of the destination, cf line 98.
                if play[4].isdigit() and 8 - int(play[4]) == back_line:
                    if play[6] in ["R", "B", "N", "Q"]:
                        promotion = play[6]
                        play = play[:5]
                    else:
                        return infos.text_data["game.chess.error.promote.piece"]
                else:
                    return infos.text_data["game.chess.error.format"]
            else:
                return infos.text_data["game.chess.error.format"]
        if len(play) == 5:
            if 'a' <= play[0] <= 'h' and '1' <= play[1] <= '8' and play[2] == '-' and 'a' <= play[3] <= 'h' and '1' <= play[4] <= '8':
                y_start = ord(play[0]) - ord('a')
                x_start = 8 - int(play[1])

                y_end = ord(play[3]) - ord('a')
                x_end = 8 - int(play[4])

                piece = board[x_start][y_start]
                if type(piece) is str:
                    return infos.text_data["game.chess.error.no_piece"]
                elif piece.color != color:
                    return infos.text_data["game.chess.error.opposite_piece"]
                elif (x_end, y_end) not in piece.available_moves(board):
                    return infos.text_data["game.chess.error.illegal_move"]
                elif game_infos.in_check_after_play(piece.color, x_start, y_start, x_end, y_end):
                    return infos.text_data["game.chess.error.check"]
                elif game_infos.would_be_in_check_if_moved(piece):
                    return infos.text_data["game.chess.error.go_to_check"]
                else:
                    if promotion is not None and type(piece) != Pieces.Pawn:
                        return infos.text_data["game.chess.error.promote.from_piece"]
                    game_infos.play_move(x_start, y_start, x_end, y_end, promotion=promotion)
                    return None
            else:
                return infos.text_data["game.chess.error.format"]
        else:
            return infos.text_data["game.chess.error.format"]


# Called to end the game
async def end(infos, winner=None, stalemate=False, inactivity=False, forfeit=False):
    if inactivity:
        await infos.client.send_message(
            infos.message.channel,
            infos.text_data["game.chess.inactivity.lost"].format(
                winner.mention
            )
        )
    elif forfeit:
        await infos.client.send_message(
            infos.message.channel,
            infos.text_data["game.chess.forfeit"].format(
                winner.mention
            )
        )
    elif winner is not None:
        await infos.client.send_message(
            infos.message.channel,
            "{}\n{}".format(
                infos.text_data["game.chess.checkmate"],
                infos.text_data["game.winner"].format(
                    winner.mention
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


# Manages a game
async def game(infos, game_infos):
    turn = 0
    colors = [
        "WHITE",
        "BLACK"
    ]
    while game_infos.status() == "NONE":
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
                    infos.message.text_data["game.chess.warning"].format(
                        game_infos.players[turn]
                    )
                )
                play = await infos.client.wait_for_message(
                    timeout=60,
                    author=game_infos.players[turn],
                    channel=infos.message.channel
                )
            if play is None:
                winner = game_infos.players[
                    1 - turn
                ]
                await end(
                    infos,
                    winner,
                    inactivity=True
                )
                return
            elif play.content == "stop":
                winner = game_infos.players[
                    1 - turn
                ]
                await end(
                    infos,
                    winner=winner,
                    forfeit=True
                )
            else:
                parsed_play = parse_input(
                    infos,
                    play.content,
                    game_infos,
                    colors[
                        turn
                    ]
                )
            if parsed_play is not None:
                await infos.client.send_message(
                    infos.message.channel,
                    parsed_play
                )

        turn = 1 - turn
        await update_message(infos, game_infos)
        if game_infos.status() == "NONE":
            await infos.client.send_message(
                infos.message.channel,
                infos.text_data["game.chess.turn"].format(
                    game_infos.players[
                        turn
                    ].mention,
                    colors[
                        turn
                    ]
                )
            )

    status = game_infos.status()
    if status == "STALEMATE":
        await end(infos, stalemate=True)
    elif status == "DRAW":
        await end(infos)
    else:
        if status == "WHITE":
            winner = game_infos.players[1]  # White losing, black winning
        else:
            winner = game_infos.players[0]  # Black losing, white winning
        await end(infos, winner=winner)


# Called when a user uses the "y!chess" command. It creates and start the chess game
async def start(infos):
    channel = infos.message.channel
    if channel.id not in channel_list:
        channel_list.append(channel.id)
        game_infos = await init(infos)

        if game_infos is None:
            await infos.client.send_message(
                channel,
                infos.text_data["game.chess.inactivity.cancel"]
            )
        else:
            await update_message(infos, game_infos)
            await game(infos, game_infos)

        channel_list.remove(channel.id)
    else:
        infos.client.send_message(
            channel,
            infos.text_data["game.chess.already_launched"]
        )
