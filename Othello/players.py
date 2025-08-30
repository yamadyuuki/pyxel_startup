# coding: utf-8
from abc import ABC, abstractmethod
import copy
from game_logic import Board, opponent, N, BLACK, WHITE

# --- 評価関数 ---
# 各マスの価値を定義した評価ボード (値が大きいほど有利)
EVALUATION_BOARD = [
    [120, -20,  20,   5,   5,  20, -20, 120],
    [-20, -40,  -5,  -5,  -5,  -5, -40, -20],
    [ 20,  -5,  15,   3,   3,  15,  -5,  20],
    [  5,  -5,   3,   3,   3,   3,  -5,   5],
    [  5,  -5,   3,   3,   3,   3,  -5,   5],
    [ 20,  -5,  15,   3,   3,  15,  -5,  20],
    [-20, -40,  -5,  -5,  -5,  -5, -40, -20],
    [120, -20,  20,   5,   5,  20, -20, 120],
]

def evaluate(board, color):
    """
    盤面を評価してスコアを返す関数。
    自分の石があるマスの価値の合計から、相手の石があるマスの価値の合計を引く。
    """
    own_score = 0
    opponent_score = 0
    opp_color = opponent(color)

    for y in range(N):
        for x in range(N):
            if board.get(x, y) == color:
                own_score += EVALUATION_BOARD[y][x]
            elif board.get(x, y) == opp_color:
                opponent_score += EVALUATION_BOARD[y][x]
    
    return own_score - opponent_score

# --- プレイヤーの基底クラス ---
class Player(ABC):
    """全プレイヤーの共通の機能を持つ基底クラス（抽象クラス）"""
    def __init__(self, color):
        self.color = color

    @abstractmethod
    def get_move(self, game):
        """次の手を返すメソッド。継承したクラスで必ず実装する。"""
        pass

# --- 人間プレイヤー ---
class HumanPlayer(Player):
    """人間の入力を受け付けるプレイヤークラス"""
    def get_move(self, game):
        # 人間の入力はmain.pyのupdateループで直接処理されるため、ここでは何もしない
        return None

# --- 評価関数法に基づくCPUプレイヤー ---
class CPUPlayer(Player):
    """評価関数に基づいて手を選択するCPUプレイヤークラス"""
    def get_move(self, game):
        if game.current != self.color:
            return None

        best_score = -float('inf')
        best_move = None
        
        moves = game.legal_moves(self.color)
        if not moves:
            return None

        # 最初の合法手をデフォルトの最善手としておく
        best_move = list(moves)[0]

        for x, y in moves:
            # ゲームの状態をコピーして、もしこの手を打ったらどうなるかシミュレーションする
            # copy.deepcopyは低速なため、パフォーマンスが重要な場合はより効率的な方法を検討すること
            temp_game = copy.deepcopy(game)
            temp_game.play(x, y)
            
            # 評価は自分の色で行う
            score = evaluate(temp_game.board, self.color)
            
            if score > best_score:
                best_score = score
                best_move = (x, y)
                
        return best_move
