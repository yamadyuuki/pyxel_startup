import pyxel
from collision import get_tile_type
from constants import (
    SCROLL_BORDER_X,
    TILE_FLOWER_POINT,
    TILE_MUMMY_POINT,
    TILE_SLIME1_POINT,
    TILE_SLIME2_POINT,
)
from entities import Flower, Mummy, Player, Slime


# プレイ画面クラス
class PlayScene:
    # プレイ画面を初期化する
    def __init__(self, game):
        self.game = game

    # プレイ画面を開始する
    def start(self):
        # 変更前のマップに戻す
        pyxel.tilemaps[0].blt(0, 0, 2, 0, 0, 256, 16)

        # プレイ画面の状態を初期化する
        game = self.game  # ゲームクラス
        game.player = Player(game, 0, 0)  # プレイヤー
        game.screen_x = 0  # フィールド表示範囲の左端のX座標
        game.score = 0  # スコア

        # 敵を出現させる
        self.spawn_enemy(0, 127)

        # BGMを再生する
        pyxel.stop()
        pyxel.playm(1, loop=True)

    # 敵を出現させる
    def spawn_enemy(self, left_x, right_x):
        game = self.game
        enemies = game.enemies

        # 判定範囲のタイルを計算する
        left_x = pyxel.ceil(left_x / 8)
        right_x = pyxel.floor(right_x / 8)

        # 判定範囲のタイルに応じて敵を出現させる
        for tx in range(left_x, right_x + 1):
            for ty in range(16):
                x = tx * 8
                y = ty * 8
                tile_type = get_tile_type(x, y)

                if tile_type == TILE_SLIME1_POINT:  # グリーンスライムの出現位置の時
                    enemies.append(Slime(game, x, y, False))
                elif tile_type == TILE_SLIME2_POINT:  # レッドスライムの出現位置の時
                    enemies.append(Slime(game, x, y, True))
                elif tile_type == TILE_MUMMY_POINT:  # マミーの出現位置の時
                    enemies.append(Mummy(game, x, y))
                elif tile_type == TILE_FLOWER_POINT:  # フラワーの出現位置の時
                    enemies.append(Flower(game, x, y))
                else:
                    continue

                # 出現位置タイルを消す
                pyxel.tilemaps[0].pset(tx, ty, (0, 0))

    # プレイ画面を更新する
    def update(self):
        game = self.game
        player = game.player
        enemies = game.enemies

        # プレイヤーを更新する
        if player is not None:
            player.update()

        # プレイヤーの移動範囲を制限する
        player.x = min(max(player.x, game.screen_x), 2040)
        player.y = max(player.y, 0)

        # プレイヤーがスクロール境界を越えたら画面をスクロールする
        if player.x > game.screen_x + SCROLL_BORDER_X:
            last_screen_x = game.screen_x
            game.screen_x = min(player.x - SCROLL_BORDER_X, 240 * 8)
            # 240タイル分以上は右にスクロールさせない

            # スクロールした幅に応じて敵を出現させる
            self.spawn_enemy(last_screen_x + 128, game.screen_x + 127)

        # プレイヤーが画面の下に落ちたらゲームオーバーにする
        if player.y >= pyxel.height:
            pyxel.play(3, 4)
            game.change_scene("gameover")

        # 敵を更新する
        for enemy in enemies.copy():
            enemy.update()

            # プレイヤーと敵が接触したらゲームオーバーにする
            if abs(player.x - enemy.x) < 6 and abs(player.y - enemy.y) < 6:
                game.change_scene("gameover")
                return

            # 敵が画面の左端または下端から外に出たら削除する
            if (
                enemy.x < game.screen_x - 8
                or enemy.x > game.screen_x + 160
                or enemy.y > 160
            ):
                if enemy in enemies:  # 敵リストに登録されている時
                    enemies.remove(enemy)

    # プレイ画面を描画する
    def draw(self):
        # 画面をクリアする
        pyxel.cls(0)

        # フィールドを描画する
        self.game.draw_field()

        # プレイヤーを描画する
        self.game.draw_player()

        # 敵を描画する
        self.game.draw_enemies()
