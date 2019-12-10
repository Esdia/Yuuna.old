"""
    This module is used to manage the pieces

    WARNING :
    The functions here that give a list of the legal moves DO NOT check if doing the move would
    put your own king in check, this verification is done in the Board class
"""


class Pieces:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color

    """
        directions is a list of directions
        e.g : [(0,1), (0,-1), (1,0), (-1, 0)] describes the four horizontal directions
    """

    def moves_list(self, board, directions, ignore=None):
        moves = []
        for (a, b) in directions:
            (x, y) = (self.x + a, self.y + b)
            while board.in_bounds(x, y) and not board.in_conflict(x, y, self.color):
                moves.append((x, y))
                if not board.empty(x, y) and (ignore is None or board.board[x][y] != ignore):
                    break
                (x, y) = (x + a, y + b)
        return moves

    def move(self, board, x, y, promotion=None, test=False):
        board.move(self.x, self.y, x, y, promotion, test)
        self.x = x
        self.y = y


class Pawn(Pieces):
    def __init__(self, x, y, color):
        super().__init__(x, y, color)
        self.has_moved = False
        if color == "W":
            self.emote = '<:white_pawn:524288295992295424>'
        else:
            self.emote = '<:black_pawn:524288295388053523>'

    def legal_moves(self, board):
        moves = []
        # A white piece goes up the board (toward x=0), a black piece goes downward (toward x=7)
        direction = -1 if self.color == "W" else 1

        # If the pawn can eat regularly to the left of the board
        if board.can_eat(self.x + direction, self.y - 1, self.color):
            moves.append((self.x + direction, self.y - 1))
        # If the pawn can eat regularly to the right of the board
        if board.can_eat(self.x + direction, self.y + 1, self.color):
            moves.append((self.x + direction, self.y + 1))

        # If the pawn can move forward
        if board.empty(self.x + direction, self.y):
            moves.append((self.x + direction, self.y))
            if board.empty(self.x + 2*direction, self.y) and not self.has_moved:
                moves.append((self.x + 2 * direction, self.y))

        en_passant = board.en_passant(self.x, self.y)
        if en_passant is not None:
            moves.append(en_passant)

        return moves

    def move(self, board, x, y, promotion=None, test=False):
        self.has_moved = True
        if (x, y) == board.en_passant(self.x, self.y):
            direction = 1 if self.color == "W" else -1
            board.delete(x+direction, y)
        super().move(board, x, y, promotion, test)


class Rook(Pieces):
    def __init__(self, x, y, color):
        super().__init__(x, y, color)
        self.has_moved = False
        if color == "W":
            self.emote = '<:white_rook:524288296038170634>'
        else:
            self.emote = '<:black_rook:524288295685980166>'

    def legal_moves(self, board, ignore=None):
        return super().moves_list(
            board,
            [(0, 1), (0, -1), (1, 0), (-1, 0)],
            ignore
        )

    def move(self, board, x, y, promotion=None, test=False):
        self.has_moved = True
        super().move(board, x, y, test=test)


class Knight(Pieces):
    def __init__(self, x, y, color):
        super().__init__(x, y, color)
        if color == "W":
            self.emote = '<:white_knight:524288295870660619>'
        else:
            self.emote = '<:black_knight:524288295627259916>'

    def legal_moves(self, board):
        moves = []
        directions = [(1, 2), (1, -2), (-1, 2), (-1, -2), (2, 1), (2, -1), (-2, 1), (-2, -1)]
        for (a, b) in directions:
            if board.in_bounds(self.x + a, self.y + b) and not board.in_conflict(self.x + a, self.y + b, self.color):
                moves.append((self.x + a, self.y + b))
        return moves


class Bishop(Pieces):
    def __init__(self, x, y, color):
        super().__init__(x, y, color)
        if color == "W":
            self.emote = '<:white_bishop:524288295539310638>'
        else:
            self.emote = '<:black_bishop:524288295308492800>'

    def legal_moves(self, board, ignore=None):
        return super().moves_list(
            board,
            [(1, 1), (-1, -1), (1, -1), (-1, 1)],
            ignore
        )


class Queen(Rook, Bishop):
    def __init__(self, x, y, color):
        Bishop.__init__(self, x, y, color)  # We use Bishop's init because we do not want the 'has_moved' attribute the rook has
        if color == "W":
            self.emote = '<:white_queen:524288297564897296>'
        else:
            self.emote = '<:black_queen:524288295694499850>'

    def legal_moves(self, board, ignore=None):
        moves = Rook.legal_moves(self, board, ignore)
        moves.extend(
            Bishop.legal_moves(self, board, ignore)
        )
        return moves


class King(Pieces):
    def __init__(self, x, y, color):
        super().__init__(x, y, color)
        self.has_moved = False
        if color == "W":
            self.emote = '<:white_king:524288295820066816>'
        else:
            self.emote = '<:black_king:524288295065354251>'

    def legal_moves(self, board):
        moves = []
        directions = [(1, 1), (-1, -1), (1, -1), (-1, 1), (0, 1), (0, -1), (1, 0), (-1, 0)]
        for (a, b) in directions:
            if board.in_bounds(self.x + a, self.y + b) and not board.in_conflict(self.x + a, self.y + b, self.color):
                moves.append((self.x + a, self.y + b))
        return moves

    def move(self, board, x, y, promotion=None, test=False):
        self.has_moved = True
        super().move(board, x, y, test=test)
