import copy


class Piece:
    def __init__(self, color, position):
        self.color = color
        self.position = position
        self.symbol = None
        self.has_moved = False

    def get_possible_moves(self, board):
        pass

    def get_possible_captures(self, board):
        return self.get_possible_moves(board)

    def __str__(self):
        return self.symbol if self.color == 'white' else self.symbol.lower()


class Pawn(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)
        self.symbol = 'P'

    def get_possible_moves(self, board):
        moves = []
        x, y = self.position
        direction = -1 if self.color == 'white' else 1
        start_row = 6 if self.color == 'white' else 1

        if 0 <= x + direction < 8 and board[x + direction][y] is None:
            moves.append((x + direction, y))
            if x == start_row and board[x + 2 * direction][y] is None:
                moves.append((x + 2 * direction, y))

        for dy in [-1, 1]:
            if 0 <= y + dy < 8 and 0 <= x + direction < 8:
                target = board[x + direction][y + dy]
                if target and target.color != self.color:
                    moves.append((x + direction, y + dy))

        return moves


class Rook(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)
        self.symbol = 'R'

    def get_possible_moves(self, board):
        moves = []
        x, y = self.position
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

        for dx, dy in directions:
            step = 1
            while True:
                nx, ny = x + dx * step, y + dy * step
                if not (0 <= nx < 8 and 0 <= ny < 8):
                    break
                if board[nx][ny] is None:
                    moves.append((nx, ny))
                else:
                    if board[nx][ny].color != self.color:
                        moves.append((nx, ny))
                    break
                step += 1
        return moves


class Knight(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)
        self.symbol = 'N'

    def get_possible_moves(self, board):
        moves = []
        x, y = self.position
        offsets = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]

        for dx, dy in offsets:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 8 and 0 <= ny < 8:
                if board[nx][ny] is None or board[nx][ny].color != self.color:
                    moves.append((nx, ny))
        return moves


class Bishop(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)
        self.symbol = 'B'

    def get_possible_moves(self, board):
        moves = []
        x, y = self.position
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]

        for dx, dy in directions:
            step = 1
            while True:
                nx, ny = x + dx * step, y + dy * step
                if not (0 <= nx < 8 and 0 <= ny < 8):
                    break
                if board[nx][ny] is None:
                    moves.append((nx, ny))
                else:
                    if board[nx][ny].color != self.color:
                        moves.append((nx, ny))
                    break
                step += 1
        return moves


class Queen(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)
        self.symbol = 'Q'

    def get_possible_moves(self, board):
        moves = []
        x, y = self.position
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

        for dx, dy in directions:
            step = 1
            while True:
                nx, ny = x + dx * step, y + dy * step
                if not (0 <= nx < 8 and 0 <= ny < 8):
                    break
                if board[nx][ny] is None:
                    moves.append((nx, ny))
                else:
                    if board[nx][ny].color != self.color:
                        moves.append((nx, ny))
                    break
                step += 1
        return moves


class King(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)
        self.symbol = 'K'

    def get_possible_moves(self, board):
        moves = []
        x, y = self.position
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < 8 and 0 <= ny < 8:
                    if board[nx][ny] is None or board[nx][ny].color != self.color:
                        moves.append((nx, ny))
        return moves


class Move:
    def __init__(self, piece, from_pos, to_pos, captured_piece=None):
        self.piece = piece
        self.from_pos = from_pos
        self.to_pos = to_pos
        self.captured_piece = captured_piece


