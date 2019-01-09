"""Finish all TODO items in this file to complete the isolation project, then
test your agent's strength against a set of known agents using tournament.py
and include the results in your report.
"""
import math


class SearchTimeout(Exception):
    """Subclass base exception for code clarity. """
    pass

# a global variable used by custom_score_3
# stores a previously computed maximum distance between players
max_distance_between_players = None

def custom_score_3(game, player):
    """Calculate the heuristic value of a game state from the point of view
    of the given player.

    Note: this function should be called from within a Player instance as
    `self.score()` -- you should not need to call this function directly.
    
    Strategy
    ---------
   heuristic with Manhattan dist: This heuristic takes the distance between the two players and minimizes it. Manhattan distance method is used to calculate the distance between the two squares (as they can move in L-shaped fashion, and this way of measuring is close to approximating that). The idea behind this heuristic is, typically the distance between the players gets smaller towards the end of the game. An adversarial agent would try to block the moves of the opponent, and will be actively trying to get closer to them as the result.
    
    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    -------
    float
        The heuristic value of the current game state to the specified player.
    """
    global max_distance_between_players
    if game.move_count <= 5:
        #tournament.py tries to initialize two random moves for both players
        #before calling AB 
        max_distance_between_players = None
        
    own_moves = len(game.get_legal_moves(player))
    opp_moves = len(game.get_legal_moves(game.get_opponent(player)))
    
    if opp_moves == 0:
        return float("inf")
    elif own_moves == 0:
        return float("-inf")
    else :  
        #get the center of the board
        center_y_pos, center_x_pos = game.height // 2,  game.width // 2
        #get the current location of active player
        player_y_pos, player_x_pos = game.get_player_location(player)
        #get the current location of opponent
        opponent_y_pos, opponent_x_pos = game.get_player_location(game.get_opponent(player))
        #compute the Manhattan Distance of player from center
        curr_player_distance = abs(player_y_pos - opponent_y_pos) + abs(player_x_pos - opponent_x_pos)
        if max_distance_between_players is None:
            #first time around return the current distance amplified by the move count
            score = float(curr_player_distance) * game.move_count
            max_distance_between_players = curr_player_distance
        else :    
            # return the change in distance resulting from current move by subtracting
            # from previously recorded one. Amplify the score by the move count in the game
            score = float(max_distance_between_players - curr_player_distance) * game.move_count
            if curr_player_distance < max_distance_between_players:
                max_distance_between_players = curr_player_distance
            
        return score
        

def custom_score(game, player):
    """Calculate the heuristic value of a game state from the point of view
    of the given player.

    Note: this function should be called from within a Player instance as
    `self.score()` -- you should not need to call this function directly.
    
    Strategy
    ---------
   Increasing aggressivity: Given that blocking the opponent is not really feasible at the beginning of the match, we concentrate on preserving our own mobility at first, then gradually increase the focus on limiting the opponent's moves.
(1 - gameratio) own moves 4.0 - game ratio * opp moves
where game ratio is the approximate completion of the game (increasing over time).
This seems to provide a more balanced solution to the problem by concentrating on
what really matters throught the game ( 65% success against other heuristics)
    
    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    -------
    float
        The heuristic value of the current game state to the specified player.
    """
    
    own_moves = len(game.get_legal_moves(player))
    opp_moves = len(game.get_legal_moves(game.get_opponent(player)))
    
    score = 0
    if opp_moves == 0:
        return float("inf")
    elif own_moves == 0:
        return float("-inf")
    else :
        gameratio = game.move_count / (game.height * game.width)
        #preserving our own mobility at first, then gradually increase the focus on 
        #limiting the opponent's moves. 
        return float((1 - gameratio) * own_moves * 4.0 - gameratio * opp_moves)
    
