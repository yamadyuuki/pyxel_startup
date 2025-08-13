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
        self.number = 0
        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()
        
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            if 30 <= pyxel.mouse_x <= 50 and 60 <= pyxel.mouse_y <= 80:
                self.number -=1
            elif 110 <= pyxel.mouse_x <= 130 and 60 <= pyxel.mouse_y <= 80:
                self.number += 1
    def draw(self):
        pyxel.cls(pyxel.COLOR_DARK_BLUE)
        pyxel.text(number_x, text_y, f"{self.number}", pyxel.COLOR_WHITE)
        pyxel.text(minus_x, text_y, "-", pyxel.COLOR_WHITE)
        pyxel.text(plus_x, text_y, "+", pyxel.COLOR_WHITE)
        #

App()  # Create an instance of the App class to run the game