# coding: utf-8
import pyxel
import copy
from abc import ABC, abstractmethod

# --- 定数 ---
N = 8
EMPTY, BLACK, WHITE = 0, 1, -1
DIR8 = [(-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1)]
CELL = 20
BOARD_LEFT, BOARD_TOP = 20, 20
BOARD_SIZE = N * CELL

def opponent(color:int) -> int:
    """相手の色を返す"""
    return -color

# --- 評価関数と評価ボード ---
EVALUATION_BOARD = [
    [120, -20,  20,   5,   5,  20, -20, 120],
    [-20, -40,  -5,  -5,  -5,  -5, -40, -20],
    [ 20,  -5,  15,   3,   3,  15,  -5,  20],
    [  5,  -5,   3,   3,   3,   3,  -5,   5],
    [  5,  -5,   3,   3,   3,   3,  -5,   5],
    [ 20,  -5,  15,   3,   3,  15,  -5,  20],
    [-20, -40,  -5,  -5,  -5,  -5, -40, -20],
    [120, -20,  20,   5,   5,  20, -20, 120],
]

def evaluate(board, color):
    """盤面を評価してスコアを返す"""
    own_score = 0
    opponent_score = 0
    opp_color = opponent(color)
    for y in range(N):
        for x in range(N):
            if board.get(x, y) == color:
                own_score += EVALUATION_BOARD[y][x]
            elif board.get(x, y) == opp_color:
                opponent_score += EVALUATION_BOARD[y][x]
    return own_score - opponent_score

# --- プレイヤーのクラス定義 ---
class Player(ABC):
    """全プレイヤーの共通の機能を持つ基底クラス"""
    def __init__(self, color):
        self.color = color
    @abstractmethod
    def get_move(self, game):
        pass

class HumanPlayer(Player):
    """人間の入力を受け付けるプレイヤークラス"""
    def get_move(self, game):
        return None

class CPUPlayer(Player):
    """評価関数に基づいて手を選択するCPUプレイヤークラス"""
    def get_move(self, game):
        if game.current != self.color:
            return None
        best_score = -float('inf')
        best_move = None
        moves = game.legal_moves(self.color)
        if not moves:
            return None
        best_move = list(moves)[0]
        for x, y in moves:
            temp_game = copy.deepcopy(game)
            temp_game.play(x, y)
            score = evaluate(temp_game.board, self.color)
            if score > best_score:
                best_score = score
                best_move = (x, y)
        return best_move

# --- ゲームロジックのクラス ---
class Board:
    """盤面を管理するクラス"""
    def __init__(self):
        self.cells = [[EMPTY for _ in range(N)] for _ in range(N)]
        self.reset_initial()

    def reset_initial(self):
        for y in range(N):
            for x in range(N):
                self.cells[y][x] = EMPTY
        mid = N // 2
        self.cells[mid-1][mid-1] = WHITE
        self.cells[mid][mid]     = WHITE
        self.cells[mid-1][mid]   = BLACK
        self.cells[mid][mid-1]   = BLACK

    def inside(self, x, y):
        return 0 <= x < N and 0 <= y < N

    def get(self, x, y):
        return self.cells[y][x]

    def set(self, x, y, v):
        self.cells[y][x] = v

    def count(self, color):
        return sum(1 for y in range(N) for x in range(N) if self.cells[y][x] == color)

class Game:
    """ゲーム全体の進行を管理するクラス"""
    def __init__(self, black_player_type, white_player_type):
        self.board = Board()
        self.current = BLACK
        self.game_over = False
        self.history = []
        self.players = {
            BLACK: black_player_type(BLACK),
            WHITE: white_player_type(WHITE)
        }
    
    def would_flip(self, x, y, color):
        if self.board.get(x, y) != EMPTY:
            return []
        flips = []
        for dx, dy in DIR8:
            tmp = []
            cx, cy = x + dx, y + dy
            while self.board.inside(cx, cy) and self.board.get(cx, cy) == opponent(color):
                tmp.append((cx, cy))
                cx += dx; cy += dy
            if self.board.inside(cx, cy) and self.board.get(cx, cy) == color and tmp:
                flips.extend(tmp)
        return flips

    def legal_moves(self, color):
        moves = set()
        for y in range(N):
            for x in range(N):
                if self.board.get(x, y) == EMPTY and self.would_flip(x, y, color):
                    moves.add((x, y))
        return moves

    def play(self, x, y):
        if self.game_over: return
        flips = self.would_flip(x, y, self.current)
        if not flips: return

        snapshot = { "x": x, "y": y, "color": self.current, "flipped": flips[:],
                     "prev_current": self.current, "prev_game_over": self.game_over }
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
        if not self.history: return
        rec = self.history.pop()
        x, y, color, flipped = rec["x"], rec["y"], rec["color"], rec["flipped"]
        self.board.set(x, y, EMPTY)
        rev_color = opponent(color)
        for fx, fy in flipped:
            self.board.set(fx, fy, rev_color)
        self.current = rec["prev_current"]
        self.game_over = rec["prev_game_over"]

    def score(self):
        return (self.board.count(BLACK), self.board.count(WHITE))