class Board:
    def __init__(self):
        self.grid = [[None for _ in range(8)] for _ in range(8)]
        self.move_history = []
        self.current_turn = 'white'
        self.check_positions = {'white': False, 'black': False}
        self.setup_pieces()

    def setup_pieces(self):
        for i in range(8):
            self.grid[1][i] = Pawn('black', (1, i))
            self.grid[6][i] = Pawn('white', (6, i))

        pieces = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for i, piece_class in enumerate(pieces):
            self.grid[0][i] = piece_class('black', (0, i))
            self.grid[7][i] = piece_class('white', (7, i))

    def get_piece(self, pos):
        x, y = pos
        return self.grid[x][y]

    def set_piece(self, pos, piece):
        x, y = pos
        self.grid[x][y] = piece
        if piece:
            piece.position = pos

    def is_valid_move(self, piece, from_pos, to_pos):
        if not piece:
            return False
        if piece.color != self.current_turn:
            return False

        possible_moves = piece.get_possible_moves(self.grid)
        if to_pos not in possible_moves:
            return False

        temp_board = copy.deepcopy(self)
        temp_board.make_move_internal(from_pos, to_pos)
        if temp_board.is_check(piece.color):
            return False

        return True

    def make_move_internal(self, from_pos, to_pos):
        piece = self.get_piece(from_pos)
        if not piece:
            return False

        captured = self.get_piece(to_pos)
        self.set_piece(to_pos, piece)
        self.set_piece(from_pos, None)
        piece.has_moved = True
        return captured

    def make_move(self, from_pos, to_pos):
        piece = self.get_piece(from_pos)
        if not piece:
            return False

        if not self.is_valid_move(piece, from_pos, to_pos):
            return False

        captured = self.make_move_internal(from_pos, to_pos)
        move = Move(piece, from_pos, to_pos, captured)
        self.move_history.append(move)

        self.current_turn = 'black' if self.current_turn == 'white' else 'white'
        self.update_check_status()
        return True

    def undo_move(self):
        if not self.move_history:
            return False

        move = self.move_history.pop()
        self.set_piece(move.from_pos, move.piece)
        self.set_piece(move.to_pos, move.captured_piece)
        move.piece.has_moved = False
        move.piece.position = move.from_pos

        self.current_turn = 'black' if self.current_turn == 'white' else 'white'
        self.update_check_status()
        return True

    def undo_moves(self, count):
        for _ in range(count):
            if not self.undo_move():
                return False
        return True

    def is_check(self, color):
        king_pos = None
        for i in range(8):
            for j in range(8):
                piece = self.grid[i][j]
                if piece and piece.symbol == 'K' and piece.color == color:
                    king_pos = (i, j)
                    break
            if king_pos:
                break

        if not king_pos:
            return False

        opponent_color = 'black' if color == 'white' else 'white'
        for i in range(8):
            for j in range(8):
                piece = self.grid[i][j]
                if piece and piece.color == opponent_color:
                    if king_pos in piece.get_possible_moves(self.grid):
                        return True
        return False

    def update_check_status(self):
        self.check_positions['white'] = self.is_check('white')
        self.check_positions['black'] = self.is_check('black')

    def get_threatened_pieces(self, color):
        threatened = []
        opponent_color = 'black' if color == 'white' else 'white'

        for i in range(8):
            for j in range(8):
                piece = self.grid[i][j]
                if piece and piece.color == color:
                    for x in range(8):
                        for y in range(8):
                            opp_piece = self.grid[x][y]
                            if opp_piece and opp_piece.color == opponent_color:
                                if (i, j) in opp_piece.get_possible_moves(self.grid):
                                    threatened.append((i, j))
                                    break
        return threatened

    def get_highlighted_moves(self, pos):
        piece = self.get_piece(pos)
        if not piece or piece.color != self.current_turn:
            return []

        moves = []
        captures = []

        for move in piece.get_possible_moves(self.grid):
            if self.is_valid_move(piece, pos, move):
                if self.get_piece(move):
                    captures.append(move)
                else:
                    moves.append(move)

        return moves, captures

    def display(self, selected_pos=None):
        print("    a   b   c   d   e   f   g   h")
        print("    -----------------------------")
        for i in range(8):
            print(f"{8 - i} ", end=" ")
            for j in range(8):
                piece = self.grid[i][j]
                if selected_pos and (i, j) == selected_pos:
                    print("[", end="")
                    print(str(piece) if piece else " ", end="")
                    print("]", end=" ")
                elif piece:
                    print(f" {str(piece)} ", end=" ")
                else:
                    print(" - ", end=" ")
            print(f" {8 - i}")
        print("    -----------------------------")
        print("    a   b   c   d   e   f   g   h")

        if self.check_positions['white']:
            print("Белые под шахом!")
        if self.check_positions['black']:
            print("Черные под шахом!")


