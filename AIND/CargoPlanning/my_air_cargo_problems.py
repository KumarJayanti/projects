from aimacode.logic import PropKB
from aimacode.planning import Action
from aimacode.search import (
    Node, Problem,
)
from aimacode.utils import expr
from lp_utils import (
    FluentState, encode_state, decode_state, conjunctive_sentence,
)
from my_planning_graph import PlanningGraph

from functools import lru_cache

import logging

#uncomment for debugging
#logging.basicConfig(filename='AirCargoProblem.log',level=logging.DEBUG)
class AirCargoProblem(Problem):
    def __init__(self, cargos, planes, airports, initial: FluentState, goal: list):
        """

        :param cargos: list of str
            cargos in the problem
        :param planes: list of str
            planes in the problem
        :param airports: list of str
            airports in the problem
        :param initial: FluentState object
            positive and negative literal fluents (as expr) describing initial state
        :param goal: list of expr
            literal fluents required for goal test
        """
        self.state_map = initial.pos + initial.neg
        self.initial_state_TF = encode_state(initial, self.state_map)
        Problem.__init__(self, self.initial_state_TF, goal=goal)
        self.cargos = cargos
        self.planes = planes
        self.airports = airports
        self.actions_list = self.get_actions()

     
    def get_actions(self):
        """
        This method creates concrete actions (no variables) for all actions in the problem
        domain action schema and turns them into complete Action objects as defined in the
        aimacode.planning module. It is computationally expensive to call this method directly;
        however, it is called in the constructor and the results cached in the `actions_list` property.

        Returns:
        ----------
        list<Action>
            list of Action objects
        """

        # TODO create concrete Action objects based on the domain action schema for: Load, Unload, and Fly
        # concrete actions definition: specific literal action that does not include variables as with the schema
        # for example, the action schema 'Load(c, p, a)' can represent the concrete actions 'Load(C1, P1, SFO)'
        # or 'Load(C2, P2, JFK)'.  The actions for the planning problem must be concrete because the problems in
        # forward search and Planning Graphs must use Propositional Logic

        
        def load_actions():
            """Create all concrete Load actions and return a list

            :return: list of Action objects
            """
            loads = []
            for c in self.cargos:
                for p in self.planes:
                    for a in self.airports:
                        #PRECOND:At(c, a) ∧ At(p, a) ∧ Cargo(c) ∧ Plane(p) ∧ Airport(a)
                        #ignore the unary ones
                        precond_pos = [expr("At({},{})".format(c,a)), expr("At({},{})".format(p,a))]
                        
                        precond_neg = []
                        #EFFECT: ¬ At(c, a) ∧ In(c, p))
                        effect_add = [expr("In({},{})".format(c,p))]
                        effect_rem = [expr("At({},{})".format(c,a))]
                        #Load(c, p, a)
                        act = Action(expr("Load({},{},{})".format(c,p,a)), 
                                     [precond_pos, precond_neg], [effect_add, effect_rem])
                        loads.append(act)  
            return loads

        def unload_actions():
            """Create all concrete Unload actions and return a list

            :return: list of Action objects
            """
            unloads = []
            for c in self.cargos:
                for p in self.planes:
                    for a in self.airports:
                        #PRECOND: In(c, p) ∧ At(p, a) ∧ Cargo(c) ∧ Plane(p) ∧ Airport(a)
                        precond_pos = [expr("In({},{})".format(c,p)), 
                                       expr("At({},{})".format(p,a))]
                        
                        precond_neg = []
                        #EFFECT: At(c, a) ∧ ¬ In(c, p))
                        effect_add = [expr("At({},{})".format(c,a))]
                        effect_rem = [expr("In({},{})".format(c,p))]
                        #Unload(c, p, a)
                        act = Action(expr("Unload({},{},{})".format(c,p,a)), 
                                     [precond_pos, precond_neg], 
                                     [effect_add, effect_rem])
                        unloads.append(act) 
            return unloads

        def fly_actions():
            """Create all concrete Fly actions and return a list

            :return: list of Action objects
            """
            flys = []
            for fr in self.airports:
                for to in self.airports:
                    if fr != to:
                        for p in self.planes:
                            precond_pos = [expr("At({}, {})".format(p, fr)),
                                           ]
                            precond_neg = []
                            effect_add = [expr("At({}, {})".format(p, to))]
                            effect_rem = [expr("At({}, {})".format(p, fr))]
                            fly = Action(expr("Fly({}, {}, {})".format(p, fr, to)),
                                         [precond_pos, precond_neg],
                                         [effect_add, effect_rem])
                            flys.append(fly)
            return flys

        return load_actions() + unload_actions() + fly_actions()

    def check_precond(self, kb, action):
        """Checks if the precondition is satisfied in the current state"""
        assert isinstance(kb, PropKB), "kb is not of type PropKB: %r" % kb
        
        # check for positive clauses
        for clause in action.precond_pos:
            if clause not in kb.clauses:
                return False
        # check for negative clauses
        for clause in action.precond_neg:
            if clause in kb.clauses:
                return False
        logger.debug("All precondtions satisfied for action=%r", action)
        return True
    
    def apply_action(self, kb, action):
        # check if the preconditions are satisfied
        #if not self.check_precond(kb, action):
        #    raise Exception("Action pre-conditions not satisfied")
        # remove negative litera
        for clause in action.effect_rem:
            kb.retract(clause)
        # add positive literals
        for clause in action.effect_add:
            kb.tell(clause)
    
    def actions(self, state: str) -> list:
        """ Return the actions that can be executed in the given state.

        :param state: str
            state represented as T/F string of mapped fluents (state variables)
            e.g. 'FTTTFF'
        :return: list of Action objects
        """
        
        #The actions that are applicable to a state are all those whose preconditions are satisfied.
        kb = PropKB()
        kb.tell(decode_state(state, self.state_map).pos_sentence())
        possible_actions = [ a for a in self.actions_list if a.check_precond(kb, a.args) ]
        return possible_actions
         
       
    def result(self, state: str, action: Action):
        """ Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state).

        :param state: state entering node
        :param action: Action applied
        :return: resulting state after action
        """
        assert state != None, "state passed to Problem.result is None"
        assert action != None, "action passed to Problem.result is None"
        
        new_state = FluentState([], [])
        #decode the fulents of the current state
        old_fs = decode_state(state, self.state_map)
        
        #compute the new state's positive fluents by applying the actions
        kb = PropKB()
        #initialize a KB with positive fluents of old state.
        kb.tell(old_fs.pos_sentence())
        # apply the rem and add effects of the action onto the KB
        self.apply_action(kb,action)
        # the positive fluents of new state are in KB
        new_state.pos = kb.clauses
        logging.debug("Positive Fluents of New State: %r", new_state.pos)
        #encode_state only cares about the positive fluents in new_state
        #anything in state_map which is not in new_state.pos is assigned 'F'
        return encode_state(new_state, self.state_map)
         

    def goal_test(self, state: str) -> bool:
        """ Test the state to see if goal is reached

        :param state: str representing state
        :return: bool
        """
        kb = PropKB()
        kb.tell(decode_state(state, self.state_map).pos_sentence())
        for clause in self.goal:
            if clause not in kb.clauses:
                return False
        return True

    def h_1(self, node: Node):
        # note that this is not a true heuristic
        h_const = 1
        return h_const

    @lru_cache(maxsize=8192)
    def h_pg_levelsum(self, node: Node):
        """This heuristic uses a planning graph representation of the problem
        state space to estimate the sum of all actions that must be carried
        out from the current state in order to satisfy each individual goal
        condition.
        """
        # requires implemented PlanningGraph class
        pg = PlanningGraph(self, node.state)
        pg_levelsum = pg.h_levelsum()
        return pg_levelsum

    @lru_cache(maxsize=8192)
    def h_ignore_preconditions(self, node: Node):
        """This heuristic estimates the minimum number of actions that must be
        carried out from the current state in order to satisfy all of the goal
        conditions by ignoring the preconditions required for an action to be
        executed.
        """
        assert node != None, "Node passed to h_ignore_preconditions is None"
        # implement (see Russell-Norvig Ed-3 10.2.3  or Russell-Norvig Ed-2 11.2)
        count = 0
        kb = PropKB()
        # Add the positive sentences of current state to KB 
        kb.tell(decode_state(node.state, self.state_map).pos_sentence())

        for clause in self.goal:
            if clause not in kb.clauses:
                count += 1
        return count


