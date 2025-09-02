# coding: utf-8
import pyxel
from game_logic import Game, N, EMPTY, BLACK, WHITE
# 新しいCPUクラスもインポートする
from players import HumanPlayer, CPUPlayer, SearchCPUPlayer, MCTSCPUPlayer

# --- UI定数 ---
CELL = 20
BOARD_LEFT, BOARD_TOP = 20, 20
BOARD_SIZE = N * CELL

# --- シーン管理用定数 ---
SCENE_START = 0
SCENE_GAME = 1

class App:
    """Pyxelアプリケーション全体を管理するクラス"""
    def __init__(self):
        w = BOARD_LEFT*2 + BOARD_SIZE
        h = BOARD_TOP*2 + BOARD_SIZE + 24
        pyxel.init(w, h, title="Pyxel Othello", fps=30)
        
        # --- シーンとメニューの初期設定 ---
        self.scene = SCENE_START
        self.game = None # ゲームはまだ始まっていないのでNone
        self.difficulties = ["HARD", "VERY HARD", "LUNATIC"]
        self.cpu_types = [CPUPlayer, SearchCPUPlayer, MCTSCPUPlayer]
        self.selected_index = 0
        
        # CPU思考状態管理用フラグ
        self.cpu_thinking = False
        
        pyxel.mouse(True)
        pyxel.run(self.update, self.draw)

    def start_game(self):
        """選択された難易度でゲームを開始する"""
        cpu_player_class = self.cpu_types[self.selected_index]
        self.game = Game(HumanPlayer, cpu_player_class) # 人間 vs 選択されたCPU
        self.last_cpu_move = None
        self.cpu_thinking = False  # 思考状態をリセット
        self.scene = SCENE_GAME # シーンをゲーム画面に切り替え

    # --- update系メソッド ---
    def update(self):
        """毎フレームの更新処理をシーンに応じて振り分ける"""
        if self.scene == SCENE_START:
            self.update_start_screen()
        elif self.scene == SCENE_GAME:
            self.update_game()

    def update_start_screen(self):
        """スタート画面の更新処理"""
        # ↓キーで選択項目を下に
        if pyxel.btnp(pyxel.KEY_DOWN):
            self.selected_index = (self.selected_index + 1) % len(self.difficulties)
        # ↑キーで選択項目を上に
        if pyxel.btnp(pyxel.KEY_UP):
            self.selected_index = (self.selected_index - 1 + len(self.difficulties)) % len(self.difficulties)
        # SpaceキーかZキーでゲーム開始
        if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_Z):
            self.start_game()

    def update_game(self):
        """ゲーム画面の更新処理"""
        # Rキーでタイトルに戻る
        if pyxel.btnp(pyxel.KEY_R):
            self.scene = SCENE_START
            self.cpu_thinking = False  # 思考状態をリセット
            return
        
        if pyxel.btnp(pyxel.KEY_Z):
            # CPUが思考中の場合は取り消し操作を無効化
            if not self.cpu_thinking:
                self.game.undo()
                self.game.undo()
                self.last_cpu_move = None
            return

        if self.game.game_over:
            return

        current_player = self.game.players[self.game.current]

        if not isinstance(current_player, HumanPlayer):
            # 重要な修正：CPUが既に思考中でない場合のみ新しい思考を開始
            if not self.cpu_thinking:
                # 思考開始をマーク
                self.cpu_thinking = True
                
                # CPUに手を考えさせる
                move = current_player.get_move(self.game)
                
                # 手があれば実行
                if move:
                    self.game.play(move[0], move[1])
                    self.last_cpu_move = move
                
                # 思考完了をマーク
                self.cpu_thinking = False
        
        elif isinstance(current_player, HumanPlayer):
            # 人間のターンではCPU思考フラグをリセット
            self.cpu_thinking = False
            
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                g = self.mouse_to_grid(pyxel.mouse_x, pyxel.mouse_y)
                if g and (g in self.game.legal_moves(self.game.current)):
                    self.game.play(g[0], g[1])

    # --- draw系メソッド ---
    def draw(self):
        """毎フレームの描画処理をシーンに応じて振り分ける"""
        pyxel.cls(12)
        if self.scene == SCENE_START:
            self.draw_start_screen()
        elif self.scene == SCENE_GAME and self.game:
            self.draw_board()
            self.draw_discs()
            self.draw_last_move_highlight()
            self.draw_hints()
            self.draw_ui()

    def draw_start_screen(self):
        """スタート画面の描画処理"""
        pyxel.cls(0)
        pyxel.text(70, 50, "PYXEL OTHELLO", pyxel.frame_count % 16)
        pyxel.text(65, 80, "SELECT DIFFICULTY", 7)
        
        for i, diff in enumerate(self.difficulties):
            col = 15
            if i == self.selected_index:
                col = 12 # 選択されている項目をハイライト
                pyxel.text(70, 100 + i * 15, ">", col)
            
            pyxel.text(80, 100 + i * 15, diff, col)

        pyxel.text(55, 180, "UP/DOWN: SELECT", 5)
        pyxel.text(55, 190, "SPACE/Z: START", 5)

    def mouse_to_grid(self, mx, my):
        gx = (mx - BOARD_LEFT) // CELL
        gy = (my - BOARD_TOP) // CELL
        if 0 <= gx < N and 0 <= gy < N:
            return int(gx), int(gy)
        return None

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
        if self.last_cpu_move:
            x, y = self.last_cpu_move
            cx = BOARD_LEFT + x * CELL + CELL // 2
            cy = BOARD_TOP + y * CELL + CELL // 2
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
            if self.cpu_thinking:
                msg = "CPU THINKING..."
            else:
                msg = f"{turn_color}'S TURN"
        pyxel.text(BOARD_LEFT + 100, BOARD_TOP + BOARD_SIZE + 5, msg, 7)
        pyxel.text(BOARD_LEFT, BOARD_TOP + BOARD_SIZE + 15, "R: Back to Title  Z: Undo", 5)

if __name__ == "__main__":
    App()