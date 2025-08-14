# シーン(画面)モジュール

# scenesフォルダのクラスを__init__.pyでインポートすることで
#   from scenes.play_scene import PlayScene
# のように個別にインポートする代わりに
#   from scenes import PlayScene, TitleScene, GameOverScene
# のようにまとめてインポートできるようにする

from .clear_scene import ClearScene  # クリア画面クラス
from .gameover_scene import GameOverScene  # ゲームオーバー画面クラス
from .play_scene import PlayScene  # プレイ画面クラス
from .title_scene import TitleScene  # タイトル画面クラス
