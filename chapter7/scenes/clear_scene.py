import pyxel


# クリア画面クラス
class ClearScene:
    # ゲームクリア画面を初期化する
    def __init__(self, game):
        self.game = game

    # ゲームクリア画面を開始する[
    def start(self):
        # BGMを再生する
        pyxel.stop()
        pyxel.playm(0, loop=True)

    # ゲームクリア画面を更新する
    def update(self):
        pass  # 何も動かさない

    # ゲームクリア画面を描画する
    def draw(self):
        # 画面をクリアする
        pyxel.cls(0)

        # フィールドを描画する
        self.game.draw_field()
        self.game.draw_player()
        self.game.draw_enemies()

        # テキストを描画する
        pyxel.rect(6, 49, 116, 30, 0)
        pyxel.rectb(6, 49, 116, 30, 7)
        pyxel.text(19, 57, "YOU ESCAPED THE CAVERN!", 7)
        pyxel.text(17, 66, "BUT YOUR QUEST CONTINUES", 7)
