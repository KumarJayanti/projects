import collections
import logging

rows = 'ABCDEFGHI'
cols = '123456789'

assignments = []

def cross(a, b):
    return [s+t for s in a for t in b]

boxes = cross(rows, cols)

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
unitlist = row_units + column_units + square_units
diagonal_units = [[r+c for r,c in zip(rows,cols)], [r+c for r,c in zip(rows,cols[::-1])]]
unitlist = row_units + column_units + square_units + diagonal_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)
diagonal_square_units=[square_units[0],square_units[2],square_units[4],square_units[6],square_units[8]]

def display(values):
    """
    Display the values as a 2-D grid.
    Input: The sudoku in dictionary form
    Output: None
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return


def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Input: A grid in string form.
    Output: A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    chars = []
    digits = '123456789'
    for c in grid:
        if c in digits:
            chars.append(c)
        if c == '.':
            chars.append(digits)
    assert len(chars) == 81
    return dict(zip(boxes, chars))
    
def has_duplicates(values, unit):
    """
    check if a unit has duplicate values.
    Input:  values: the sudoku in dict form, unit the unit in which to check for duplicates
    Output: True if there are duplicates in a unit (can occur after an elimination step)
    """
    v = [values[x] for x in unit if len(values[x]) == 1]
    vd = [item for item, count in collections.Counter(v).items() if count > 1]
    if len(vd) > 0:
        return True
    return False

def units_violated(values, box):
    """
    check if the units of a box are in violation of the sudoku rules
    Input:  values: the sudoku in dict form, box: the box whose units are to be checked
    Output: True if a unit in which the box is a part has sudoku rules violated (can occur after an elimination/only_choice assignment step)
    """
    for unit in units[box]:
        if has_duplicates(values, unit):
            return True;
    return False
        
def subset(places, unit):
    return set(places).issubset(set(unit))

def on_same_square_unit(dplaces):
    result = [u for u in diagonal_square_units if subset(dplaces, u)]
    if len(result) == 0:
        return False
    return result[0]

def get_twins(unit,values, number):
    """ return twin values or []
    Args: 
        values(dict): a dictionary of the form {'box_name': '123456789', ...}
        unit : a row/column/square unit
    Returns:
        twins if present
    """
    unitValues = [values[u] for u in unit]
    twins = [item for item, count in collections.Counter(unitValues).items() if count == number]
    result = [x for x in twins if len(x) == number]
    return result


def diagonal_violated(values):
    """
    Input: A sudoku in dictionary form.
    Output: True if a diagonal rule is violated in the sudoku. Called form search() to validate a possible solution found by search.
    """
    for u in diagonal_units:
        if has_duplicates(values, u):
            return True 
    return False


def check_diagonal(values, box, value):
    """
    Input: A sudoku in dictionary form, the box to which search is trying to assign a fixed value
    Output: True if assignment of 'value' to the specified 'box' will lead to diagonal rule violation. Called form search() to prune the search space at the point when it makes a fixed value assignment.
    """
    if box in diagonal_units[0]:
        for s in diagonal_units[0]:
            if values[s] == value:
                return False
    if box in diagonal_units[1]:
        for s in diagonal_units[1]:
            if values[s] == value:
                return False
    return True

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values


def eliminate(values):
    """
    Go through all the boxes, and whenever there is a box with a value, eliminate this value from the values of all its peers.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in peers[box]:
            if len(values[peer]) > 1:
                assign_value(values,peer, values[peer].replace(digit,''));
    return values

