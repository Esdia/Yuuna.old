"""
    This module is used to manage the pieces

    The board is represented by a list of lists

    Each piece have an attribute x and an attribute y, which represents the coordinates of the piece

    Warning : the origin is on the top left on the board (with the white camp on the bottom)
    The x axis goes downward, the y axis goes to the right
"""


# This functions returns a list of legal plays a piece can make
# It is only used for the Rook, the Bishop and the Queen, since they all can move only through axis
# and they all have an unknown maximum moves
#
# On the other hand, a pawn have at most 4 available moves, a king and a knight all have at most 8
#
#
# Sometime, the king is protected by another piece (meaning that the king would be in check if that piece were to mode)
# In order to see is a move is possible, we have to check if this kind of situation could happen
# the ignore variable is a piece we want to ignore (meaning that we will consider it's case as empty).
#
# If the king is not in check, but it's coordinates are in the available move
# of a piece if a defending piece were to move,
# then this piece cannot move, since it would put it's own king in check
#
# The management of when to ignore or not is made by the "would_be_in_check_if_moved(piece)" function, line 86 of board.py
def legal_plays(x, y, interval, color_moving, board, ignore=None):
    moves = []
    # The interval is a list of directions
    for (a, b) in interval:
        x_temp, y_temp = x, y
        while Pieces.is_in_bounds(x_temp + a, y_temp + b):
            x_temp += a
            y_temp += b
            piece = board[x_temp][y_temp]
            if type(piece) is str or (ignore is not None and piece == ignore):
                moves.append((x_temp, y_temp))
            else:
                if piece.color != color_moving:
                    moves.append((x_temp, y_temp))
                break
    return moves


