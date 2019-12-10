import copy

from src.modules.game.chess.pieces import *


class Board:
    def __init__(self):
        self.board = [
            [Rook(0, 0, "B"), Knight(0, 1, "B"), Bishop(0, 2, "B"), Queen(0, 3, "B"), King(0, 4, "B"), Bishop(0, 5, "B"), Knight(0, 6, "B"), Rook(0, 7, "B")],
            [Pawn(1, i, "B") for i in range(8)],
            [None] * 8,
            [None] * 8,
            [None] * 8,
            [None] * 8,
            [Pawn(6, i, "W") for i in range(8)],
            [Rook(7, 0, "W"), Knight(7, 1, "W"), Bishop(7, 2, "W"), Queen(7, 3, "W"), King(7, 4, "W"), Bishop(7, 5, "W"), Knight(7, 6, "W"), Rook(7, 7, "W")]
        ]
        self.last_move = None
        self.tmp_board = None

    @staticmethod
    def in_bounds(x, y):
        return 0 <= x <= 7 and 0 <= y <= 7

    def in_conflict(self, x, y, color):
        return self.board[x][y] is not None and self.board[x][y].color == color

    def delete(self, x, y):
        self.board[x][y] = None

    def empty(self, x, y):
        return self.board[x][y] is None

    def move(self, x_start, y_start, x_end, y_end, promotion=None, test=False):
        piece = self.board[x_start][y_start]

        if promotion is not None:
            promotion_pieces = {
                "R": Rook,
                "N": Knight,
                "B": Bishop,
                "Q": Queen
            }
            piece = promotion_pieces[promotion](
                x_end,
                y_end,
                piece.color
            )

        self.board[x_end][y_end] = piece
        self.delete(x_start, y_start)

        if not test:
            self.last_move = {
                "x": x_end,
                "y": y_end,
                "type": type(piece),
                "moved_two_cases": type(piece) is Pawn and abs(x_end - x_start) == 2
            }

    # Used by the pawn to determine if it can move diagonally
    def can_eat(self, x, y, color):
        return self.in_bounds(x, y) and self.board[x][y] is not None and self.board[x][y] != color

    # Determines if a pawn can do "en passant", and returns the move that would cause an "en passant"
    def en_passant(self, x, y):
        piece = self.board[x][y]
        if type(piece) is not Pawn or self.last_move is None:
            return None

        direction = -1 if piece.color == "W" else 1
        if self.last_move["type"] is Pawn and self.last_move["x"] == x and self.last_move["moved_two_cases"]:
            if self.last_move["y"] == y - 1:
                return x + direction, y - 1
            elif self.last_move["y"] == y + 1:
                return x + direction, y + 1
        return None

    def get_king(self, color):
        for line in self.board:
            for piece in line:
                if type(piece) is King and piece.color == color:
                    return piece
        return None

    # Determines if the piece on the case x y is on check by a piece of the color opposed of color
    def on_check(self, x, y, color):
        for line in self.board:
            for piece in line:
                if piece is not None and piece.color != color and (x, y) in piece.legal_moves(self):
                    return True
        return False

    def king_on_check(self, color):
        king = self.get_king(color)
        return self.on_check(king.x, king.y, color)

    # Check if the player is putting themselves in check by moving a piece
    def self_check_by_uncover(self, moving_piece):
        king = self.get_king(moving_piece.color)
        for line in self.board:
            for attacking_piece in line:
                if attacking_piece is not None and attacking_piece.color != moving_piece.color:
                    if type(attacking_piece) in [Rook, Bishop, Queen]:
                        if (king.x, king.y) in attacking_piece.legal_moves(self, ignore=moving_piece):
                            return True
                    else:
                        if (king.x, king.y) in attacking_piece.legal_moves(self):
                            return True
        return False

    def in_check_after_play(self, piece, x_end, y_end):
        self.tmp_board = self.board  # We save the board
        self.board = copy.deepcopy(self.tmp_board)

        tmp_piece = self.board[piece.x][piece.y]

        tmp_piece.move(self, x_end, y_end, test=True)

        in_check = self.king_on_check(piece.color)
        self.board = self.tmp_board
        return in_check

    def has_legal_moves(self, color):
        for line in self.board:
            for piece in line:
                if piece is not None and piece.color == color:
                    moves = piece.legal_moves(self)
                    for(x, y) in moves:
                        if not self.in_check_after_play(piece, x, y):
                            return True
        return False

    # big_castle = True -> queen side castle
    def can_castle(self, color, big_castle):
        (x_king, y_king) = (0 if color == "B" else 7, 4)
        (x_rook, y_rook) = (x_king, 0 if big_castle else 7)

        king = self.board[x_king][y_king]
        rook = self.board[x_rook][y_rook]

        if type(king) is not King or king.has_moved:
            return 1

        if type(rook) is not Rook or rook.has_moved:
            return 2

        if any(not self.empty(x_king, y) for y in range(min(y_king, y_rook) + 1, max(y_king, y_rook))):
            return 3

        # Queen side castle
        if y_king > y_rook:
            if any(self.on_check(x_king, y_king - i, color) for i in range(3)):
                return 4
        else:
            if any(self.on_check(x_king, y_king + i, color) for i in range(3)):
                return 4

        return 0

    def castle(self, color, big_castle):
        (x_king, y_king) = (0 if color == "B" else 7, 4)
        (x_rook, y_rook) = (x_king, 0 if big_castle else 7)

        # can_castle returns 0 if it can, anything else is an error code
        if self.can_castle(color, big_castle) == 0:
            if big_castle:
                self.board[x_rook][y_rook].move(self, x_king, y_king - 1)
                self.board[x_king][y_king].move(self, x_king, y_king - 2)
            else:
                self.board[x_rook][y_rook].move(self, x_king, y_king + 1)
                self.board[x_king][y_king].move(self, x_king, y_king + 2)

    def checkmate(self, color):
        return self.king_on_check(color) and not self.has_legal_moves(color)

    def lack_of_material(self):
        for line in self.board:
            for piece in line:
                if piece is not None and type(piece) is not King:
                    return False
        return True

    def status(self):
        colors = ["W", "B"]
        for color in colors:
            if not self.has_legal_moves(color):
                if self.king_on_check(color):
                    # This color lost
                    return color
                else:
                    return "STALEMATE"
        if self.lack_of_material():
            return "DRAW"
        return None
