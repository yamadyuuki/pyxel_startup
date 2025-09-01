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
    # 深さを元に戻しても、アルファベータ法ならより高速に動作します
    SEARCH_DEPTH = 4  # 例えば4に設定

    def get_move(self, game):
        """アルファベータ法を使って最善手を見つける"""
        if game.current != self.color:
            return None
        
        best_score = -float('inf')
        best_move = None
        moves = game.legal_moves(self.color)

        if not moves:
            return None

        if len(moves) == 1:
            return list(moves)[0]

        # 変更点: alphaとbetaの初期値を設定
        alpha = -float('inf')
        beta = float('inf')
            
        for move in moves:
            temp_game = copy.deepcopy(game)
            temp_game.play(move[0], move[1])
            
            is_next_player_maximizer = (temp_game.current == self.color)
            
            # 変更点: _alphabetaメソッドを呼び出し、alphaとbetaを渡す
            score = self._alphabeta(temp_game, self.SEARCH_DEPTH - 1, alpha, beta, is_next_player_maximizer)
            
            # get_moveはMAXプレイヤーの視点なので、スコアがalphaを更新するかチェック
            if score > best_score:
                best_score = score
                best_move = move
            
            # 変更点: ここでもalphaを更新する
            alpha = max(alpha, best_score)
        
        return best_move if best_move is not None else list(moves)[0]

    # 変更点: メソッド名を_minimaxから_alphabetaに変更し、alphaとbetaを引数に追加
    def _alphabeta(self, game, depth, alpha, beta, is_maximizing_player):
        """
        アルファベータ法の本体 (再帰関数)
        """
        # --- 終了条件 (ここは変更なし) ---
        current_moves = game.legal_moves(game.current)
        opponent_color = opponent(game.current)
        opponent_moves = game.legal_moves(opponent_color)

        if (not current_moves and not opponent_moves) or game.game_over or depth == 0:
            return evaluate(game.board, self.color)
        
        # --- パスの処理 (ここは変更なし) ---
        if not current_moves:
            temp_game = copy.deepcopy(game)
            temp_game.current = opponent_color
            return self._alphabeta(temp_game, depth - 1, alpha, beta, not is_maximizing_player)

        # --- 探索処理 (ここからがアルファベータ法の本質) ---
        if is_maximizing_player: # MAXプレイヤー (自分)
            max_eval = -float('inf')
            for move in current_moves:
                temp_game = copy.deepcopy(game)
                temp_game.play(move[0], move[1])
                eval = self._alphabeta(temp_game, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, eval)
                
                # 変更点: alphaを更新
                alpha = max(alpha, eval)
                
                # 変更点: 枝刈り！
                if beta <= alpha:
                    break # この枝はこれ以上調べても無駄
            return max_eval
        
        else: # MINプレイヤー (相手)
            min_eval = float('inf')
            for move in current_moves:
                temp_game = copy.deepcopy(game)
                temp_game.play(move[0], move[1])
                eval = self._alphabeta(temp_game, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval)

                # 変更点: betaを更新
                beta = min(beta, eval)

                # 変更点: 枝刈り！
                if beta <= alpha:
                    break # この枝はこれ以上調べても無駄
            return min_eval

# --- (仮) 強化学習CPU (LUNATIC) ---
class RLCPUPlayer(CPUPlayer):
    pass