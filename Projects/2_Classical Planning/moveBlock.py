from aimacode.planning import Action
from aimacode.search import (
    breadth_first_search, astar_search, depth_first_graph_search,
    uniform_cost_search, greedy_best_first_graph_search
)
from aimacode.utils import expr

from _utils import (
    FluentState, encode_state,make_relations,run_search
)
from planning_problem import BasePlanningProblem

class MoveBlockProblem(BasePlanningProblem):
    def __init__(self,initial,goal):
        super().__init__(initial,goal)
        self.action_list = self.get_actions()

    def get_actions(self):
        precond_pos = [expr("On(b,x)"),
                       expr("Clear(b)"),
                       expr("Clear(y)"),
                       expr("Block(b)"),
                       expr(expr("Block(y)"))]
        precon_neg = [expr("")]
        move_action = Action()