def custom_score_2(game, player):
    """Calculate the heuristic value of a game state from the point of view
    of the given player.

    Note: this function should be called from within a Player instance as
    `self.score()` -- you should not need to call this function directly.
    
   Strategy
    ---------
     Defending mobility : This first heuristic is a variant of the basic cost/benefit analysis.
In this variant, we prioritize our own mobility over obstruction of the opponent by computing:
2 * own_moves - opp moves
This gives results similar to our baseline ID_improved player ( 60% success against other heuristics).
    
    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    -------
    float
        The heuristic value of the current game state to the specified player.
    """
    if game.is_loser(player):
        return float("-inf")

    if game.is_winner(player):
        return float("inf")

    own_moves = len(game.get_legal_moves(player))
    opp_moves = len(game.get_legal_moves(game.get_opponent(player)))
    return float(2 * own_moves - opp_moves)  
    
def reviewer_custom_score_4(game, player):
    """Calculate the heuristic value of a game state from the point of view
    of the given player.

    Note: this function should be called from within a Player instance as
    `self.score()` -- you should not need to call this function directly.
    
    Strategy
    ---------
   This is a variant of ID_Improved where we try to restrict the opponent early on (Initial Game) by choosing moves where own moves are a factor X more than the opponent and gradually reduce the factor X as we move towards Mid and End Game and concentrate on own mobility in Mid to End game.

    
    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    -------
    float
        The heuristic value of the current game state to the specified player.
    """
    
     # get current move count
    move_count = game.move_count

    # count number of moves available
    own_moves = len(game.get_legal_moves(player))
    opp_moves = len(game.get_legal_moves(game.get_opponent(player)))

    # calculate weight
    w = 10 / (move_count + 1)

    # return weighted delta of available moves
    return float(own_moves - (w * opp_moves))  


class IsolationPlayer:
    """Base class for minimax and alphabeta agents -- this class is never
    constructed or tested directly.

    ********************  DO NOT MODIFY THIS CLASS  ********************

    Parameters
    ----------
    search_depth : int (optional)
        A strictly positive integer (i.e., 1, 2, 3,...) for the number of
        layers in the game tree to explore for fixed-depth search. (i.e., a
        depth of one (1) would only explore the immediate sucessors of the
        current state.)

    score_fn : callable (optional)
        A function to use for heuristic evaluation of game states.

    timeout : float (optional)
        Time remaining (in milliseconds) when search is aborted. Should be a
        positive value large enough to allow the function to return before the
        timer expires.
    """
    def __init__(self, search_depth=3, score_fn=custom_score, timeout=10.):
        self.search_depth = search_depth
        self.score = score_fn
        self.time_left = None
        self.TIMER_THRESHOLD = timeout
        self.last_selected_move = None

