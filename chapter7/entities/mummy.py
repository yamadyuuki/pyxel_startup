import pyxel
from collision import in_collision, push_back


# マミークラス
class Mummy:
    # マミーを初期化する
    def __init__(self, game, x, y):
        self.game = game  # ゲームクラス
        self.x = x  # X座標
        self.y = y  # Y座標
        self.dx = 0  # X軸方向の移動距離
        self.dy = 0  # Y軸方向の移動距離
        self.direction = 1  # 左右の移動方向

    # マミーを更新する
    def update(self):
        # 移動距離を決める
        self.dx = self.direction  # X軸方向の移動距離
        self.dy = min(self.dy + 1, 3)  # Y軸方向の移動距離

        # 移動方向を反転させる
        if in_collision(self.x, self.y + 8) or in_collision(
            self.x + 7, self.y + 8
        ):  # 床の上にいる時
            if self.direction < 0 and (
                in_collision(self.x - 1, self.y + 4)
                or not in_collision(self.x - 1, self.y + 8)
            ):  # 移動先に壁があるまたは床がない時
                self.direction = 1  # 右に移動する
            elif self.direction > 0 and (
                in_collision(self.x + 8, self.y + 4)
                or not in_collision(self.x + 8, self.y + 8)
            ):  # 移動先に壁があるまたは床がない時
                self.direction = -1  # 左に移動する

        # 押し戻し処理
        self.x, self.y = push_back(self.x, self.y, self.dx, self.dy)

    # マミーを描画する
    def draw(self):
        # 画像の参照X座標を決める
        u = pyxel.frame_count // 4 % 2 * 8 + 8  # 4フレーム周期で16と24を繰り返す

        # 画像の幅を決める
        w = 8 if self.direction > 0 else -8
        # 移動方向が正の場合は8にしてそのまま描画、負の場合は-8にして左右反転させる

        # 画像を描画する
        pyxel.blt(self.x, self.y, 0, u, 88, w, 8, 15)