# --- Pyxelアプリケーション ---
class App:
    def __init__(self):
        w = BOARD_LEFT*2 + BOARD_SIZE
        h = BOARD_TOP*2 + BOARD_SIZE + 24
        pyxel.init(w, h, title="Pyxel Othello with CPU", fps=30)
        self.reset_game()
        pyxel.mouse(True)
        pyxel.run(self.update, self.draw)

    def reset_game(self):
        # 人間(黒:先手) vs CPU(白:後手) でゲームを開始
        self.game = Game(HumanPlayer, CPUPlayer)
        self.last_cpu_move = None # CPUの最後の着手をリセット

    def mouse_to_grid(self, mx, my):
        gx = (mx - BOARD_LEFT) // CELL
        gy = (my - BOARD_TOP) // CELL
        if 0 <= gx < N and 0 <= gy < N:
            return int(gx), int(gy)
        return None

    def update(self):
        if pyxel.btnp(pyxel.KEY_R):
            self.reset_game()
            return
        
        if pyxel.btnp(pyxel.KEY_Z):
            # 2手分戻す（CPUの手と、その前の自分の手）
            self.game.undo()
            self.game.undo()
            # CPUの着手ハイライトもリセットする
            self.last_cpu_move = None
            return

        if self.game.game_over:
            return

        current_player = self.game.players[self.game.current]

        if isinstance(current_player, CPUPlayer):
            if pyxel.frame_count % 15 == 0:
                move = current_player.get_move(self.game)
                if move: 
                    self.game.play(move[0], move[1])
                    self.last_cpu_move = move # CPUの最後の着手を保存
        
        elif isinstance(current_player, HumanPlayer):
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                g = self.mouse_to_grid(pyxel.mouse_x, pyxel.mouse_y)
                if g and (g in self.game.legal_moves(self.game.current)):
                    self.game.play(g[0], g[1])

    def draw(self):
        pyxel.cls(12)
        self.draw_board()
        self.draw_discs()
        self.draw_last_move_highlight() # CPUの着手ハイライトを追加
        self.draw_hints()
        self.draw_ui()

    def draw_board(self):
        pyxel.rect(BOARD_LEFT-2, BOARD_TOP-2, BOARD_SIZE+4, BOARD_SIZE+4, 1)
        pyxel.rect(BOARD_LEFT, BOARD_TOP, BOARD_SIZE, BOARD_SIZE, 3)
        for i in range(N):
            for j in range(N):
                 pyxel.rectb(BOARD_LEFT + i * CELL, BOARD_TOP + j * CELL, CELL, CELL, 1)

    def draw_discs(self):
        for y in range(N):
            for x in range(N):
                v = self.game.board.get(x, y)
                if v == EMPTY: continue
                cx = BOARD_LEFT + x*CELL + CELL//2
                cy = BOARD_TOP  + y*CELL + CELL//2
                r = CELL//2 - 3
                col = 1 if v == BLACK else 7
                pyxel.circ(cx, cy, r, col)

    def draw_last_move_highlight(self):
        """CPUの最後の着手をハイライト表示する"""
        if self.last_cpu_move:
            x, y = self.last_cpu_move
            cx = BOARD_LEFT + x * CELL + CELL // 2
            cy = BOARD_TOP + y * CELL + CELL // 2
            # 石より少し大きい赤い円を描画 (pyxelカラー8番は赤)
            pyxel.circb(cx, cy, CELL // 2 - 1, 8)

    def draw_hints(self):
        if isinstance(self.game.players[self.game.current], HumanPlayer):
            moves = self.game.legal_moves(self.game.current)
            for x, y in moves:
                cx = BOARD_LEFT + x*CELL + CELL//2
                cy = BOARD_TOP  + y*CELL + CELL//2
                col = 0 if self.game.current == BLACK else 7
                pyxel.circb(cx, cy, CELL//2 - 5, col)

    def draw_ui(self):
        b, w = self.game.score()
        turn_color = "BLACK" if self.game.current == BLACK else "WHITE"
        pyxel.text(BOARD_LEFT, BOARD_TOP + BOARD_SIZE + 5, f"BLACK: {b}  WHITE: {w}", 7)
        msg = ""
        if self.game.game_over:
            if b > w: msg = "BLACK WINS"
            elif w > b: msg = "WHITE WINS"
            else: msg = "DRAW"
        else:
            msg = f"{turn_color}'S TURN"
        pyxel.text(BOARD_LEFT + 100, BOARD_TOP + BOARD_SIZE + 5, msg, 7)
        pyxel.text(BOARD_LEFT, BOARD_TOP + BOARD_SIZE + 15, "Z: Undo  R: Reset", 5)

if __name__ == "__main__":
    App()