def only_choice(values):
    """
    Go through all the units, and whenever there is a unit with a value that only fits in one box, assign the value to this box.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                v = values[dplaces[0]]
                assign_value(values, dplaces[0], digit)
                # bcktrack and return False if this only_choice determination results in duplicates in a unit of the box
                if units_violated(values,dplaces[0]):
                    assign_value(values,dplaces[0],v)
                    return False
    return values

def eliminate_from_non_diag(squnit, digit, dplaces, values):
    peer_boxes = set(squnit) - set(dplaces)
    for p in peer_boxes:
        if len(values[p]) > 1:
            v = values[p];
            assign_value(values,p, values[p].replace(digit,''));
            # bcktrack and return False if this elimination results in duplicates in a unit of the box
            if units_violated(values, p):
                assign_value(values,p,v)
                return False
    return values
        
def box_line_step(digit, dplaces, values):
    if len(dplaces) > 1:
        squnit = on_same_square_unit(dplaces)
        if squnit != False:
            v = eliminate_from_non_diag(squnit,digit,dplaces,values)
            if v != False:
                values = v
    return values


def box_line_reduction(values):
    for digit in '123456789':
        ldplaces = [box for box in diagonal_units[0] if digit in values[box]]
        rdplaces = [box for box in diagonal_units[1] if digit in values[box]]
        values = box_line_step(digit, ldplaces, values)
        values = box_line_step(digit,rdplaces, values)
    return values
        

def eliminate_from_peers(unit, twin, values):
    """Eliminate from peers the values that occur in the twin
    Inputs: the unit and the twin in question along with the sudoku
    """
    unitPeers = [box for box in unit if values[box] not in twin]
    for c in twin:
        for u in unitPeers:
            v = values[u].replace(c,'')
            assign_value(values, u, v)
    return values

def naked_twins(values):
    # We have to iterate through all units until there are no more twins to be found. The way we do that is to compare the board before
    # and after the naked twins detection. If the board is the same then no new twins have been found. We have to do it in a while loop
    # because we might uncover new twins when possible values are removed from peers
    no_more_twins = False

    while not no_more_twins:
        board_before = values        
        for u in unitlist:
            tuples = [(values[b],b) for b in u if len(values[b]) == 2]
            twins_dict = dict()
            if len(tuples) > 0:
                for t in tuples:
                    if t[0] in twins_dict.keys():
                        twins_dict[t[0]].append(t[1])
                    else:
                        twins_dict[t[0]] = [t[1]]
                twins = [twins_dict[x] for x in twins_dict.keys() if len(twins_dict[x]) == 2]    
                if len(twins) > 0:
                    for tw in twins:
                        values = eliminate_from_peers(u, values[tw[0]],values)
        board_after = values
        # if boards before and after naked twin detection are the same then there are no more twins thus we end the while loop
        if board_before == board_after:
            no_more_twins = True
    return values


def naked_pairs(values, number):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked pairs eliminated from peers.
    """
    # Find all instances of naked twins
    unitsWithTwins = [ u for u in unitlist if len(get_twins(u,values,number)) > 0]
    # Eliminate the naked twins as possibilities for their peers
    for u in unitsWithTwins:
        twins = get_twins(u,values,number)
        for t in twins:
            values = eliminate_from_peers(u, t,values)
    return values

def reduce_puzzle(values):
    """
    Iterate eliminate() and only_choice(). If at some point, there is a box with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same, return the sudoku.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    stalled = False
    while not stalled:
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        values = eliminate(values)
        if values == False:
            return False
        values = naked_pairs(values,4)
        values = naked_pairs(values,3)
        values = naked_twins(values)
        values = box_line_reduction(values)
        values = only_choice(values)
        if values == False:
            return False
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        stalled = solved_values_before == solved_values_after
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values


def search(values):
    "Using depth-first search and propagation, create a search tree and solve the sudoku."
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    # reduce_puzzle can fail once eliminate or only_choice results in sudoku rule violations
    if values is False:
        return False
    if all(len(values[s]) == 1 for s in boxes): 
        # if search found a solution but it violates the diagonal rule, then its not useful for us.
        if diagonal_violated(values):
            return False
        return values 
    # Choose one of the unfilled squares with the fewest possibilities
    n,s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    # Now use recursion to solve each one of the resulting sudokus, and if one returns a value (not False), return that answer!
    for value in values[s]:
        new_sudoku = values.copy()
        # select the value only if diagonal constraint is not violated by the selection: prune the search
        if check_diagonal(values, s, value):
            new_sudoku[s] = value
            result = search(new_sudoku)
            if result:
                return result


def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    values = grid_values(grid)
    # search for the solution
    values = search(values)
    return values


if __name__ == '__main__':
    #diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    #diag_sudoku_grid = '9.1....8.8.5.7..4.2.4....6...7......5..............83.3..6......9................'
    #diag_sudoku_grid = '5.2...8.4...1.....4..9....5......29...........23......8....3..7.....4...1.7...3.9'
    #diag_sudoku_grid = '2..3..4.8........7..147.6.......1...8.......4...2.......7.683..6........3.8..9..5'
    diag_sudoku_grid = '...7.9....85...31.2......7...........1..7.6......8...7.7.........3......85.......'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
