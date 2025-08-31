# coding: utf-8

# --- 定数 ---
N = 8
EMPTY, BLACK, WHITE = 0, 1, -1
DIR8 = [(-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1)]

def opponent(color:int) -> int:
    """相手の色を返す"""
    return -color

class Board:
    """盤面を管理するクラス"""
    def __init__(self):
        self.cells = [[EMPTY for _ in range(N)] for _ in range(N)]
        self.reset_initial()

    def reset_initial(self):
        """盤面を初期配置にリセットする"""
        for y in range(N):
            for x in range(N):
                self.cells[y][x] = EMPTY
        mid = N // 2
        self.cells[mid-1][mid-1] = WHITE
        self.cells[mid][mid]     = WHITE
        self.cells[mid-1][mid]   = BLACK
        self.cells[mid][mid-1]   = BLACK

    def inside(self, x, y):
        """(x, y)が盤面の内側か判定する"""
        return 0 <= x < N and 0 <= y < N

    def get(self, x, y):
        """(x, y)の石の色を取得する"""
        return self.cells[y][x]

    def set(self, x, y, v):
        """(x, y)に石を置く"""
        self.cells[y][x] = v

    def count(self, color):
        """指定された色の石の数を数える"""
        return sum(1 for y in range(N) for x in range(N) if self.cells[y][x] == color)

class Game:
    """ゲーム全体の進行を管理するクラス"""
    def __init__(self, black_player_type, white_player_type):
        self.board = Board()
        self.current = BLACK
        self.game_over = False
        self.history = []

        # Playerクラスの型を受け取り、インスタンスを生成して保持する
        self.players = {
            BLACK: black_player_type(BLACK),
            WHITE: white_player_type(WHITE)
        }
    
    def would_flip(self, x, y, color):
        """(x, y)に石を置いた場合に裏返る相手の石のリストを返す"""
        if self.board.get(x, y) != EMPTY:
            return []
        flips = []
        for dx, dy in DIR8:
            tmp = []
            cx, cy = x + dx, y + dy
            while self.board.inside(cx, cy) and self.board.get(cx, cy) == opponent(color):
                tmp.append((cx, cy))
                cx += dx
                cy += dy
            if self.board.inside(cx, cy) and self.board.get(cx, cy) == color and tmp:
                flips.extend(tmp)
        return flips

    def legal_moves(self, color):
        """指定された色にとっての合法手のリストを返す"""
        moves = set()
        for y in range(N):
            for x in range(N):
                if self.board.get(x, y) == EMPTY and self.would_flip(x, y, color):
                    moves.add((x, y))
        return moves

    def play(self, x, y):
        """(x, y)に石を置き、手番を進める"""
        if self.game_over:
            return
        flips = self.would_flip(x, y, self.current)
        if not flips:
            return

        snapshot = {
            "x": x, "y": y, "color": self.current,
            "flipped": flips[:],
            "prev_current": self.current,
            "prev_game_over": self.game_over,
        }
        self.history.append(snapshot)

        self.board.set(x, y, self.current)
        for fx, fy in flips:
            self.board.set(fx, fy, self.current)

        self.current = opponent(self.current)
        if not self.legal_moves(self.current):
            self.current = opponent(self.current)
            if not self.legal_moves(self.current):
                self.game_over = True

    def undo(self):
        """直前の1手を取り消す"""
        if not self.history:
            return
        rec = self.history.pop()

        x, y = rec["x"], rec["y"]
        color = rec["color"]
        self.board.set(x, y, EMPTY)
        rev_color = opponent(color)
        for fx, fy in rec["flipped"]:
            self.board.set(fx, fy, rev_color)

        self.current = rec["prev_current"]
        self.game_over = rec["prev_game_over"]

    def score(self):
        """現在のスコアを (黒, 白) のタプルで返す"""
        return (self.board.count(BLACK), self.board.count(WHITE))

