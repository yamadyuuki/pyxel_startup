import pyxel
from scenes import ClearScene, GameOverScene, PlayScene, TitleScene


# ゲームクラス
class Game:
    # ゲームを初期化する
    def __init__(self):
        # Pyxelを初期化する
        pyxel.init(128, 128, title="Cursed Caverns")

        # リソースファイルを読み込む
        pyxel.load("assets/cursed_caverns.pyxres")
        pyxel.tilemaps[2].blt(0, 0, 0, 0, 0, 256, 16)  # 変更前のマップをコピーする

        # ゲームの状態を初期化する
        self.player = None  # プレイヤー
        self.enemies = []  # 敵のリスト
        self.scenes = {
            "title": TitleScene(self),
            "play": PlayScene(self),
            "gameover": GameOverScene(self),
            "clear": ClearScene(self),
        }  # シーンの辞書
        self.scene_name = None  # 現在のシーン名
        self.screen_x = 0  # フィールド表示範囲の左端のX座標
        self.score = 0  # 得点

        # シーンをタイトル画面に変更する
        self.change_scene("title")

        # ゲームの実行を開始する
        pyxel.run(self.update, self.draw)

    # シーンを変更する
    def change_scene(self, scene_name):
        self.scene_name = scene_name
        self.scenes[self.scene_name].start()

    # フィールドを描画する
    def draw_field(self):
        pyxel.bltm(0, 0, 0, self.screen_x, 0, 128, 128)

    # プレイヤーを描画する
    def draw_player(self):
        # カメラ位置(描画の原点)を変更する
        pyxel.camera(self.screen_x, 0)

        # プレイヤーを描画する
        if self.player is not None:  # プレイヤーが存在する時
            self.player.draw()

        # カメラ位置を戻す
        pyxel.camera()

    # 敵を描画する
    def draw_enemies(self):
        # カメラ位置(描画の原点)を変更する
        pyxel.camera(self.screen_x, 0)

        # 敵を描画する
        for enemy in self.enemies:
            enemy.draw()

        # カメラ位置を戻す
        pyxel.camera()

    # ゲームを更新する
    def update(self):
        # 現在のシーンを更新する
        self.scenes[self.scene_name].update()

    # ゲームを描画する
    def draw(self):
        # 現在のシーンを描画する
        self.scenes[self.scene_name].draw()

        # スコアを描画する
        pyxel.text(45, 4, f"SCORE {self.score:4}", 7)