class MinimaxPlayer(IsolationPlayer):
    """Game-playing agent that chooses a move using depth-limited minimax
    search. You must finish and test this player to make sure it properly uses
    minimax to return a good move before the search time limit expires.
    """
    
    def terminal_test(self, game, depth):
        if self.time_left() < self.TIMER_THRESHOLD:
            raise SearchTimeout()   
        terminalNode = not game.get_legal_moves()
        if depth == 0  or terminalNode:
            return True
        return False
   
    def min_value(self,game, depth):
        if self.time_left() < self.TIMER_THRESHOLD:
            raise SearchTimeout()
            
        if self.terminal_test(game, depth):  
            return self.score(game, self)
        
        v = float('inf')
        for a in game.get_legal_moves():
            v = min(v, self.max_value(game.forecast_move(a), depth - 1))
        return v
    
    def max_value(self, game, depth):
        if self.time_left() < self.TIMER_THRESHOLD:
            raise SearchTimeout()
            
        if self.terminal_test(game, depth):
            return self.score(game, self)
        
        v = float('-inf')
        for a in game.get_legal_moves():
            v = max(v, self.min_value(game.forecast_move(a), depth - 1))
        return v

  
    def get_move(self, game, time_left):
        """Search for the best move from the available legal moves and return a
        result before the time limit expires.

        **************  YOU DO NOT NEED TO MODIFY THIS FUNCTION  *************

        For fixed-depth search, this function simply wraps the call to the
        minimax method, but this method provides a common interface for all
        Isolation agents, and you will replace it in the AlphaBetaPlayer with
        iterative deepening search.

        Parameters
        ----------
        game : `isolation.Board`
            An instance of `isolation.Board` encoding the current state of the
            game (e.g., player locations and blocked cells).

        time_left : callable
            A function that returns the number of milliseconds left in the
            current turn. Returning with any less than 0 ms remaining forfeits
            the game.

        Returns
        -------
        (int, int)
            Board coordinates corresponding to a legal move; may return
            (-1, -1) if there are no available legal moves.
        """
        self.time_left = time_left

        # Initialize the best move so that this function returns something
        # in case the search fails due to timeout
        best_move = (-1, -1)

        try:
            # The try/except block will automatically catch the exception
            # raised when the timer is about to expire.
            best_move = self.minimax(game, self.search_depth)

        except SearchTimeout:
            pass  # Handle any actions required after timeout as needed
        
        # Return the best move from the last completed search iteration
        return best_move

    
        
    def minimax(self, game, depth):
        """Implement depth-limited minimax search algorithm as described in
        the lectures.

        This should be a modified version of MINIMAX-DECISION in the AIMA text.
        https://github.com/aimacode/aima-pseudocode/blob/master/md/Minimax-Decision.md

        **********************************************************************
            You MAY add additional methods to this class, or define helper
                 functions to implement the required functionality.
        **********************************************************************

        Parameters
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        Returns
        -------
        (int, int)
            The board coordinates of the best move found in the current search;
            (-1, -1) if there are no legal moves

        Notes
        -----
            (1) You MUST use the `self.score()` method for board evaluation
                to pass the project tests; you cannot call any other evaluation
                function directly.

            (2) If you use any helper functions (e.g., as shown in the AIMA
                pseudocode) then you must copy the timer check into the top of
                each helper function or else your agent will timeout during
                testing.
        """ 
        
        if self.time_left() < self.TIMER_THRESHOLD:
            raise SearchTimeout()
        # Body of minimax: as defined in AIMA
        return max(game.get_legal_moves(),
               key=lambda a: self.min_value(game.forecast_move(a), depth -1), default=(-1,-1))  
                
            