"""
-Init(At(C1, SFO) ∧ At(C2, JFK) 
    ∧ At(P1, SFO) ∧ At(P2, JFK) 
    ∧ Cargo(C1) ∧ Cargo(C2) 
    ∧ Plane(P1) ∧ Plane(P2)
    ∧ Airport(JFK) ∧ Airport(SFO))
Goal(At(C1, JFK) ∧ At(C2, SFO))

"""
def air_cargo_p1() -> AirCargoProblem:
    cargos = ['C1', 'C2']
    planes = ['P1', 'P2']
    airports = ['JFK', 'SFO']
    pos = [expr('At(C1, SFO)'),
           expr('At(C2, JFK)'),
           expr('At(P1, SFO)'),
           expr('At(P2, JFK)'),
           ]
    neg = [expr('At(C2, SFO)'),
           expr('In(C2, P1)'),
           expr('In(C2, P2)'),
           expr('At(C1, JFK)'),
           expr('In(C1, P1)'),
           expr('In(C1, P2)'),
           expr('At(P1, JFK)'),
           expr('At(P2, SFO)'),
           ]
    init = FluentState(pos, neg)
    goal = [expr('At(C1, JFK)'),
            expr('At(C2, SFO)'),
            ]
    return AirCargoProblem(cargos, planes, airports, init, goal)

