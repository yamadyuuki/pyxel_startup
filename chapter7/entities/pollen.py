import pyxel


# 花粉クラス
class Pollen:
    # 花粉を初期化する
    def __init__(self, game, x, y, dx, dy):
        self.game = game  # ゲームクラス
        self.x = x  # X座標
        self.y = y  # Y座標
        self.dx = dx  # X軸方向の移動距離
        self.dy = dy  # Y軸方向の移動距離

    # 花粉を更新する
    def update(self):
        # 位置を更新する
        self.x += self.dx
        self.y += self.dy

    # 花粉を描画する
    def draw(self):
        # 画像の参照X座標を決める
        u = pyxel.frame_count % 2 * 8 + 8  # 1フレーム周期で16と24を繰り返す

        # 画像を描画する
        pyxel.blt(self.x, self.y, 0, u, 104, 8, 8, 15)
