import pyxel


# タイトル画面クラス
class TitleScene:
    # タイトル画面を初期化する
    def __init__(self, game):
        self.game = game  # ゲームクラス
        self.alpha = 0.0  # 画面の透明度(0.0:透明, 1.0:不透明)

    # タイトル画面を開始する
    def start(self):
        # 画面の透明度を初期化する
        self.alpha = 0.0

        # プレイヤーを削除する
        self.game.player = None

        # 全ての敵を削除する
        self.game.enemies = []

        # BGMを再生する
        pyxel.playm(0, loop=True)

    def update(self):
        # 画面の透明度を変更する
        if self.alpha < 1.0:
            self.alpha += 0.015

        # キー入力をチェックする
        if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(
            pyxel.GAMEPAD1_BUTTON_B
        ):  # EnterキーまたはゲームパッドのBボタンが押された時
            # 画面の透明度を不透明にする
            pyxel.dither(1.0)

            # プレイ画面に切り替える
            self.game.change_scene("play")

    def draw(self):
        # 画面をクリアする
        pyxel.cls(0)

        # タイトル画像を描画する
        pyxel.dither(self.alpha)  # 描画の透明度を設定
        pyxel.bltm(0, 0, 1, 0, 0, 128, 128)
        pyxel.blt(0, 0, 1, 0, 0, 128, 128, 0)

        # テキストを描画する
        pyxel.rect(30, 97, 67, 11, 0)
        pyxel.text(34, 100, "PRESS ENTER KEY", 7)
