# othello.py (UTF-8)
import pyxel

N = 8
EMPTY, BLACK, WHITE = 0, 1, -1

CELL = 20
BOARD_LEFT, BOARD_TOP = 20, 20
BOARD_SIZE = N * CELL

DIR8 = [(-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1)]

def opponent(color:int) -> int:
    return -color

class Board:
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
    def __init__(self):
        self.board = Board()
        self.current = BLACK  # 先手は黒
        self.game_over = False

    def would_flip(self, x, y, color):
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
        moves = set()
        for y in range(N):
            for x in range(N):
                if self.board.get(x, y) == EMPTY and self.would_flip(x, y, color):
                    moves.add((x, y))
        return moves

    def play(self, x, y):
        if self.game_over:
            return
        flips = self.would_flip(x, y, self.current)
        if not flips:
            return
        # 置く＋反転
        self.board.set(x, y, self.current)
        for fx, fy in flips:
            self.board.set(fx, fy, self.current)
        # 手番交代 or パス/終了
        self.current = opponent(self.current)
        if not self.legal_moves(self.current):
            # 相手に合法手なし → 自分に戻す or 両者なし=終局
            self.current = opponent(self.current)
            if not self.legal_moves(self.current):
                self.game_over = True

    def score(self):
        return (self.board.count(BLACK), self.board.count(WHITE))

class App:
    def __init__(self):
        w = BOARD_LEFT*2 + BOARD_SIZE
        h = BOARD_TOP*2 + BOARD_SIZE + 16
        pyxel.init(w, h, title="Pyxel Othello")
        self.game = Game()
        pyxel.mouse(True)
        pyxel.run(self.update, self.draw)

    def mouse_to_grid(self, mx, my):
        gx = (mx - BOARD_LEFT) // CELL
        gy = (my - BOARD_TOP) // CELL
        if 0 <= gx < N and 0 <= gy < N:
            return int(gx), int(gy)
        return None

    def update(self):
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            g = self.mouse_to_grid(pyxel.mouse_x, pyxel.mouse_y)
            if g:
                x, y = g
                self.game.play(x, y)
        # Rでリセット
        if pyxel.btnp(pyxel.KEY_R):
            self.game = Game()

    def draw_board(self):
        # 木目っぽい緑（単色）
        pyxel.rect(BOARD_LEFT-1, BOARD_TOP-1, BOARD_SIZE+2, BOARD_SIZE+2, 3)
        for y in range(N):
            for x in range(N):
                left = BOARD_LEFT + x * CELL
                top  = BOARD_TOP  + y * CELL
                pyxel.rect(left, top, CELL-1, CELL-1, 11)  # マス
        # グリッド線
        for i in range(N+1):
            x = BOARD_LEFT + i*CELL
            y = BOARD_TOP  + i*CELL
            pyxel.line(BOARD_LEFT, y, BOARD_LEFT+BOARD_SIZE, y, 1)
            pyxel.line(x, BOARD_TOP, x, BOARD_TOP+BOARD_SIZE, 1)

    def draw_discs(self):
        for y in range(N):
            for x in range(N):
                v = self.game.board.get(x, y)
                if v == EMPTY:
                    continue
                cx = BOARD_LEFT + x*CELL + CELL//2
                cy = BOARD_TOP  + y*CELL + CELL//2
                r = CELL//2 - 2
                col = 0 if v == BLACK else 7
                pyxel.circ(cx, cy, r, col)

    def draw_hints(self):
        # 合法手に小さな点
        for x, y in self.game.legal_moves(self.game.current):
            cx = BOARD_LEFT + x*CELL + CELL//2
            cy = BOARD_TOP  + y*CELL + CELL//2
            pyxel.circ(cx, cy, 2, 8)

    def draw_ui(self):
        b, w = self.game.score()
        turn = "BLACK" if self.game.current == BLACK else "WHITE"
        pyxel.text(BOARD_LEFT, BOARD_TOP + BOARD_SIZE + 4, f"B:{b}  W:{w}", 7)
        if self.game.game_over:
            msg = "RESULT "
            if b > w: msg += "(BLACK WIN)"
            elif w > b: msg += "(WHITE WIN)"
            else: msg += "(DRAW)"
            pyxel.text(BOARD_LEFT+80, BOARD_TOP + BOARD_SIZE + 4, msg, 10)
        else:
            pyxel.text(BOARD_LEFT+80, BOARD_TOP + BOARD_SIZE + 4, f"TURN: {turn}", 7)
        pyxel.text(BOARD_LEFT+220, BOARD_TOP + BOARD_SIZE + 4, "R: Reset", 5)

    def draw(self):
        pyxel.cls(0)
        self.draw_board()
        self.draw_discs()
        self.draw_hints()
        self.draw_ui()

if __name__ == "__main__":
    App()
