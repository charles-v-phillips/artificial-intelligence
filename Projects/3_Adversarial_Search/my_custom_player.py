from sample_players import DataPlayer
import time
import random
from isolation import isolation, Isolation, DebugState
import math

beam_width = 9  # branching factor essentially
depth = 5



class TreeNode:
    def __init__(self, boardState,parent,action):
        self.board_state = boardState
        self.children = []
        self.n = 1
        self.parent = parent
        self.v = 0
        self.action = action


def ucb1(node):
    exploit = node.v
    explore = 2*math.sqrt(math.log(node.parent.n,math.e)/node.n)
    return explore + exploit

def traverse(node):
    current = node
    while len(current.children) != 0:
        current = max(current.children, key=ucb1)
    return current


def rollout(node):
    b_s = node.board_state
    while True:
        if b_s.terminal_test():
            return -1 if b_s._has_liberties(b_s.player()) else 1
        action = random.choice(b_s.actions())
        b_s = b_s.result(action)


def back_propogate(node,num):
    while node is not None:
        node.v +=num
        node.n +=1
        node = node.parent
        num = -num


class CustomPlayer(DataPlayer):

    def MCTS(self,state, epochs):
        root = TreeNode(state,None,None)

        for i in range(epochs):
            leaf = traverse(root)
            if leaf.n == 0:
                simulation_result = rollout(leaf)
            else:
                leaf.children = [TreeNode(leaf.board_state.result(action), leaf,action) for action in leaf.board_state.actions()]
                if len(leaf.children) != 0:
                    leaf = leaf.children[0]
                    simulation_result = rollout(leaf)
                else: #this should mean we are at a terminal node
                    # print(DebugState.from_state(leaf.board_state))
                    simulation_result = -1 if leaf.board_state._has_liberties(leaf.board_state.player()) else 1


            back_propogate(leaf,simulation_result)

        best =  max(root.children, key= lambda x: x.v)
        node_vals = [node.v for node in root.children]
        # print(node_vals)
        print("move {} vals: {}".format(int(state.ply_count/2),node_vals))
        return best.action




    def get_action(self, state):


        # start_time = time.time()
        # print("SEARCHING")
        # move = self.alpha_beta_search(state,depth)
        # print("FOUND MOVE")

        # print("--- %s seconds ---" % (time.time() - start_time))
        # self.queue.put(move)


        if state.ply_count < 2:
            self.queue.put(random.choice(state.actions()))
        else:
            # start_time = time.time()

            self.queue.put(self.MCTS(state, 35))
            # self.queue.put(self.MCTS(state,35))


            # print(str(time.time()-start_time)[:6])
            # self.queue.put(self.minimax(state,depth))

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
    b = Isolation().result(5).result(27)
    c = CustomPlayer(0)
    best_move = c.MCTS(b,30)
    print(best_move)