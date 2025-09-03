import pyxel
import pyxel
from scenes import SceneManager, TitleScene, PlayScene, ResultScene

# --- 定数設定 ---
SCREEN_WIDTH = 256
SCREEN_HEIGHT = 192
GAME_TITLE = "Mini Kabu Trader"

class App:
    """
    ゲーム全体を管理するクラス
    Pyxelの初期化、シーンマネージャーの生成、メインループの実行を担当
    """
    def __init__(self):
        # Pyxelウィンドウの初期化
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title=GAME_TITLE, fps=30)

        # シーンマネージャーを生成
        self.scene_manager = SceneManager()

        # 全てのシーンを生成し、マネージャーに登録
        # シーンに渡す'manager=self.scene_manager'は、各シーンが他のシーンへ
        # 遷移できるようにするためのお作法です。
        self.scene_manager.add_scene("title", TitleScene(manager=self.scene_manager))
        self.scene_manager.add_scene("play", PlayScene(manager=self.scene_manager))
        self.scene_manager.add_scene("result", ResultScene(manager=self.scene_manager))

        # 開始シーンをタイトル画面に設定
        self.scene_manager.change_scene("title")

        # Pyxelの実行（これによりゲームループが開始される）
        pyxel.run(self.update, self.draw)

    def update(self):
        """
        毎フレームの更新処理
        実際の処理は現在のシーンに委ねる
        """
        self.scene_manager.update()

    def draw(self):
        """
        毎フレームの描画処理
        実際の処理は現在のシーンに委ねる
        """
        # 画面を黒でクリア
        pyxel.cls(2)
        self.scene_manager.draw()

# --- プログラムの開始点 ---
if __name__ == "__main__":
    # Appクラスのインスタンスを作成してゲームを開始
    App()