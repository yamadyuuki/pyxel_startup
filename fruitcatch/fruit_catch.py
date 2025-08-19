import pyxel
import random

from fruits_constants import *

def rects_intersect(ax, ay, aw, ah, bx, by, bw, bh):
    ah = 1
    return (ax < bx + bw and bx < ax + aw and
            ay < by + bh and by < ay + ah)


class Fruit:
    def __init__(self, kind_dict, x, y):
        self.x = x
        self.y = y
        self.w = kind_dict["w"]
        self.h = kind_dict["h"]
        self.u = kind_dict["u"]
        self.v = kind_dict["v"]
        self.speed = kind_dict["speed"]
        self.random_move = kind_dict["random"]
        self.point = kind_dict["point"]      # ← 追加
        self.name = kind_dict["name"]        # ← 追加        
        # 左右移動の向き（-1 or 1）を適当に決める
        self.hdir = random.choice([-1, 1])        
    def update(self):
        self.y += self.speed
        # 左右ランダム移動タイプだけ、横にも少し動かす
        if self.random_move:
            self.x += self.hdir  # 横1pxずつ
            # たまに向きを反転させる（揺れる感じ）
            if pyxel.rndi(0, 30) == 0:
                self.hdir *= -1
            # 画面端からはみ出ないようクランプ
            self.x = max(0, min(self.x, SCREEN_W - self.w))

    def draw(self):
        pyxel.blt(self.x, self.y, 0, self.u, self.v, self.w, self.h, 0)        

class Player:
    def __init__(self):
        self.x = SCREEN_W / 2
        self.y = SCREEN_H - 30
        self.w = 16
        self.h = 16
        self.score = 0
        self.speed = 2


    def on_catch(self, fruit):
        self.score += fruit.point
                
    def update(self):

        if pyxel.btn(pyxel.KEY_LEFT):
            self.x -= self.speed
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.x += self.speed

        # 画面端での制限
        self.x = max(0, min(self.x, SCREEN_W - self.w))

    def draw(self):
        pyxel.blt(self.x, self.y, 0, 0, 16, self.w, self.h, 0) # プレイヤーを黄色で描画


class App:
    def __init__(self):
        pyxel.init(SCREEN_W, SCREEN_H, title="Fruit catch", fps=60)
        pyxel.load("my_resource.pyxres") # リソースの読み込み
        pyxel.mouse(True)
        self.scene = TITLE_SCENE
        self.player = Player()
        self.fruits = []

        pyxel.run(self.update, self.draw)

    def spawn_fruits_by_interval(self):
        """
        各フルーツ定義の spawn_interval に従って、フレームごとに必要なものだけ生成。
        """
        for kind in FRUITS:
            interval = kind["spawn_interval"]
            if interval > 0 and pyxel.frame_count % interval == 0:
                x = pyxel.rndi(0, SCREEN_W - kind["w"])
                y = -kind["h"]  # 画面上の外から出す
                self.fruits.append(Fruit(kind, x, y))


    def update(self):
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()

        if self.scene == TITLE_SCENE:
            if pyxel.btnp(pyxel.KEY_SPACE):
                self.scene = PLAY_SCENE
                self.player = Player()
                self.fruits = []
        elif self.scene == PLAY_SCENE:
            # スポーン
            self.spawn_fruits_by_interval()
            # プレイヤー
            self.player.update()
            # フルーツ
            for f in self.fruits:
                f.update()
            # 当たり判定
            next_fruits = []
            for f in self.fruits:
                if rects_intersect(self.player.x, self.player.y, self.player.w, self.player.h,
                                   f.x, f.y, f.w, f.h):
                    self.player.on_catch(f)
                elif f.y < SCREEN_H:
                    next_fruits.append(f)
            self.fruits = next_fruits

    def draw_sky(self):
        num_grands = NUM_GRANDS
        grand_height = GRAND_HEIGHT
        grand_start_y = pyxel.height - grand_height*num_grands
        pyxel.cls(5)
        for i in range(num_grands):
            pyxel.dither((i + 1) / num_grands)
            pyxel.rect(
                0,
                grand_start_y + i * grand_height,
                pyxel.width,
                grand_height,
                1
            )
            pyxel.dither(1)

    def draw_points_legend(self):
        """
        画面右上に「[アイコン] : point」を縦に表示する
        """
        margin = 12
        line_h = 10         # 行の高さ（アイコン8px + 余白）
        icon_size = 8

        # 右上から少し内側に配置
        icon_x = 4  # だいたい右寄せ
        text_x = icon_x + icon_size + 2
        y = margin

        for kind in FRUITS:
            # アイコン
            pyxel.blt(icon_x, y, 0, kind["u"], kind["v"], kind["w"], kind["h"], 0)
            # テキスト「: N」
            pyxel.text(text_x, y + 1, f": {kind['point']}", 7)  # 7=白
            y += line_h

    def draw(self):
        pyxel.cls(0)
        if self.scene == TITLE_SCENE:
            pyxel.text(SCREEN_W//2 - 30, SCREEN_H//2 - 10, "FRUIT CATCH", 7)
            pyxel.text(SCREEN_W//2 - 40, SCREEN_H//2 + 10, "PRESS SPACE TO START", 7)
        elif self.scene == PLAY_SCENE:
            self.draw_sky()
            for f in self.fruits:
                f.draw()
            self.player.draw()
            pyxel.text(4, 4, f"SCORE: {int(self.player.score)}", 7)
            self.draw_points_legend()


App()


