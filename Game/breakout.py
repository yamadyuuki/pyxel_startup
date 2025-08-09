import pyxel

SCREEN_W = 160
SCREEN_H = 120
BALL_SPEED = 2
BALL_SPEED_UP = 0.05

BLOOK_TYPE = [
    {"hp": 1, "color": 8},
    {"hp": 2, "color": 10},
    {"hp": 3, "color": 11}
]

BLOOK_W = 16
BLOOK_H = 8
BLOOK_MARGIN_X = 0
BLOOK_MARGIN_Y = 2

BLOCK_COLS = SCREEN_W // BLOOK_W      # 10列（160/16）
BLOCK_ROWS = 5                        # 行数は好みで
BLOCK_TOP = 12

START_SCENE = 0
PLAY_SCENE = 1
PAUSE_SCENE = 2

# パドルの設定
PADDLE_W = 24      # 板の幅
PADDLE_H = 4       # 板の高さ
PADDLE_SPEED = 3   # 板の移動速度

class App:
    def __init__(self):
        pyxel.init(SCREEN_W, SCREEN_H, title="Breakout Game", fps=30)
        pyxel.load("my_resource.pyxres") # リソースの読み込み
        self.jp_font = pyxel.Font("umplus_j10r.bdf") # 日本語フォントの読み込み
        self.init_game()
        pyxel.run(self.update, self.draw)

    def init_game(self):
        self.current_scene = START_SCENE

        #パドルの初期化
        self.paddle_x = (SCREEN_W - PADDLE_W) // 2
        self.paddle_y = SCREEN_H - PADDLE_H - 8


    def update(self):
        if pyxel.btnp(pyxel.KEY_ESCAPE):
             pyxel.quit()
        if self.current_scene == START_SCENE:
            self.update_start_scene()
        elif self.current_scene == PLAY_SCENE:
            self.update_play_scene()
        elif self.current_scene == PAUSE_SCENE:
            self.update_pause_scene()

    def update_start_scene(self):
        """スタートシーンの更新"""
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.current_scene = PLAY_SCENE

    def update_play_scene(self):
        """プレイシーンの更新"""
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.current_scene = PAUSE_SCENE
        # パドルの更新処理を呼び出し
        self.update_paddle()

    def update_pause_scene(self):
        """ポーズシーンの更新"""
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.current_scene = PLAY_SCENE

    # パドルの更新
    def update_paddle(self):
         if pyxel.btn(pyxel.KEY_RIGHT) and self.paddle_x < SCREEN_W -PADDLE_W - BLOOK_MARGIN_X:
            self.paddle_x += PADDLE_SPEED
         if pyxel.btn(pyxel.KEY_LEFT) and self.paddle_x > BLOOK_MARGIN_X:
            self.paddle_x -= PADDLE_SPEED


    def draw(self):
        if self.current_scene == START_SCENE:
            self.draw_start_scene()
        elif self.current_scene == PLAY_SCENE:
            self.draw_play_scene()
        elif self.current_scene == PAUSE_SCENE:
            self.draw_pause_scene()
    
    def draw_start_scene(self): # スタートシーンの描画
        pyxel.cls(pyxel.COLOR_NAVY)
        pyxel.text(SCREEN_W // 2 - 30, SCREEN_H // 2 - 10, "BREAKOUT GAME", pyxel.COLOR_WHITE)
        pyxel.text(SCREEN_W // 2 - 35, SCREEN_H // 2 + 10, "Press SPACE to start", pyxel.COLOR_WHITE)

    def draw_play_scene(self): # プレイシーンの描画
          pyxel.cls(pyxel.COLOR_CYAN)
          self.draw_paddle()

    def draw_pause_scene(self): # ポーズシーンの描画
            pyxel.cls(pyxel.COLOR_GRAY)
            pyxel.text(SCREEN_W // 2 - 20, SCREEN_H // 2, "PAUSED", pyxel.COLOR_WHITE)
            pyxel.text(SCREEN_W // 2 - 30, SCREEN_H // 2 + 10, "Press SPACE to continue", pyxel.COLOR_WHITE)

    # 板の描画
    def draw_paddle(self):
        """板の描画"""
        # 単色の矩形で板を描画
        pyxel.rect(self.paddle_x, self.paddle_y, PADDLE_W, PADDLE_H, pyxel.COLOR_WHITE)
        # より見た目を良くしたい場合は、枠線を追加
        pyxel.rectb(self.paddle_x, self.paddle_y, PADDLE_W, PADDLE_H, pyxel.COLOR_GRAY)    

App()