class AlphaBetaPlayer(IsolationPlayer):
    """Game-playing agent that chooses a move using iterative deepening minimax
    search with alpha-beta pruning. You must finish and test this player to
    make sure it returns a good move before the search time limit expires.
    """

    def terminal_test(self, game, depth, depthLimit):
        if self.time_left() < self.TIMER_THRESHOLD:
            raise SearchTimeout()
        #if no legal moves left     
        terminalNode = not game.get_legal_moves()
        #if we have crossed the depth limit
        if depth >= depthLimit  or terminalNode:
            return True
        return False
    
    # Functions used by alphabeta
    def max_value(self, game, alpha, beta, depth, depthLimit):
        if self.time_left() < self.TIMER_THRESHOLD:
            raise SearchTimeout()
        
        #if no legal moves or reached depthlimit return the score
        if self.terminal_test(game, depth, depthLimit):
            return self.score(game, self)
        
        v = float('-inf')
        for a in game.get_legal_moves():
            #compute the max of min values at the next level
            v = max(v, self.min_value(game.forecast_move(a),
                                 alpha, beta, depth + 1, depthLimit))    
            # found a value greater than or equal to Beta so no need to
            # explore the remaining moves
            if v >= beta:
                return v
            #Alpha is the maximum lower bound 
            alpha = max(alpha, v)
        return v

    def min_value(self,game, alpha, beta, depth, depthLimit):
        if self.time_left() < self.TIMER_THRESHOLD:
            raise SearchTimeout()
            
        #if no legal moves or reached depthlimit return the score
        if self.terminal_test(game, depth, depthLimit):
            return self.score(game, self)    
        
        v = float('inf')
        for a in game.get_legal_moves():
            #compute the min of max values at the next level 
            v = min(v, self.max_value(game.forecast_move(a),
                                 alpha, beta, depth + 1, depthLimit))
            # found a value less than or equal to Alpha so no need to
            # explore the remaining moves
            if v <= alpha:
                return v
            #Beta is the minimum upper bound 
            beta = min(beta, v)
        return v

    
    def get_move(self, game, time_left):
        """Search for the best move from the available legal moves and return a
        result before the time limit expires.

        Modify the get_move() method from the MinimaxPlayer class to implement
        iterative deepening search instead of fixed-depth search.

        **********************************************************************
        NOTE: If time_left() < 0 when this function returns, the agent will
              forfeit the game due to timeout. You must return _before_ the
              timer reaches 0.
        **********************************************************************

        Parameters
        ----------
        game : `isolation.Board`
            An instance of `isolation.Board` encoding the current state of the
            game (e.g., player locations and blocked cells).

        time_left : callable
            A function that returns the number of milliseconds left in the
            current turn. Returning with any less than 0 ms remaining forfeits
            the game.

        Returns
        -------
        (int, int)
            Board coordinates corresponding to a legal move; may return
            (-1, -1) if there are no available legal moves.
        """
        self.time_left = time_left
        
        # Initialize the best move so that this function returns something
        # in case the search fails due to timeout
        best_move = (-1, -1)
        d = 0
        try:
            # The try/except block will automatically catch the exception
            # raised when the timer is about to expire.
            # the maximum depth to search until end-game
            limit = (game.width * game.height) + 1
            for d in range(1,limit):
                temp_move = self.alphabeta(game, d)
                if temp_move != (-1,-1):
                    #store the best move so far to be returned 
                    #either upon search till end-game or a timeout
                    best_move = temp_move

        except SearchTimeout:
            pass  # Handle any actions required after timeout as needed
        
        #used by custom score 3
        self.last_selected_move = best_move
        # Return the best move from the last completed search iteration
        return best_move

    def alphabeta(self, game, depth, alpha=float("-inf"), beta=float("inf")):
        """Implement depth-limited minimax search with alpha-beta pruning as
        described in the lectures.

        This should be a modified version of ALPHA-BETA-SEARCH in the AIMA text
        https://github.com/aimacode/aima-pseudocode/blob/master/md/Alpha-Beta-Search.md

        **********************************************************************
            You MAY add additional methods to this class, or define helper
                 functions to implement the required functionality.
        **********************************************************************

        Parameters
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        alpha : float
            Alpha limits the lower bound of search on minimizing layers

        beta : float
            Beta limits the upper bound of search on maximizing layers

        Returns
        -------
        (int, int)
            The board coordinates of the best move found in the current search;
            (-1, -1) if there are no legal moves

        Notes
        -----
            (1) You MUST use the `self.score()` method for board evaluation
                to pass the project tests; you cannot call any other evaluation
                function directly.

            (2) If you use any helper functions (e.g., as shown in the AIMA
                pseudocode) then you must copy the timer check into the top of
                each helper function or else your agent will timeout during
                testing.
        """
        if self.time_left() < self.TIMER_THRESHOLD:
            raise SearchTimeout()
        
        legal_moves = game.get_legal_moves()
        best_action = None
        
        #if no legal moves left exit
        if len(legal_moves) == 0:
            return (-1, -1)
        else:
            #start with first one
            best_action = legal_moves[0]
 
        for a in game.get_legal_moves():
            v = self.min_value(game.forecast_move(a), alpha, beta, 1, depth)
            if v > alpha:
                #adjust Alpha to the maximum of min values
                alpha = v
                best_action = a
        return best_action  
    
    
    
   
        
