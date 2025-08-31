# coding: utf-8
from abc import ABC, abstractmethod
import copy
from game_logic import Board, opponent, N, BLACK, WHITE

# --- デバッグ用ログカウンター ---
debug_counter = 0

# --- 評価関数 (変更なし) ---
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

# --- プレイヤーの基底クラス (変更なし) ---
class Player(ABC):
    def __init__(self, color):
        self.color = color
    @abstractmethod
    def get_move(self, game):
        pass

# --- 人間プレイヤー (変更なし) ---
class HumanPlayer(Player):
    def get_move(self, game):
        return None

# --- CPUプレイヤー (HARD: 評価関数法) (変更なし) ---
class CPUPlayer(Player):
    def get_move(self, game):
        if game.current != self.color: return None
        best_score = -float('inf')
        best_move = None
        moves = game.legal_moves(self.color)
        if not moves: return None
        best_move = list(moves)[0]
        for x, y in moves:
            temp_game = copy.deepcopy(game)
            temp_game.play(x, y)
            score = evaluate(temp_game.board, self.color)
            if score > best_score:
                best_score = score
                best_move = (x, y)
        return best_move

# --- 探索アルゴリズム CPU (VERY HARD) - デバッグ用修正版 ---
class SearchCPUPlayer(Player):
    SEARCH_DEPTH = 3  # 深度1でテスト

    def get_move(self, game):
        """ミニマックス法を使って最善手を見つける"""
        if game.current != self.color:
            return None
        
        best_score = -float('inf')
        best_move = None
        moves = game.legal_moves(self.color)

        if not moves:
            return None

        if len(moves) == 1:
            return list(moves)[0]
            
        for move in moves:
            temp_game = copy.deepcopy(game)
            temp_game.play(move[0], move[1])
            
            # あなたが発見した正しいロジックを適用
            # play()後に手番が自分に戻ってくるケース（パス）を考慮する
            is_next_player_maximizer = (temp_game.current == self.color)
            
            # 正しいフラグを渡してミニマックス法を呼び出す
            score = self._minimax(temp_game, self.SEARCH_DEPTH - 1, is_next_player_maximizer)
            
            if score > best_score:
                best_score = score
                best_move = move
        
        return best_move if best_move is not None else list(moves)[0]

    def _minimax(self, game, depth, is_maximizing_player):
        """
        ミニマックス法の本体 (再帰関数) - 改良版
        """
        # --- 終了条件を先頭に集約 ---
        current_moves = game.legal_moves(game.current)
        opponent_color = opponent(game.current)
        opponent_moves = game.legal_moves(opponent_color)

        # 1. 両者とも打つ手がない、またはゲームが終了していたら盤面を評価
        if (not current_moves and not opponent_moves) or game.game_over:
            return evaluate(game.board, self.color)
        
        # 2. 規定の深さに達したら盤面を評価
        if depth == 0:
            return evaluate(game.board, self.color)

        # --- パスの場合の処理を共通化 ---
        # 現在のプレイヤーがパスするしか無い場合
        if not current_moves:
            # 手番だけを相手に移して、探索を1段階深く続行する
            # (is_maximizing_playerフラグも反転させる)
            temp_game = copy.deepcopy(game)
            temp_game.current = opponent_color
            return self._minimax(temp_game, depth - 1, not is_maximizing_player)

        # --- 通常の探索処理 ---
        if is_maximizing_player:
            max_eval = -float('inf')
            # 変数 'moves' を 'current_moves' に変更
            for move in current_moves:
                temp_game = copy.deepcopy(game)
                temp_game.play(move[0], move[1])
                eval = self._minimax(temp_game, depth - 1, False)
                max_eval = max(max_eval, eval)
            return max_eval
        
        else: # MINプレイヤー
            min_eval = float('inf')
            # 変数 'moves' を 'current_moves' に変更
            for move in current_moves:
                temp_game = copy.deepcopy(game)
                temp_game.play(move[0], move[1])
                eval = self._minimax(temp_game, depth - 1, True)
                min_eval = min(min_eval, eval)
            return min_eval

# --- (仮) 強化学習CPU (LUNATIC) ---
class RLCPUPlayer(CPUPlayer):
    pass