class CheckersPiece(Piece):
    def __init__(self, color, position, is_king=False):
        super().__init__(color, position)
        self.is_king = is_king
        if is_king:
            self.symbol = '⦾' if color == 'white' else '⬤'
        else:
            self.symbol = '●' if color == 'white' else '○'

    def get_possible_moves(self, board):
        moves = []
        x, y = self.position
        direction = -1 if self.color == 'white' else 1

        if self.is_king:
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        else:
            directions = [(direction, -1), (direction, 1)]

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 8 and 0 <= ny < 8:
                if board[nx][ny] is None:
                    moves.append((nx, ny))
                elif board[nx][ny].color != self.color:
                    jump_x, jump_y = nx + dx, ny + dy
                    if 0 <= jump_x < 8 and 0 <= jump_y < 8 and board[jump_x][jump_y] is None:
                        moves.append((jump_x, jump_y))
        return moves


class CheckersBoard(Board):
    def setup_pieces(self):
        for i in range(3):
            for j in range(8):
                if (i + j) % 2 == 1:
                    self.grid[i][j] = CheckersPiece('black', (i, j))

        for i in range(5, 8):
            for j in range(8):
                if (i + j) % 2 == 1:
                    self.grid[i][j] = CheckersPiece('white', (i, j))

    def make_move_internal(self, from_pos, to_pos):
        piece = self.get_piece(from_pos)
        if not piece:
            return False

        captured = None
        x1, y1 = from_pos
        x2, y2 = to_pos

        if abs(x2 - x1) == 2:
            mid_x, mid_y = (x1 + x2) // 2, (y1 + y2) // 2
            captured = self.get_piece((mid_x, mid_y))
            self.set_piece((mid_x, mid_y), None)

        self.set_piece(to_pos, piece)
        self.set_piece(from_pos, None)

        if not piece.is_king:
            if (piece.color == 'white' and to_pos[0] == 0) or (piece.color == 'black' and to_pos[0] == 7):
                piece.is_king = True
                piece.symbol = '⦾' if piece.color == 'white' else '⬤'

        piece.has_moved = True
        return captured


class ChessGame:
    def __init__(self):
        self.board = Board()
        self.selected = None

    def parse_position(self, pos_str):
        if len(pos_str) != 2:
            return None
        col = ord(pos_str[0]) - ord('a')
        row = 8 - int(pos_str[1])
        if 0 <= row < 8 and 0 <= col < 8:
            return (row, col)
        return None

    def run(self):
        print("Шахматы запущены!")
        print("Команды: e2e4, undo, undox, help, exit")

        while True:
            self.board.display(self.selected)

            threatened = self.board.get_threatened_pieces(self.board.current_turn)
            if threatened:
                threatened_pos = [f"{chr(97 + y)}{8 - x}" for x, y in threatened]
                print("Фигуры под боем:", ", ".join(threatened_pos))

            if self.selected:
                moves, captures = self.board.get_highlighted_moves(self.selected)
                if moves or captures:
                    moves_str = [f"{chr(97 + y)}{8 - x}" for x, y in moves]
                    captures_str = [f"{chr(97 + y)}{8 - x}" for x, y in captures]
                    if moves_str:
                        print("Возможные ходы:", ", ".join(moves_str))
                    if captures_str:
                        print("Возможные взятия:", ", ".join(captures_str))

            cmd = input(f"{'Белые' if self.board.current_turn == 'white' else 'Черные'} ходят: ").strip().lower()

            if cmd == "exit":
                break
            elif cmd == "help":
                print(
                    "Команды: e2e4 - сделать ход, undo - отменить последний ход, undox - отменить x ходов, exit - выход")
            elif cmd.startswith("undo"):
                if cmd == "undo":
                    self.board.undo_move()
                elif cmd.startswith("undo"):
                    try:
                        count = int(cmd[4:])
                        self.board.undo_moves(count)
                    except:
                        print("Неверная команда undo")
                self.selected = None
            else:
                if len(cmd) == 4:
                    from_pos = self.parse_position(cmd[:2])
                    to_pos = self.parse_position(cmd[2:])
                    if from_pos and to_pos:
                        if self.board.make_move(from_pos, to_pos):
                            self.selected = None
                        else:
                            print("Неверный ход!")
                    else:
                        print("Неверный формат позиции!")
                elif len(cmd) == 2:
                    pos = self.parse_position(cmd)
                    if pos:
                        piece = self.board.get_piece(pos)
                        if piece and piece.color == self.board.current_turn:
                            self.selected = pos
                        else:
                            print("Неверный выбор!")
                    else:
                        print("Неверная позиция!")
                else:
                    print("Неизвестная команда!")


