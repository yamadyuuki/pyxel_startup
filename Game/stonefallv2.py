
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
STONE_INTERVAL = 7.5  # 石が落ちる間隔 (0.25秒ごとに2つ落ちる)
GAME_OVER_DISPLAY_TIME = 60 # 60フレーム (2秒) ゲームオーバー表示時間
START_SCENE = "start"
PLAY_SCENE = "play"


#石に関する挙動
class Stone:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def update(self):
        if self.y < SCREEN_HEIGHT:
            self.y += 1
        
        if 0 < self.x < SCREEN_WIDTH -8:  # 画面外に出ないように
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
        self.game_over_display_timer = GAME_OVER_DISPLAY_TIME  # ゲームオーバー表示時間
        pyxel.load("my_resource.pyxres")
        self.current_scene = START_SCENE
        pyxel.run(self.update, self.draw)

    def reset_play_scene(self):
        self.player_x = SCREEN_WIDTH // 2
        self.player_y = SCREEN_HEIGHT * 4 // 5
        self.stones = []
        self.is_collision = False
        self.game_over_display_timer = GAME_OVER_DISPLAY_TIME  # ゲームオーバー表示時間

    def update_start_scene(self):
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            self.current_scene = PLAY_SCENE
            self.reset_play_scene()

    def update_play_scene(self):
        # ゲームオーバー時
        if self.is_collision:
            if self.game_over_display_timer > 0:
                self.game_over_display_timer -= 1
            else:
                self.current_scene = START_SCENE
            return

        #プレイヤーの移動
        if pyxel.btn(pyxel.KEY_RIGHT) and self.player_x < SCREEN_WIDTH - 16:
            self.player_x += 1
        elif pyxel.btn(pyxel.KEY_LEFT) and self.player_x > 0:
            self.player_x -= 1

        # 石の生成
        if pyxel.frame_count % STONE_INTERVAL == 0:
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

    def update(self):
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()
        
        if self.current_scene == START_SCENE:
            self.update_start_scene()
        elif self.current_scene == PLAY_SCENE:
            self.update_play_scene()

    def draw_start_scene(self):
        pyxel.blt(0, 0, 0, 32, 0, 160, 120)
        pyxel.text(SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT // 2 - 10, "Click to Start", pyxel.COLOR_WHITE)
        
    
    def draw_play_scene(self):
        pyxel.cls(pyxel.COLOR_ORANGE)
        # 石
        for stone in self.stones:
            stone.draw()
        # 人
        pyxel.blt(self.player_x, self.player_y, 0, 16, 0, 16, 16, pyxel.COLOR_BLACK )

        if self.is_collision:
            pyxel.text(SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT // 2, "GAME OVER", pyxel.COLOR_RED)

    def draw(self):
        if self.current_scene == START_SCENE:
            self.draw_start_scene()
        elif self.current_scene == PLAY_SCENE:
            self.draw_play_scene()




App()  # Create an instance of the App class to run the game