"""
- Problem 2 initial state and goal:

Init(At(C1, SFO) ∧ At(C2, JFK) ∧ At(C3, ATL) 
    ∧ At(P1, SFO) ∧ At(P2, JFK) ∧ At(P3, ATL) 
    ∧ Cargo(C1) ∧ Cargo(C2) ∧ Cargo(C3)
    ∧ Plane(P1) ∧ Plane(P2) ∧ Plane(P3)
    ∧ Airport(JFK) ∧ Airport(SFO) ∧ Airport(ATL))
Goal(At(C1, JFK) ∧ At(C2, SFO) ∧ At(C3, SFO))
"""

def air_cargo_p2() -> AirCargoProblem:
    cargos = ['C1', 'C2', 'C3']
    planes = ['P1', 'P2', 'P3']
    airports = ['JFK', 'SFO', 'ATL']
    pos = [expr('At(C1, SFO)'),
           expr('At(C2, JFK)'),
           expr('At(C3, ATL)'),
           expr('At(P1, SFO)'),
           expr('At(P2, JFK)'),
           expr('At(P3, ATL)'),
           ]
    neg = [expr('At(C2, SFO)'),
           expr('At(C2, ATL)'),
           expr('In(C2, P1)'),
           expr('In(C2, P2)'),
           expr('In(C2, P3)'),
           expr('At(C1, JFK)'),
           expr('At(C1, ATL)'),
           expr('In(C1, P1)'),
           expr('In(C1, P2)'),
           expr('In(C1, P3)'),
           expr('At(C3, SFO)'),
           expr('At(C3, JFK)'),
           expr('In(C3, P1)'),
           expr('In(C3, P2)'),
           expr('In(C3, P3)'),
           expr('At(P1, JFK)'),
           expr('At(P1, ATL)'),
           expr('At(P2, SFO)'),
           expr('At(P2, ATL)'),
           expr('At(P3, SFO)'),
           expr('At(P3, JFK)'),
           ]
    init = FluentState(pos, neg)
    goal = [expr('At(C1, JFK)'),
            expr('At(C2, SFO)'),
            expr('At(C3, SFO)'),
            ]
    return AirCargoProblem(cargos, planes, airports, init, goal)

"""
- Problem 3 initial state and goal:

Init(At(C1, SFO) ∧ At(C2, JFK) ∧ At(C3, ATL) ∧ At(C4, ORD) 
    ∧ At(P1, SFO) ∧ At(P2, JFK) 
    ∧ Cargo(C1) ∧ Cargo(C2) ∧ Cargo(C3) ∧ Cargo(C4)
    ∧ Plane(P1) ∧ Plane(P2)
    ∧ Airport(JFK) ∧ Airport(SFO) ∧ Airport(ATL) ∧ Airport(ORD))
Goal(At(C1, JFK) ∧ At(C3, JFK) ∧ At(C2, SFO) ∧ At(C4, SFO))

"""
def air_cargo_p3() -> AirCargoProblem:
    cargos = ['C1', 'C2', 'C3','C4']
    planes = ['P1', 'P2']
    airports = ['JFK', 'SFO','ATL','ORD']
    pos = [expr('At(C1, SFO)'),
           expr('At(C2, JFK)'),
           expr('At(C3, ATL)'),
           expr('At(C4, ORD)'),
           expr('At(P1, SFO)'),
           expr('At(P2, JFK)'),
           ]
    neg = [expr('At(C1, JFK)'),
           expr('At(C1, ATL)'),
           expr('At(C1, ORD)'),
           expr('In(C1, P1)'),
           expr('In(C1, P2)'),
           expr('At(C2, SFO)'),
           expr('At(C2, ATL)'),
           expr('At(C2, ORD)'),
           expr('In(C2, P1)'),
           expr('In(C2, P2)'),
           expr('At(C3, SFO)'),
           expr('At(C3, JFK)'),
           expr('At(C2, ORD)'),
           expr('In(C3, P1)'),
           expr('In(C3, P2)'),
           expr('At(C4, SFO)'),
           expr('At(C4, JFK)'),
           expr('At(C4, ATL)'),
           expr('In(C4, P1)'),
           expr('In(C4, P2)'),
           expr('At(P1, JFK)'),
           expr('At(P1, ATL)'),
           expr('At(P1, ORD)'),
           expr('At(P2, SFO)'),
           expr('At(P2, ATL)'),
           expr('At(P2, ORD)'),
           ]
    init = FluentState(pos, neg)
    goal = [expr('At(C1, JFK)'),
            expr('At(C2, SFO)'),
            expr('At(C3, JFK)'),
            expr('At(C4, SFO)'),
            ]
    return AirCargoProblem(cargos, planes, airports, init, goal)