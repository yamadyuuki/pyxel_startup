# エンティティ(キャラクター)モジュール

# entitiesフォルダのクラスを__init__.pyでインポートすることで
#   from entities.player import Player
# のようにクラスを個別にインポートする代わりに
#   from entities import Player, Enemy1, Enemy2, Enemy3
# のようにまとめてインポートできるようにする

from .flower import Flower  # フラワークラス
from .mummy import Mummy  # マミークラス
from .player import Player  # プレイヤークラス
from .pollen import Pollen  # 花粉クラス
from .slime import Slime  # スライムクラス
