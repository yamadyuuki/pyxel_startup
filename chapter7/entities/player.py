import pyxel
from collision import get_tile_type, in_collision, push_back
from constants import TILE_EXIT, TILE_GEM, TILE_LAVA, TILE_MUSHROOM, TILE_SPIKE


# プレイヤークラス
class Player:
    # プレイヤーを初期化する
    def __init__(self, game, x, y):
        self.game = game  # ゲームクラス
        self.x = x  # X座標
        self.y = y  # Y座標
        self.dx = 0  # X軸方向の移動距離
        self.dy = 0  # Y軸方向の移動距離
        self.direction = 1  # 左右の移動方向
        self.jump_counter = 0  # ジャンプ時間

    # プレイヤーを更新する
    def update(self):
        # キー入力に応じて左右に移動する
        if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(
            pyxel.GAMEPAD1_BUTTON_DPAD_LEFT
        ):  # 左キーまたはゲームパッド左ボタンが押されている時
            self.dx = -2
            self.direction = -1

        if pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(
            pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT
        ):  # 右キーまたはゲームパッド右ボタンが押されている時
            self.dx = 2
            self.direction = 1

        # 下方向に加速する
        if self.jump_counter > 0:  # ジャンプ中
            self.jump_counter -= 1  # ジャンプ時間を減らす
        else:  # ジャンプしていない時
            self.dy = min(self.dy + 1, 4)  # 下方向に加速する

        # タイルとの接触処理
        for i in [1, 6]:
            for j in [1, 6]:
                x = self.x + j
                y = self.y + i
                tile_type = get_tile_type(x, y)

                if tile_type == TILE_GEM:  # 宝石に触れた時
                    # スコアを加算する
                    self.game.score += 10

                    # 宝石タイルを消す
                    pyxel.tilemaps[0].pset(x // 8, y // 8, (0, 0))

                    # 効果音を再生する
                    pyxel.play(3, 1)

                if self.dy >= 0 and tile_type == TILE_MUSHROOM:  # キノコに触れた時
                    # ジャンプの距離を設定する
                    self.dy = -6
                    self.jump_counter = 6

                    # 効果音を再生する
                    pyxel.play(3, 2)

                if tile_type == TILE_EXIT:  # 出口に到達した時
                    self.game.change_scene("clear")
                    return

                if tile_type in [TILE_SPIKE, TILE_LAVA]:  # トゲ又は溶岩に触れた時
                    self.game.change_scene("gameover")
                    return

        # ジャンプする
        if (
            self.dy >= 0
            and (
                in_collision(self.x, self.y + 8) or in_collision(self.x + 7, self.y + 8)
            )
            and (pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B))
        ):
            # 上昇中ではなく、プレイヤーの左下又は右下が床に接している状態で
            # スペースキーまたはゲームパッドのBボタンが押された時
            self.dy = -6
            self.jump_counter = 2
            pyxel.play(3, 0)

        # 押し戻し処理
        self.x, self.y = push_back(self.x, self.y, self.dx, self.dy)

        # 横方向の移動を減速する
        self.dx = int(self.dx * 0.8)

    # プレイヤーを描画する
    def draw(self):
        # 画像の参照X座標を決める
        u = pyxel.frame_count // 4 % 2 * 8 + 8
        # 4フレーム周期で0と8を交互に繰り返す

        # 画像の幅を決める
        w = 8 if self.direction > 0 else -8
        # 移動方向が正の場合は8にしてそのまま描画、負の場合は-8にして左右反転させる

        # 画像を描画する
        pyxel.blt(self.x, self.y, 0, u, 64, w, 8, 15)
