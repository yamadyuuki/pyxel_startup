import pyxel


# ゲームオーバー画面クラス
class GameOverScene:
    # ゲームオーバー画面を初期化する
    def __init__(self, game):
        self.game = game

    # ゲームオーバー画面を開始する
    def start(self):
        # 現在のプレイヤーの位置を保存する
        self.player_x = self.game.player.x  # プレイヤーのX座標
        self.player_y = self.game.player.y  # プレイヤーのY座標

        # ゲームオーバー画面の表示時間を設定する
        self.display_timer = 110

        # ゲームオーバー音を再生する
        pyxel.stop()
        pyxel.play(0, 3)

    # ゲームオーバー画面を更新する
    def update(self):
        # 表示時間が0になったらタイトル画面に戻る
        if self.display_timer > 0:
            self.display_timer -= 1
        else:
            self.game.change_scene("title")

    # ゲームオーバー画面を描画する
    def draw(self):
        # 画面をクリアする
        pyxel.cls(0)

        # カメラ位置を戻す
        pyxel.camera()

        # フィールドを描画する
        self.game.draw_field()

        # 敵を描画する
        self.game.draw_enemies()

        # ジタバタするプレイヤーを描画する
        pyxel.camera(self.game.screen_x, 0)  # カメラ位置(描画の原点)を変更する
        w = 8 if pyxel.frame_count // 2 % 2 == 0 else -8
        # 2フレーム周期で8と-8を繰り返す
        pyxel.blt(self.player_x, self.player_y, 0, 8, 64, w, 8, 15)
        pyxel.camera()  # カメラ位置を戻す

        # テキストを描画する
        pyxel.rect(6, 49, 116, 30, 0)
        pyxel.rectb(6, 49, 116, 30, 7)
        pyxel.text(47, 62, "GAME OVER", 7)
