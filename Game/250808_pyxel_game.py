#250808_pyxel_game.py

import pyxel
SCREEN_WIDTH = 160
SCREEN_HEIGHT = 120
center_x = SCREEN_WIDTH // 2
center_y = SCREEN_HEIGHT // 2
minus_x = SCREEN_WIDTH // 4
plus_x = SCREEN_WIDTH * 3 // 4
number_x = center_x - 6  # 少し左に寄せて中央に見えるように
text_y = center_y

class App:
    def __init__(self):
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="My Game") 
        pyxel.mouse(True)
        self.player_x = SCREEN_WIDTH // 2
        pyxel.load("my_resource.pyxres")
        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()

        if pyxel.btn(pyxel.KEY_RIGHT) and self.player_x < SCREEN_WIDTH - 16:
            self.player_x += 1
        elif pyxel.btn(pyxel.KEY_LEFT) and self.player_x > 0:
            self.player_x -= 1
        
    def draw(self):
        pyxel.cls(pyxel.COLOR_WHITE)
        # 石
        pyxel.blt(SCREEN_WIDTH // 2, 0, 0, 8, 0, 8, 8, pyxel.COLOR_BLACK )
        # 人
        pyxel.blt(self.player_x, SCREEN_HEIGHT * 4 // 5, 0, 16, 0, 16, 16, pyxel.COLOR_BLACK )



App()  # Create an instance of the App class to run the game