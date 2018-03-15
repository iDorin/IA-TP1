#!/usr/bin/env python3

## Solve Every Sudoku Puzzle

## See http://norvig.com/sudoku.html

## Throughout this program we have:
##   r is a row,    e.g. 'A'
##   c is a column, e.g. '3'
##   s is a square, e.g. 'A3'
##   d is a digit,  e.g. '9'
##   u is a unit,   e.g. ['A1','B1','C1','D1','E1','F1','G1','H1','I1']
##   grid is a grid,e.g. 81 non-blank chars, e.g. starting with '.18...7...
##   values is a dict of possible values, e.g. {'A1':'12349', 'A2':'8', ...}


def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [a+b for a in A for b in B]

digits   = '123456789'
rows     = 'ABCDEFGHI'
cols     = digits
squares  = cross(rows, cols)   # 'A1', 'A2',...
unitlist = ([cross(rows, c) for c in cols] +
            [cross(r, cols) for r in rows] +
            [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')])
units = dict((s, [u for u in unitlist if s in u])   # carre 9x9, ligne complete, colonne complete
             for s in squares)
peers = dict((s, set(sum(units[s],[]))-set([s]))   # unit squares
             for s in squares)

# Initialisation de la liste de quadrants qui va contenir les valeurs initiales
Quadrants_defaults = []

Quadrants  = []
strategie  = 'Norvig'
tentatives = 1


################ Unit Tests ################

def test():
    "A set of tests that must pass."
    assert len(squares) == 81
    assert len(unitlist) == 27
    assert all(len(units[s]) == 3 for s in squares)
    assert all(len(peers[s]) == 20 for s in squares)
    assert units['C2'] == [['A2', 'B2', 'C2', 'D2', 'E2', 'F2', 'G2', 'H2', 'I2'],
                           ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9'],
                           ['A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'C1', 'C2', 'C3']]
    assert peers['C2'] == set(['A2', 'B2', 'D2', 'E2', 'F2', 'G2', 'H2', 'I2',
                               'C1', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9',
                               'A1', 'A3', 'B1', 'B3'])
    print('All tests pass.')

################ Parse a Grid ################

# Retourne le dict. de valeurs final
def parse_grid(grid):
    """Convert grid to a dict of possible values, {square: digits}, or
    return False if a contradiction is detected."""
    ## To start, every square can be any digit; then assign values from the grid.
    global tentatives

    if strategie is 'HillClimbing':
        values = dict(grid_values(grid).items()) # Etat initial en forme de lst de tuples)
        makeQuadrants()                    # Cree betement les quadrants
        setQuadrantsDefaults(Quadrants, values)  # Remplit puzzle avec valeurs initiales
        
        # Generate Quadrants free values
        Quadrants_freevals = Quadrants_defaults.copy()
        for i in range(len(Quadrants_defaults)):
            Quadrants_freevals[i] = set(digits) - set(Quadrants_defaults[i])
    else:
        values = dict((s, digits) for s in squares)
   
    for s,d in list(grid_values(grid).items()):   # s - key, d - value  # Etat initial en forme de dict.
        #tentatives += 1
        if strategie is 'HillClimbing':
            q = getQuadrantNb(s, Quadrants)
            # Put numbers on free places
            if len(Quadrants_freevals[q]) > 0 and d in '0.':
                values[s] = Quadrants_freevals[q].pop()
        else:
            if d in digits and not assign(values, s, d):
                return False ## (Fail if we can't assign d to square s.)

    return values


################ Constraint Propagation ################

def assign(values, s, d):

    global tentatives

    """Eliminate all the other values (except d) from values[s] and propagate.
    Return values, except return False if a contradiction is detected."""
    other_values = values[s].replace(d, '')
    if all(eliminate(values, s, d2) for d2 in other_values):
        tentatives += 1
        return values
    else:
        return False

# Elimine les chiffres. Si nb d'une seule chiffre, return False.
# Transforme '123456789' -> '3'
def eliminate(values, s, d):
    """Eliminate d from values[s]; propagate when values or places <= 2.
    Return values, except return False if a contradiction is detected."""
    if d not in values[s]:
        return values ## Already eliminated
    values[s] = values[s].replace(d,'')

    ## (1) If a square s is reduced to one value d2, then eliminate d2 from the peers.
    if len(values[s]) == 0:
        return False ## Contradiction: removed last value
    elif len(values[s]) == 1:
        
        d2 = values[s]
        if not all(eliminate(values, s2, d2) for s2 in peers[s]):
            return False

    ## (2) If a unit u is reduced to only one place for a value d, then put it there.
    for u in units[s]:
        dplaces = [s for s in u if d in values[s]] # Ex.: liste ['G6',...]
        if len(dplaces) == 0:
            return False ## Contradiction: no place for this value
        elif len(dplaces) == 1:
            if not assign(values, dplaces[0], d):
                return False

    return values

################ Display as 2-D grid ################

def display(values):
    "Display these values as a 2-D grid."
    width = 1+max(len(values[s]) for s in squares)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    print()


################ Search ################

def solve(grid):
    return search(parse_grid(grid))

def search(values):
    "Using depth-first search and propagation, try all possible values."
    #print(values)
    if values is False:
        return False ## Failed earlier
    if all(len(values[s]) == 1 for s in squares):
        return values ## Solved!
    ## Chose the unfilled square s with the fewest possibilities
    n,s = min((len(values[s]), s) for s in squares if len(values[s]) > 1)
    return some(search(assign(values.copy(), s, d))
                for d in values[s])


################ Methodes pour Hill Climbing ################

# Liste de 9 Quadrants
def makeQuadrants():
    global Quadrants
    Quadrants = []
    quadrant = [] # un quadrant contient  une liste de cases
    width = len(rows)
    n = len(squares)
    for i in range(0, n, n//3):
        for j in range(i, i+width, width//3):
            quadrant = []
            for k in range(j, i+n//3, width):
                quadrant += squares[k : k+width//3]
            Quadrants.append(quadrant)

# Remplit la liste de valeurs initiales pour chaque quadrant
def setQuadrantsDefaults(Quadrants, values):
    # Collecte les digits predefinies pour chaque quadrant dans une liste
    global Quadrants_defaults
    Quadrants_defaults = []
    for i in range(len(Quadrants)):
        str = ''
        for j in Quadrants[i]:
            if values[j] != '0' and values[j] != '.':
                str += values[j]
        Quadrants_defaults.append(str)

# Retourne le no. du quadrant ou se trouve la cle s
def getQuadrantNb(s, Quadrants):
    # Determine le numero du quadrant, 9 au total
    q = 0 # numero du quadrant
    for i in range(len(Quadrants)):
        for j in Quadrants[i]:
            if s == j:
                q = i
    return q

# Retourne grid en forme de dict. (etat initial)
def grid_values(grid):
    "Convert grid into a dict of {square: char} with '0' or '.' for empties."
    chars = [c for c in grid if c in digits or c in '0.']
    assert len(chars) == 81
    gridDict = dict(list(zip(squares, chars)))
    return gridDict


### Calcule le score ###

def getScore(values):
    # Extracting lines & return score for lines
    def getRowScore(lst):
        score = 0 # nb d'elems corrects
        width = len(rows) # largeur de l'echiquier
        for i in range(0, len(lst), width): # iteration sur toutes les elems du dictionnaire
            row = lst[i : i + width] # row contient une liste de 9 tuples 
            rowPeers = ''
            for j in range(len(row)): # recuperation valeurs d'un row
                if row[j][1] != '0':
                    rowPeers += row[j][1]
            score += len(set(rowPeers)) # Calcule score. Car c'est un set, elimine les valeurs egales
        return score

    # Extracting cols & return score for cols
    def getColScore(lst):
        score = 0 # nb d'elems corrects
        width = len(rows) # largeur de l'echiquier
        for i in range(width):
            col = list()
            for j in range(i, len(lst), width):
                if lst[j][1] != '0':
                    col.append(lst[j][1])
            score += len(set(col)) # Calcule score. Car c'est un set, elimine les valeurs egales
        return score

    # Extracting squares & return score for squares (1 square = 9 atomic elements)
    def getSquareScore(lst):
        score = 0
        width = len(rows)
        n = len(lst)
        for i in range(0, n, n//3):
            for j in range(i, i+width, width//3):
                square = list()
                for k in range(j, i+n//3, width):
                    square += lst[k : k+width//3]
                squareSet = set()
                for kk in range(width):
                    if square[kk][1] != '0':
                        squareSet.add(square[kk][1])
                score += len(squareSet)
        return score

    lst = sorted(list(values.items()))
    return getRowScore(lst) + getColScore(lst) + getSquareScore(lst) # -2

# Retourne l'etat successeur
def successor(values, Qindex):
    neighbor = values.copy()
    # Cherche cases selon les contraintes
    while True:
        index1 = random.randint(0, 8)
        index2 = random.randint(0, 8)

        # Picking 2 elems to swap
        s1 = Quadrants[Qindex][index1] # Donne 'A1' p.e.
        s2 = Quadrants[Qindex][index2]
        fixedDigits = Quadrants_defaults[Qindex]
        if (index1 == index2) or (neighbor[s1] in fixedDigits) or (neighbor[s2] in fixedDigits):
            continue
        else:
            # Swap 2 elements
            temp = neighbor[s1]
            neighbor[s1] = neighbor[s2]
            neighbor[s2] = temp
            break
    return neighbor

#### Solution par HILL CLIMBING ###
def solveHillClimbing(grid):
    global strategie
    global tentatives
    strategie = 'HillClimbing'

    # Etat initial, mais avec des valeurs init, en respectant les contraintes
    currentState = parse_grid(grid) 

    # Boucle HC
    while True: # boucle pour puzzle complet
        tentatives += 1
        Qindex = random.randint(0, 8)
        neighborState = successor(currentState, Qindex)
        #print('Neighbor score:',getScore(neighborState),', current score:', getScore(currentState))
        if getScore(neighborState) <= getScore(currentState):
            return currentState
        currentState = neighborState.copy()

    return currentState

################ END Methodes pour Hill Climbing ################


################ Utilities ################

def some(seq):
    "Return some element of seq that is true."
    for e in seq:
        if e: return e
    return False

def from_file(filename, sep='\n'):
    "Parse a file into a list of strings, separated by sep."
    return open(filename).read().strip().split(sep)

def shuffled(seq):
    "Return a randomly shuffled copy of the input sequence."
    seq = list(seq)
    random.shuffle(seq)
    return seq

################ System test ################

def resetTentatives():
    global tentatives
    tentatives = 1

import time, random

def solve_all(grids, name='', showif=0.0, strategie='Norvig'):
    """Attempt to solve a sequence of grids. Report results.
    When showif is a number of seconds, display puzzles that take longer.
    When showif is None, don't display any puzzles."""
    def time_solve(grid):
        start = time.clock()
        if strategie is "HillClimbing":
            values = solveHillClimbing(grid)
        else:
            values = solve(grid)
        t = time.clock()-start
        ## Display puzzles that take long enough
        if showif is not None and t > showif:
            display(grid_values(grid))
            if values: display(values)
            print('(%.2f seconds)\n' % t)
        return (t, solved(values))
    times, results = list(zip(*[time_solve(grid) for grid in grids]))
    N = len(grids)
    if N > 1:
        print("Solved %d of %d %s puzzles (avg %.2f secs (%d Hz), max %.2f secs)." % (
            sum(results), N, name, sum(times)/N, N/sum(times), max(times)))
    print(' Strategie: ', strategie)
    print(' Tentatives:', tentatives)
    resetTentatives()

def solved(values):
    "A puzzle is solved if each unit is a permutation of the digits 1 to 9."
    def unitsolved(unit): return set(values[s] for s in unit) == set(digits)
    return values is not False and all(unitsolved(unit) for unit in unitlist)

# Genere une grille initiale aleatoire
def random_puzzle(N=17):
    """Make a random puzzle with N or more assignments. Restart on contradictions.
    Note the resulting puzzle is not guaranteed to be solvable, but empirically
    about 99.8% of them are solvable. Some have multiple solutions."""
    "N, nb de cases completes, max 81"
    values = dict((s, digits) for s in squares) # fait {'H2': '123456789',...}
    for s in shuffled(squares):
        if not assign(values, s, random.choice(values[s])): # gen. nbres aleat a partir de la config.
            break
        ds = [values[s] for s in squares if len(values[s]) == 1] # ds = ['2', '5', '5', '1'] etc.
        if len(ds) >= N and len(set(ds)) >= 8:
            return ''.join(values[s] if len(values[s])==1 else '.' for s in squares)
    return random_puzzle(N) ## Give up and make a new puzzle

grid1  = '003020600900305001001806400008102900700000008006708200002609500800203009005010300'
grid2  = '4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......'
hard1  = '.....6....59.....82....8....45........3........6..3.54...325..6..................'
    
if __name__ == '__main__':
    test()
    #solve_all(from_file("easy50.txt", '========'), "easy", None)
    #solve_all(from_file("easy1.txt", '========'), "easySimple", None)
    #solve_all(from_file("top95.txt"), "hard", None)
    #solve_all(from_file("hardest.txt"), "hardest", None)
    #solve_all([random_puzzle() for _ in range(99)], "random", 100.0)
    
    #solve_all(from_file("easy1.txt", '========'), "easy1Simple", 0)
    #solve_all(from_file("easy2.txt", '========'), "easy2Simple", 0, "HillClimbing")

    # Solution par l'implantation du Norvig
    solve_all(from_file("100sudoku.txt"), "100sudoku.txt", None, "Norvig")

    # Solution par la strategie Hill Climbing
    solve_all(from_file("100sudoku.txt"), "100sudoku.txt", None, "HillClimbing")
    

## References used:
## http://www.scanraid.com/BasicStrategies.htm
## http://www.sudokudragon.com/sudokustrategy.htm
## http://www.krazydad.com/blog/2005/09/29/an-index-of-sudoku-strategies/
## http://www2.warwick.ac.uk/fac/sci/moac/currentstudents/peter_cock/python/sudoku/