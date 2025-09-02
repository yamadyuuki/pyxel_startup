# coding: utf-8
from abc import ABC, abstractmethod
import copy
from game_logic import Board, opponent, N, BLACK, WHITE
import time
import math
import random
import copy

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

# --- モンテカルロ木探索 - MCTS - (LUNATIC) ---
class MCTSCPUPlayer(Player):
    # 時間ベースの打ち切り（ミリ秒）
    THINK_TIME_MS = 300
    # UCTの探査定数
    EXPLORATION_C = 1.4142

    CORNERS = {(0,0),(0,N-1),(N-1,0),(N-1,N-1)}

    class Node:
        __slots__ = ("state","move","parent","children","wins","visits","untried_moves","player_to_move")
        def __init__(self, state, parent=None, move=None, player_to_move=None):
            self.state = state
            self.move = move
            self.parent = parent
            self.children = []
            self.wins = 0.0
            self.visits = 0
            self.untried_moves = list(state.legal_moves(state.current))
            # 誰の手番かをキャッシュ（rollout/backpropの視点判定用）
            self.player_to_move = state.current if player_to_move is None else player_to_move

        def uct_best_child(self, c):
            ln_parent = math.log(self.visits)
            best, best_score = None, -1e18
            for ch in self.children:
                if ch.visits == 0:
                    score = 1e9  # 未訪問は最優先
                else:
                    exploit = ch.wins / ch.visits
                    explore = c * math.sqrt(ln_parent / ch.visits)
                    score = exploit + explore
                if score > best_score:
                    best, best_score = ch, score
            return best

        def add_child(self, move):
            # 子局面を一手進めて作る
            next_state = copy.deepcopy(self.state)
            next_state.play(move[0], move[1])
            child = MCTSCPUPlayer.Node(next_state, parent=self, move=move, player_to_move=next_state.current)
            self.children.append(child)
            return child

        def update(self, result):
            self.visits += 1
            self.wins += result

    def get_move(self, game):
        # 自分の手番でなければパス
        if game.current != self.color:
            return None

        legal = game.legal_moves(self.color)
        if not legal:
            return None
        if len(legal) == 1:
            return list(legal)[0]

        root = MCTSCPUPlayer.Node(copy.deepcopy(game))

        time_limit = time.perf_counter() + (self.THINK_TIME_MS / 1000.0)
        while time.perf_counter() < time_limit:
            node = root

            # 1) Selection: 既に全展開ならUCTで降下
            while node.untried_moves == [] and node.children:
                node = node.uct_best_child(self.EXPLORATION_C)

            # 2) Expansion: 未展開の手があれば1手だけ展開
            if node.untried_moves:
                move = self._select_expansion_move(node)
                # untried から取り除く
                node.untried_moves.remove(move)
                node = node.add_child(move)

            # 3) Simulation: 末端から終局までロールアウト
            result = self._rollout_result(node.state)

            # 4) Backpropagation: 自分視点の勝ち=1, 負け=0, 引分=0.5
            self._backpropagate(node, result)

        # 最後は訪問回数最大の子を選ぶ（勝率ではなく訪問数が安定）
        best = max(root.children, key=lambda ch: ch.visits)
        return best.move

    # --- 角優先の軽い拡張方策 ---
    def _select_expansion_move(self, node):
        moves = node.untried_moves
        # 角があれば必ず選ぶ
        for m in moves:
            if m in self.CORNERS:
                return m
        # それ以外はランダム
        return random.choice(moves)

    # --- ランダムロールアウト（角を軽く優先） ---
    def _rollout_result(self, sim_game):
        # ここでは sim_game を破壊してOK（呼び出し側は deepcopy を持っている）
        while not sim_game.game_over:
            moves = sim_game.legal_moves(sim_game.current)
            if moves:
                move = self._rollout_policy(sim_game, moves)
                sim_game.play(move[0], move[1])
            else:
                # 手がない場合はパス処理：次プレイヤに回す（Game.play後と同じロジックを模倣）
                sim_game.current = opponent(sim_game.current)
                # 連続で手がないなら終局
                if not sim_game.legal_moves(sim_game.current):
                    sim_game.game_over = True
        black, white = sim_game.score()
        if black > white:
            winner = BLACK
        elif white > black:
            winner = WHITE
        else:
            winner = 0  # draw
        # 自分視点に変換
        if winner == 0:
            return 0.5
        return 1.0 if winner == self.color else 0.0

    def _rollout_policy(self, sim_game, moves):
        # 角最優先
        corner_moves = [m for m in moves if m in self.CORNERS]
        if corner_moves:
            return random.choice(corner_moves)
        # それ以外はランダム
        return random.choice(list(moves))

    def _backpropagate(self, node, result):
        # node から root まで
        while node is not None:
            node.update(result)
            node = node.parent