import pyxel
from constants import *

class App:
    def __init__(self):
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="bullet hell", fps=60)
        pyxel.mouse(True)
        pyxel.load("my_resource.pyxres")  # ← これを追加（spriteを使うなら必須）        

        self.scene = START_SCENE
        self.selected_level = None
        self.game = None  # ← 最初はNoneにする
        self.menu_idx = 0

        pyxel.run(self.update, self.draw)


    def update(self):
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()

        if self.scene == START_SCENE:
            self.update_start_scene()
        elif self.scene == PLAY_SCENE and self.game:      # ← 追加
            self.game.update()                            # ← 追加

    def draw(self):
        if self.scene == START_SCENE:
            self.draw_start_scene()
        elif self.scene == PLAY_SCENE:
            self.game.draw()
        elif self.scene == END_SCENE:
            self.draw_end_scene()
            
    #---update---
    def update_start_scene(self):
        # ---- キーボード操作（上下＋決定）----
        if pyxel.btnp(pyxel.KEY_UP):
            self.menu_idx = (self.menu_idx - 1) % 3
            pyxel.play(0, 0)
        if pyxel.btnp(pyxel.KEY_DOWN):
            self.menu_idx = (self.menu_idx + 1) % 3
            pyxel.play(0, 0)
        if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_RETURN):
            level_name = ("EASY", "NORMAL", "HARD")[self.menu_idx]
            self.start_game(level_name)
            pyxel.play(0, 0)

        # ---- マウスクリック操作 ----
        if pyxel.btnp(0):
            mx, my = pyxel.mouse_x, pyxel.mouse_y
            # クリック位置から選択＆即開始
            if 100 <= mx <= 160 and 80 <= my <= 90:
                self.menu_idx = 0
                self.start_game("EASY")
            elif 100 <= mx <= 160 and 100 <= my <= 110:
                self.menu_idx = 1
                self.start_game("NORMAL")
            elif 100 <= mx <= 160 and 120 <= my <= 130:
                self.menu_idx = 2
                self.start_game("HARD")


    def start_game(self, level_name):
        self.selected_level = LEVELS[level_name]
        self.game = Game(self.selected_level)
        self.scene = PLAY_SCENE


#---draw---
    def draw_start_scene(self):
        pyxel.cls(5)
        pyxel.text(96, 50, "SELECT LEVEL", 7)

        items = [("EASY", 11), ("NORMAL", 10), ("HARD", 8)]
        ys = [80, 100, 120]

        for i, ((label, col), y) in enumerate(zip(items, ys)):
            # 選択中行にカーソル（>）表示＆うっすら背景
            if i == self.menu_idx:
                pyxel.rect(92, y - 2, 80, 12, 1)     # 薄背景
                pyxel.text(92, y, ">", 7)            # カーソル
            pyxel.text(100, y, label, col)

    def draw_end_scene(self):
        pyxel.cls(5)
        pyxel.text(100, 100, "END", 7)

class Game:
    def __init__(self, level_config):
        self.level = level_config
        self.player = Player()
    def update(self):
        self.player.update()
    def draw(self):
        pyxel.cls(5)
        pyxel.text(50, 50, f"LEVEL: {self.level}", 7)
        self.player.draw()

class Player:
    def __init__(self):
        self.x = SCREEN_WIDTH / 2
        self.y = SCREEN_HEIGHT - 16
        self.speed = 1  # 少し上げてもOK

    def update(self):
        dx = (1 if pyxel.btn(pyxel.KEY_RIGHT) else 0) - (1 if pyxel.btn(pyxel.KEY_LEFT) else 0)
        dy = (1 if pyxel.btn(pyxel.KEY_DOWN)  else 0) - (1 if pyxel.btn(pyxel.KEY_UP)   else 0)

        # 正規化（斜めでも等速）
        if dx or dy:
            mag = (dx*dx + dy*dy) ** 0.5
            self.x += (dx / mag) * self.speed
            self.y += (dy / mag) * self.speed

        # 画面内に収める（8x8）
        self.x = max(0, min(self.x, SCREEN_WIDTH - 8))
        self.y = max(0, min(self.y, SCREEN_HEIGHT - 8))

    def draw(self):
        pyxel.blt(int(self.x), int(self.y), 0, 8, 0, 8, 8, 0)

class Enemy:
    def __init__(self):
        self.x = 0
        self.y = 0

    def update(self):
        pass
    def draw(self):
        pyxel.blt(int(self.x), int(self.y), 0, 0, 8, 8, 8, 0)




App()

