# -*- coding: utf-8 -*-
# pyxel 2.x想定（160x120, 30FPS）
import pyxel
from game_scenes import StartScene, PlayScene

WIDTH, HEIGHT = 160, 120
FPS = 30


class App:
    def __init__(self):
        pyxel.init(WIDTH, HEIGHT, title="Arrow Rhythm (Prototype)", fps=FPS)
        self.scene = StartScene(on_start=self.start_game)
        pyxel.load("my_resource.pyxres")
        pyxel.run(self.update, self.draw)

    # スタート画面から難易度を受け取ってゲーム開始
    def start_game(self, difficulty: str):
        self.scene = PlayScene(
            difficulty=difficulty,
            on_finish=self.back_to_title,
        )

    # プレイ終了→タイトルへ
    def back_to_title(self):
        self.scene = StartScene(on_start=self.start_game)

    def update(self):
        self.scene.update()

    def draw(self):
        pyxel.cls(1)
        self.scene.draw()


if __name__ == "__main__":
    App()
