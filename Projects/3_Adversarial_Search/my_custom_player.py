from sample_players import DataPlayer
import time
import random
from isolation import isolation, Isolation, DebugState
import math

beam_width = 9  # branching factor essentially
depth = 5


class TreeNode:
    def __init__(self,board_state,parent,action):
        self.q = 0
        self.n = 0
        self.children = []
        self.parent = parent
        self.board_state = board_state
        self.action = action
        self.untried_actions = board_state.actions()
    def is_fully_expanded(self):
        if len(self.untried_actions) == 0:
            return True
        return False













class CustomPlayer(DataPlayer):

    def MCTS2(self,state):
        root = TreeNode(state,None,None)
        active_player = state.player()

        def ucb2(node,c):
            expand = node.q/node.n
            explore = c*math.sqrt(2*math.log(node.parent.n,2)/(node.n + 1))
            return expand + explore

        def best_child(node):
            return  max(node.children,key = lambda x : ucb2(x,1))

        def tree_policy(node):
            current = node
            while not current.board_state.terminal_test():
                if not current.is_fully_expanded():
                    return expand(current)
                else:
                    current = best_child(current)
            return current

        def expand(node):
            a = random.choice(node.untried_actions)
            node.untried_actions.remove(a)
            child = TreeNode(node.board_state.result(a), node, a)
            node.children.append(child)
            return child

        def default_policy(b_state):
            s = b_state
            while not s.terminal_test():
                a = random.choice(s.actions())
                s = s.result(a)

            if s._has_liberties(active_player):return 1
            return 0

        def backup(node,val):
            current = node
            while current is not None:
                current.q +=val
                current.n +=1
                val = 1-val
                current = current.parent


        start_time = time.time()
        iter = 0

        while time.time() - start_time < .14:


            root_dummy = root

            leaf = tree_policy(root_dummy)
            reward = default_policy(leaf.board_state)
            backup(leaf,reward)
            iter+=1


        node_vals = [round(ucb2(node,0), 3) for node in root.children]

        print("move {} vals: {}, {} iterations".format(int(state.ply_count / 2), node_vals,iter))
        best_child = max(root.children,key = lambda x : ucb2(x,0))
        return best_child.action














    def get_action(self, state):
        if state.ply_count < 2:
            self.queue.put(random.choice(state.actions()))
        else:
            self.queue.put(self.MCTS2(state))










    def alpha_beta_search(self,gameState, depth):

        def min_value(gameState, alpha, beta, depth):
            """ Return the value for a win (+1) if the game is over,
            otherwise return the minimum value over all legal child
            nodes.
            """
            if gameState.terminal_test():
                return gameState.utility(self.player_id)
            if depth <= 0: return self.score(gameState)

            v = float("inf")
            actions = gameState.actions()
            actions.sort(key=lambda x: self.score(gameState.result(x)), reverse=False)
            top_moves = actions[:beam_width]

            for a in top_moves:
                v = min(v, max_value(gameState.result(a), alpha, beta, depth - 1))
                if v <= alpha:
                    return v
                beta = min(beta, v)
            return v


        def max_value(gameState, alpha, beta, depth):
            """ Return the value for a loss (-1) if the game is over,
            otherwise return the maximum value over all legal child
            nodes.
            """

            if gameState.terminal_test():
                return gameState.utility(self.player_id)

            if depth <= 0: return self.score(gameState)

            v = float("-inf")
            actions = gameState.actions()
            actions.sort(key=lambda x: self.score(gameState.result(x)), reverse=False)
            top_moves = actions[:beam_width]

            for a in top_moves:
                v = max(v, min_value(gameState.result(a), alpha, beta, depth-1))
                if v >= beta:
                    return v
                alpha = max(alpha, v)
            return v



        alpha = float("-inf")
        beta = float("inf")
        best_score = float("-inf")
        best_move = None
        actions = gameState.actions()
        actions.sort(key=lambda x: self.score(gameState.result(x)), reverse=True)
        top_moves = actions[:beam_width]
        for a in top_moves:
            v = min_value(gameState.result(a), alpha, beta, depth - 1)
            alpha = max(alpha, v)
            if v >= best_score:
                best_score = v
                best_move = a
        print(best_move)
        return best_move

    def score(self, state):
        own_loc = state.locs[self.player_id]
        opp_loc = state.locs[1 - self.player_id]
        own_liberties = state.liberties(own_loc)
        opp_liberties = state.liberties(opp_loc)
        if state.ply_count > (isolation._SIZE)/2:
            return 2 * len(own_liberties) - len(opp_liberties)
        return len(own_liberties) - 2*len(opp_liberties)

    def minimax(self, state, depth):

        def min_value(state, depth):
            if state.terminal_test(): return state.utility(self.player_id)
            if depth <= 0: return self.score(state)
            value = float("inf")
            for action in state.actions():
                value = min(value, max_value(state.result(action), depth - 1))
            return value

        def max_value(state, depth):
            if state.terminal_test(): return state.utility(self.player_id)
            if depth <= 0: return self.score(state)
            value = float("-inf")
            for action in state.actions():
                value = max(value, min_value(state.result(action), depth - 1))
            return value

        return max(state.actions(), key=lambda x: min_value(state.result(x), depth - 1))


if __name__ == '__main__':
    move_0_state = Isolation()
    move_1_state = move_0_state.result(random.choice(move_0_state.actions()))
    move_2_state = move_1_state.result(random.choice(move_1_state.actions()))
    terminal_state = move_2_state
    while not terminal_state.terminal_test():
        terminal_state = terminal_state.result(random.choice(terminal_state.actions()))
    terminal_state = terminal_state
    debug_board = DebugState.from_state(terminal_state)
    print(debug_board)
    p = CustomPlayer(terminal_state.player())
    p.MCTS2(terminal_state)


