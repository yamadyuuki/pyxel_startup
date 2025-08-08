#250808_pyxel_game.py

import pyxel
import random

SCREEN_WIDTH = 160
SCREEN_HEIGHT = 120
center_x = SCREEN_WIDTH // 2
center_y = SCREEN_HEIGHT // 2
minus_x = SCREEN_WIDTH // 4
plus_x = SCREEN_WIDTH * 3 // 4
number_x = center_x - 6  # 少し左に寄せて中央に見えるように
text_y = center_y
STONE_INTERVAL = 15  # 石が落ちる間隔

class Stone:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def update(self):
        if self.y < SCREEN_HEIGHT:
            self.y += 1
        
        if 0 < self.x <= SCREEN_WIDTH -8:  # 画面外に出ないように
            self.x += random.choice([-2, -1, 0, 1, 2]) #　石に左右の動きをつける
        elif self.x == SCREEN_WIDTH - 8:
            self.x -= random.choice([-2, -1])
        elif self.x == 0:
            self.x += random.choice([1, 2])
    
    def draw(self):
        pyxel.blt(self.x, self.y, 0, 8, 0, 8, 8, pyxel.COLOR_BLACK )


class App:
    def __init__(self):
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="My Game") 
        pyxel.mouse(True)
        self.player_x = SCREEN_WIDTH // 2
        self.player_y = SCREEN_HEIGHT * 4 // 5
        self.stones = []
        self.is_collision = False
        pyxel.load("my_resource.pyxres")
        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()
        
        # 石の生成
        if pyxel.frame_count % STONE_INTERVAL // 2 == 0:
            self.stones.append(Stone( random.randint(0, SCREEN_WIDTH - 8), 0))

        #　石の落下
        for stone in self.stones.copy():
            stone.update()

            # 衝突判定
            if (self.player_x <= stone.x <= self.player_x + 8 and
                self.player_y <= stone.y <= self.player_y +8):
                self.is_collision = True

            if stone.y >= SCREEN_HEIGHT:
                self.stones.remove(stone)

        #人の移動
        if pyxel.btn(pyxel.KEY_RIGHT) and self.player_x < SCREEN_WIDTH - 16:
            self.player_x += 1
        elif pyxel.btn(pyxel.KEY_LEFT) and self.player_x > 0:
            self.player_x -= 1
        

    def draw(self):
        pyxel.cls(pyxel.COLOR_ORANGE)
        # 石
        for stone in self.stones:
            stone.draw()
        # 人
        pyxel.blt(self.player_x, self.player_y, 0, 16, 0, 16, 16, pyxel.COLOR_BLACK )

        if self.is_collision:
            pyxel.text(SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT // 2, "GAME OVER", pyxel.COLOR_RED)



App()  # Create an instance of the App class to run the game