class CheckersGame:
    def __init__(self):
        self.board = CheckersBoard()
        self.selected = None

    def parse_position(self, pos_str):
        if len(pos_str) != 2:
            return None
        col = ord(pos_str[0]) - ord('a')
        row = 8 - int(pos_str[1])
        if 0 <= row < 8 and 0 <= col < 8:
            return (row, col)
        return None

    def run(self):
        print("Шашки запущены!")
        print("Команды: e2e4, undo, undox, help, exit")
        print("Белые шашки: ⬤, Черные шашки: ○")
        print("Белые дамки: ◉, Черные дамки: ⦾")

        while True:
            self.board.display(self.selected)

            if self.selected:
                moves, captures = self.board.get_highlighted_moves(self.selected)
                if moves or captures:
                    moves_str = [f"{chr(97 + y)}{8 - x}" for x, y in moves]
                    captures_str = [f"{chr(97 + y)}{8 - x}" for x, y in captures]
                    if moves_str:
                        print("Возможные ходы:", ", ".join(moves_str))
                    if captures_str:
                        print("Возможные взятия:", ", ".join(captures_str))

            cmd = input(f"{'Белые' if self.board.current_turn == 'white' else 'Черные'} ходят: ").strip().lower()

            if cmd == "exit":
                break
            elif cmd == "help":
                print(
                    "Команды: e2e4 - сделать ход, undo - отменить последний ход, undox - отменить x ходов, exit - выход")
            elif cmd.startswith("undo"):
                if cmd == "undo":
                    self.board.undo_move()
                elif cmd.startswith("undo"):
                    try:
                        count = int(cmd[4:])
                        self.board.undo_moves(count)
                    except:
                        print("Неверная команда undo")
                self.selected = None
            else:
                if len(cmd) == 4:
                    from_pos = self.parse_position(cmd[:2])
                    to_pos = self.parse_position(cmd[2:])
                    if from_pos and to_pos:
                        if self.board.make_move(from_pos, to_pos):
                            self.selected = None
                        else:
                            print("Неверный ход!")
                    else:
                        print("Неверный формат позиции!")
                elif len(cmd) == 2:
                    pos = self.parse_position(cmd)
                    if pos:
                        piece = self.board.get_piece(pos)
                        if piece and piece.color == self.board.current_turn:
                            self.selected = pos
                        else:
                            print("Неверный выбор!")
                    else:
                        print("Неверная позиция!")
                else:
                    print("Неизвестная команда!")


if __name__ == "__main__":
    print("Выберите игру:")
    print("1. Шахматы")
    print("2. Шашки")
    choice = input("Введите 1 или 2: ")

    if choice == "1":
        game = ChessGame()
        game.run()
    elif choice == "2":
        game = CheckersGame()
        game.run()
    else:
        print("Неверный выбор!")