class Pieces:
    # Returns true if the case (x, y) is on the board
    @staticmethod
    def is_in_bounds(x, y):
        return 0 <= x <= 7 and 0 <= y <= 7

    # Returns true if the case (x, y) is occupied by a piece with the same color as the one in parameters
    @staticmethod
    def in_conflict(x, y, color, board):
        piece = board[x][y]
        return type(piece) is not str and piece.color == color

    class Pawn:
        def __init__(self, color, x, y):
            # color = "WHITE" or "BLACK", so color[0] = W or B, hence the name WP or BP
            self.name = color[0] + "P"
            self.color = color
            self.x = x
            self.y = y
            # If they have not moved, the pawns can move two cases forward
            self.has_moved = False
            # The pawns can only walk to the opposite camp
            self.direction = -1 if self.color == "WHITE" else 1

            if color == "WHITE":
                self.emote = '<:white_pawn:524288295992295424>'
            else:
                self.emote = '<:black_pawn:524288295388053523>'

        # Returns a list of available move, taking into account the other pieces on the board,
        # bot not taking account of the check cases
        # meaning that it wont care if the king is in check or something like that
        def available_moves(self, board):
            is_in_bounds = Pieces.is_in_bounds
            in_conflict = Pieces.in_conflict
            moves = []

            x_dest = self.x + self.direction
            # We check if the pawn can move one case forward
            if is_in_bounds(x_dest, self.y) and not in_conflict(x_dest, self.y, self.color, board):
                moves.append((x_dest, self.y))

                # If it has not moved yet, a pawn is allowed to move 2 cases forward
                # We look at that only if we know it can move one case forward
                if not self.has_moved:
                    x_dest_2 = x_dest + self.direction
                    if is_in_bounds(x_dest_2, self.y) and not in_conflict(x_dest_2, self.y, self.color, board):
                        moves.append((x_dest_2, self.y))

            # The pawn can only take other pieces in diagonal
            y_dest = self.y + 1
            if is_in_bounds(x_dest, y_dest) and type(board[x_dest][y_dest]) is not str and not board[x_dest][y_dest].color == self.color:
                moves.append((x_dest, y_dest))
            y_dest = self.y - 1
            if is_in_bounds(x_dest, y_dest) and type(board[x_dest][y_dest]) is not str and not board[x_dest][y_dest].color == self.color:
                moves.append((x_dest, y_dest))

            return moves

    class Rook:
        def __init__(self, color, x, y):
            # color = "WHITE" or "BLACK", so color[0] = W or B, hence the name WR or BR
            self.name = color[0] + "R"
            self.color = color
            self.x = x
            self.y = y
            # To be able to castle, the rook must not have moved
            self.has_moved = False

            if color == "WHITE":
                self.emote = '<:white_rook:524288296038170634>'
            else:
                self.emote = '<:black_rook:524288295685980166>'

        # Returns a list of available move, taking into account the other pieces on the board,
        # bot not taking account of the check cases
        # meaning that it wont care if the king is in check or something like that
        def available_moves(self, board, ignore=None):
            # interval is the list of all the cardinal directions
            interval = [
                (0, 1),
                (1, 0),
                (0, -1),
                (-1, 0)
            ]
            # This function has been explained line 13 of this file
            return legal_plays(
                self.x,
                self.y,
                interval,
                self.color,
                board,
                ignore
            )

    class Knight:
        def __init__(self, color, x, y):
            # color = "WHITE" or "BLACK", so color[0] = W or B, hence the name WN or BN
            # we do not use K for knight because it is already used for the king
            self.name = color[0] + "N"
            self.color = color
            self.x = x
            self.y = y

            if color == "WHITE":
                self.emote = '<:white_knight:524288295870660619>'
            else:
                self.emote = '<:black_knight:524288295627259916>'

        # Returns a list of available move, taking into account the other pieces on the board,
        # bot not taking account of the check cases
        # meaning that it wont care if the king is in check or something like that
        def available_moves(self, board):
            is_in_bounds = Pieces.is_in_bounds
            in_conflict = Pieces.in_conflict
            # A knight can move 2 cases in one cardinal direction, one case in another
            # and it can jump over other pieces
            interval = [
                (-2, -1),
                (-2, 1),
                (2, -1),
                (2, 1),
                (-1, -2),
                (-1, 2),
                (1, -2),
                (1, 2)
            ]
            x, y = self.x, self.y
            return [
                (x + a, y + b) for (a, b) in interval if is_in_bounds(x + a, y + b) and not in_conflict(x+a, y+b, self.color, board)
            ]

    class Bishop:
        def __init__(self, color, x, y):
            # color = "WHITE" or "BLACK", so color[0] = W or B, hence the name WB or BB
            self.name = color[0] + "B"
            self.color = color
            self.x = x
            self.y = y

            if color == "WHITE":
                self.emote = '<:white_bishop:524288295539310638>'
            else:
                self.emote = '<:black_bishop:524288295308492800>'

        # Returns a list of available move, taking into account the other pieces on the board,
        # bot not taking account of the check cases
        # meaning that it wont care if the king is in check or something like that
        def available_moves(self, board, ignore=None):
            # interval is a list of all the diagonal directions
            interval = [
                (-1, -1),
                (1, -1),
                (-1, 1),
                (1, 1)
            ]
            # This function has been explained line 13 of this file
            return legal_plays(
                self.x,
                self.y,
                interval,
                self.color,
                board,
                ignore
            )

    class Queen:
        def __init__(self, color, x, y):
            # color = "WHITE" or "BLACK", so color[0] = W or B, hence the name WQ or BQ
            self.name = color[0] + "Q"
            self.color = color
            self.x = x
            self.y = y

            if color == "WHITE":
                self.emote = '<:white_queen:524288297564897296>'
            else:
                self.emote = '<:black_queen:524288295694499850>'

        # Returns a list of available move, taking into account the other pieces on the board,
        # bot not taking account of the check cases
        # meaning that it wont care if the king is in check or something like that
        def available_moves(self, board, ignore=None):
            # interval is the list of all the cardinal and diagonal directions
            # i.e. an union of the rook's interval and the bishop's one
            interval = [
                (-1, -1),
                (-1, 0),
                (-1, 1),
                (0, -1),
                (0, 1),
                (1, -1),
                (1, 0),
                (1, 1)
            ]
            # This function has been explained line 13 of this file
            return legal_plays(
                self.x,
                self.y,
                interval,
                self.color,
                board,
                ignore
            )

    class King:
        def __init__(self, color, x, y):
            # color = "WHITE" or "BLACK", so color[0] = W or B, hence the name WK or BK
            self.name = color[0] + "K"
            self.color = color
            self.x = x
            self.y = y
            # Like the rook, the king must not have moved in order to castle
            self.has_moved = False

            if color == "WHITE":
                self.emote = '<:white_king:524288295820066816>'
            else:
                self.emote = '<:black_king:524288295065354251>'

        # Returns a list of available move, taking into account the other pieces on the board,
        # bot not taking account of the check cases
        # meaning that it wont care if the king is in check or something like that
        def available_moves(self, board):
            is_in_bounds = Pieces.is_in_bounds
            in_conflict = Pieces.in_conflict
            # The interval is the same as the queen's
            # The difference being that the king can only move one case in one direction, where the
            # queen can move how many it wants
            interval = [
                (-1, -1),
                (-1, 0),
                (-1, 1),
                (0, -1),
                (0, 1),
                (1, -1),
                (1, 0),
                (1, 1)
            ]
            x, y = self.x, self.y
            return [
                (x + a, y + b) for (a, b) in interval if is_in_bounds(x + a, y + b) and not in_conflict(x + a, y + b, self.color, board)
            ]
