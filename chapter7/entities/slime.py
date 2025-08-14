import pyxel
from collision import in_collision, push_back


# スライムクラス
class Slime:
    # スライムを初期化する
    def __init__(self, game, x, y, is_elite):
        self.game = game  # ゲームクラス
        self.x = x  # X座標
        self.y = y  # Y座標
        self.dx = 0  # X軸方向の移動距離
        self.dy = 0  # Y軸方向の移動距離
        self.direction = -1  # 左右の移動方向
        self.is_elite = is_elite  # レッドスライムかどうか
        self.is_waiting = is_elite  # 待ち伏せ中かどうか

    # スライムを更新する
    def update(self):
        if self.is_waiting:  # 待ち伏せ中の時
            if (
                abs(self.game.player.x - self.x) >= 32
                or abs(self.game.player.y - self.y) >= 16
            ):  # プレイヤーと一定距離離れている時
                return

            # プレイヤーと接近した時
            self.is_waiting = False
            self.direction = 1 if self.game.player.x > self.x else -1
            return

        # 移動距離を決める
        self.dx = self.direction
        self.dy = min(self.dy + 1, 3)

        # 移動方向を反転させる
        if self.direction < 0 and in_collision(
            self.x - 1, self.y + 4
        ):  # 左に進むと壁の時
            self.direction = 1  # 右に移動する
        elif self.direction > 0 and in_collision(
            self.x + 8, self.y + 4
        ):  # 右に進むと壁の時
            self.direction = -1  # 左に移動する

        # 押し戻し処理
        self.x, self.y = push_back(self.x, self.y, self.dx, self.dy)

    # スライムを描画する
    def draw(self):
        # 画像の参照X座標を決める
        u = pyxel.frame_count // 4 % 2 * 8 + 8  # イメージバンクの参照X座標
        # 4フレーム周期で0と8を繰り返す

        # 画像を描画する
        if self.is_elite:  # レッドスライム
            pyxel.blt(self.x, self.y, 0, u, 80, 8, 8, 15)
        else:  # グリーンスライム
            pyxel.blt(self.x, self.y, 0, u, 72, 8, 8, 15)
