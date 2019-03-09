from src.modules.game.chess.pieces import Pieces
import copy

"""
    This module manages the board
    every board-related function is in there
"""


class Board:
    def __init__(self, players, message):
        self.board = self.create_board()
        self.players = players
        self.message = message

    @staticmethod
    def create_board():
        # Seen from the white side, a back line in chess initially looks like that
        pieces = [
            (Pieces.Rook, 0),
            (Pieces.Knight, 1),
            (Pieces.Bishop, 2),
            (Pieces.Queen, 3),
            (Pieces.King, 4),
            (Pieces.Bishop, 5),
            (Pieces.Knight, 6),
            (Pieces.Rook, 7)
        ]

        black_back = [
            P("BLACK", 0, i) for (P, i) in pieces
        ]
        black_pawns = [
            Pieces.Pawn("BLACK", 1, i) for i in range(8)
        ]

        empty_line = [
            ".." for _ in range(8)
        ]

        white_pawns = [
            Pieces.Pawn("WHITE", 6, i) for i in range(8)
        ]
        white_back = [
            P("WHITE", 7, i) for (P, i) in pieces
        ]

        board = [
            black_back,
            black_pawns,
            empty_line.copy(),
            empty_line.copy(),
            empty_line.copy(),
            empty_line.copy(),
            white_pawns,
            white_back
        ]
        return board

    # This functions returns the piece that represent the King of the specified color
    def get_king(self, color):
        board = self.board
        for line in board:
            for piece in line:
                if type(piece) is Pieces.King and piece.color == color:
                    return piece
        return None

    # color = target to check : check if piece is targeted by the other color
    # when x, y none, we check if the king of said color is in check, otherwise we check the case at the coordinates x,y
    # i.e. if x is None, so is y.
    # warning : x : vertical axis, y: horizontal axis
    def in_check(self, color, x=None, y=None, board=None):
        board = self.board if board is None else board
        if x is None:
            king = self.get_king(color)
            x = king.x
            y = king.y

        for line in board:
            for piece in line:
                # We successively check if : there is a piece there, the piece is of the opposite color, and the piece can target our piece
                if type(piece) is not str and piece.color != color and (x, y) in piece.available_moves(board):
                    return True

        return False

    # If a player move a piece, would they put themselves in check ?
    def would_be_in_check_if_moved(self, piece):
        color = piece.color
        king = self.get_king(color)
        x = king.x
        y = king.y

        for line in self.board:
            # I usually use "piece" there, but I use attacking_piece because piece is already a parameter of this function
            for attacking_piece in line:
                if type(attacking_piece) is not str and attacking_piece.color != piece.color:
                    if type(attacking_piece) in [Pieces.Rook, Pieces.Bishop, Pieces.Queen]:
                        # Rook, Bishop and Queen are the only pieces that can be blocked by another one.
                        # By saying "ignore that piece", we will get the available moves the attacking piece would have if the moving piece was not there
                        if (x, y) in attacking_piece.available_moves(self.board, ignore=piece):
                            return True
                    else:
                        # The other pieces cannot be blocked, so we have no need to tell them to ignore our piece
                        if (x, y) in attacking_piece.available_moves(self.board):
                            return True
        return False

    # returns True if the player of the given color has a legal move (i.e. a move that would not put the player in check)
    def has_legal_moves(self, color):
        for line in self.board:
            for piece in line:
                if type(piece) is not str and piece.color == color:
                    moves = piece.available_moves(self.board)
                    if len(moves) > 0 and not self.would_be_in_check_if_moved(piece):
                        return True
        return False

    # In chess, it is said that there is a lack of material if there are only kings on the board
    # In this case, a draw is declared
    def lack_of_material(self):
        for line in self.board:
            for piece in line:
                if type(piece) not in [Pieces.King, str]:
                    return False
        return True

    # Return True if the king would still be in check after a play:
    # it was in check before
    def in_check_after_play(self, color, x_start, y_start, x_end, y_end):
        board = []
        for line in self.board:
            board.append(copy.deepcopy(line))

        self.play_move(x_start, y_start, x_end, y_end, board=board)
        return self.in_check(color, board)

    # Returns the status of the game
    # A checkmate is when the player is in check, and they have no legal moves
    # A stalemate is when the player is not in check, and they have no legal moves (it is considered as a draw)
    # When there is a lack of material, the game is a draw
    # If we have none of the situations above, the game can freely continue
    def status(self):
        colors = [
            "WHITE",
            "BLACK"
        ]
        for color in colors:
            if not self.has_legal_moves(color):
                if self.in_check(color):
                    return color
                else:
                    return "STALEMATE"
        if self.lack_of_material():
            return "DRAW"
        return "NONE"

    # Given the coordinates of a piece, and the coordinates where the piece want to go, this function apply the move
    def play_move(self, x_start, y_start, x_end, y_end, promotion=None, board=None):
        board = self.board if board is None else board
        piece = board[x_start][y_start]

        if promotion is not None:
            promotion_pieces = {
                "R": Pieces.Rook,
                "N": Pieces.Knight,
                "B": Pieces.Bishop,
                "Q": Pieces.Queen
            }
            piece = promotion_pieces[promotion](
                piece.color,
                x_start,
                y_start
            )

        # These three pieces have different behaviors if they have not moved :
        # The pawn is allowed to move to cases in one turn
        # The king and the rook are allowed to castle
        if type(piece) in [Pieces.King, Pieces.Rook, Pieces.Pawn]:
            piece.has_moved = True

        board[x_start][y_start] = ".."
        board[x_end][y_end] = piece

        piece.x = x_end
        piece.y = y_end

    # This function returns a printable reading-friendly character string representing the board
    def get_printable(self):
        printable = ""
        print_board = []
        for x in range(len(self.board)):
            line = []
            for y in range(len(self.board[x])):
                piece = self.board[x][y]
                if type(piece) is not str:
                    line.append(piece.name)
                else:
                    line.append(piece)
            print_board.append(line)

        for line in print_board:
            printable += "{}\n".format(
                " | ".join(
                    line
                )
            )

        return printable
