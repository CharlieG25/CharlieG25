import numpy as np 
import time
from TrainingBoards import sudoku4,sudoku5,sudoku6,sudoku7,sudokueasy,sudoku
import copy
from StartingData import startboard,startrowdicts,startcolumndicts,startboxdicts,indices,invalidsudoku




def boxrowcolumndeletes(value,board,coordinates,boxdicts,rowdicts,columndicts):
  for segment1 in range(0,3):
    for segment2 in range(0,3):
      #boxwise
      if value in board[coordinates[0]][coordinates[1]][segment1][segment2]:
        board[coordinates[0]][coordinates[1]][segment1][segment2].remove(value) #remove value from cells in box
        # also remove from relevant dictionaries 
        boxdicts[coordinates[0]][coordinates[1]][value] -= 1
        rowdicts[coordinates[0]][segment1][value] -= 1
        columndicts[coordinates[1]][segment2][value] -= 1 
      #rowwise 
      if value in board[coordinates[0]][segment1][coordinates[2]][segment2]:
        board[coordinates[0]][segment1][coordinates[2]][segment2].remove(value) # remove value from cells in row
        # also remove from relevant dictionaries 
        boxdicts[coordinates[0]][segment1][value] -= 1
        rowdicts[coordinates[0]][coordinates[2]][value] -= 1
        columndicts[segment1][segment2][value] -= 1
      # columnwise
      if value in board[segment1][coordinates[1]][segment2][coordinates[3]]:
        board[segment1][coordinates[1]][segment2][coordinates[3]].remove(value) # remove value from cells in column 
        #also remove from relevant dictionaries 
        boxdicts[segment1][coordinates[1]][value] -= 1
        rowdicts[segment1][segment2][value] -= 1
        columndicts[coordinates[1]][coordinates[3]][value] -= 1 


def cellwisedeletes(board,coordinates,boxdicts,rowdicts,columndicts):
  for value in board[coordinates[0]][coordinates[1]][coordinates[2]][coordinates[3]]: 
    if type(value) == int:
      # remove each value other than clue value in relevant ditionaries
      boxdicts[coordinates[0]][coordinates[1]][value] -= 1
      rowdicts[coordinates[0]][coordinates[2]][value] -= 1
      columndicts[coordinates[1]][coordinates[3]][value] -= 1


def placeclue(value,board,coordinates):
  board[coordinates[0]][coordinates[1]][coordinates[2]][coordinates[3]] = [int(value),'found']


def neighboursdelete(value,board,coordinates,boxdicts,rowdicts,columndicts):
  boxrowcolumndeletes(value,board,coordinates,boxdicts,rowdicts,columndicts)
  cellwisedeletes(board,coordinates,boxdicts,rowdicts,columndicts)
  placeclue(value,board,coordinates) 



# takes input board, returns clue values and coordinates for locations in 9x3x3 
def cluelocations(inputboard):
  celllocations = []
  values = [] #pass 9x9
  for rowindex in range(0,9): 
    for columnindex in range(0,9): 
      boxrow = rowindex // 3 
      row = rowindex % 3
      boxcolumn = columnindex // 3
      column = columnindex % 3    
      coordinates = [boxrow,boxcolumn,row,column]
      if inputboard[rowindex][columnindex] > 0: # we leave 'spaces' alone
        value = inputboard[rowindex][columnindex]
        celllocations.append(coordinates)
        values.append(value)
  return celllocations, values


def cluestoninexnine(board):
  ninexnine = np.zeros((9,9)) 
  for coordinates in indices:
    celllist = board[coordinates[0]][coordinates[1]][coordinates[2]][coordinates[3]]
    if len(celllist) == 2: 
      if type(celllist[1]) == str: #only interested in 'found' clues
        row = coordinates[0]*3 + coordinates[2]
        column = coordinates[1]*3 + coordinates[3]
        ninexnine[row][column] = board[coordinates[0]][coordinates[1]][coordinates[2]][coordinates[3]][0]
  return ninexnine

# could refactor dictionary searches so we have a single functon which we pass the dicitonary type.


def boxdictssearch(board,boxdicts):  
  celllocations = []
  values = []
  for boxrow in range(0,3): #boxrows in dictionary
    for boxcolumn in range(0,3): # boxcolumns in dictionary
      for key in range(1,10): 
        if boxdicts[boxrow][boxcolumn][key] == 1: #single candidate 
          # look through specific box for its coordinates 
          for row in range(0,3): 
            for column in range(0,3):
              if key in board[boxrow][boxcolumn][row][column]:
                coordinates = [boxrow,boxcolumn,row,column] 
                celllocations.append(coordinates)
                values.append(key)
  return celllocations, values


def rowdictssearch(board,rowdicts):
  celllocations = []
  values = []
  for boxrow in range(0,3):
    for row in range(0,3):
      for key in range(1,10):
        if rowdicts[boxrow][row][key] == 1:
          for boxcolumn in range(0,3):
            for column in range(0,3):
              if key in board[boxrow][boxcolumn][row][column]:
                coordinates = [boxrow,boxcolumn,row,column]
                celllocations.append(coordinates)
                values.append(key)
  return celllocations, values


def columndictssearch(board,columndicts):
  celllocations = []
  values = [] 
  for boxcolumn in range(0,3):
    for column in range(0,3):
      for key in range(1,10):
        if columndicts[boxcolumn][column][key] == 1:
          for boxrow in range(0,3):
            for row in range(0,3):
              if key in board[boxrow][boxcolumn][row][column]:
                coordinates = [boxrow,boxcolumn,row,column]
                celllocations.append(coordinates)
                values.append(key)
  return celllocations, values


# searches dictionaries for single candidates. Places new clues at these coordinates and deletes neighbours. returns how many candidates found i.e if it was fruitful 
def singlecandidatesearch(board,boxdicts,rowdicts,columndicts):
  fruit = 0

  boxdictsresults = boxdictssearch(board,boxdicts)
  boxdictslocations = boxdictsresults[0]
  boxdictsvalues = boxdictsresults[1]
  for num in range(0,len(boxdictslocations)):
    neighboursdelete(boxdictsvalues[num],board,boxdictslocations[num],boxdicts,rowdicts,columndicts) 
    fruit += 1

  rowdictsresults = rowdictssearch(board,rowdicts)
  rowdictslocations = rowdictsresults[0]
  rowdictsvalues = rowdictsresults[1]
  for num in range(0,len(rowdictslocations)):
    neighboursdelete(rowdictsvalues[num],board,rowdictslocations[num],boxdicts,rowdicts,columndicts) 
    fruit += 1

  columndictsresults = columndictssearch(board,columndicts)
  columndictslocations = columndictsresults[0]
  columndictsvalues = columndictsresults[1]
  for num in range(0,len(columndictslocations)):
    neighboursdelete(columndictsvalues[num],board,columndictslocations[num],boxdicts,rowdicts,columndicts) 
    fruit += 1
  
  return fruit
# this is working 



def printbyrow(board):
  for num1 in range(0,3):
    for num2 in range(0,3):
        print(f'{board[num1][0][num2]}     {board[num1][1][num2]}     {board[num1][2][num2]}')

def printdictsbyrow(dict):
  for row in dict:
    print(row)

def visuals(board,boxdicts,rowdicts,columndicts):
  printbyrow(board)
  print('\n')
  print('boxdicts')
  printdictsbyrow(boxdicts) 
  print('rowdicts')
  printdictsbyrow(rowdicts)
  print('columndicts')
  printdictsbyrow(columndicts)
  print('\n')
  print('\n')

# searches board for best guess opportunity, if there are none that's because the problem is solved and we return an impossible coordinate 3,3,3,3 to signify victory 
# Uses empty cells to detect contradiction, returns impossible coordinates 4,4,4,4
def findguesscoordinates(board):
  fewestvalues = 10 #arbitrary high number 
  for coordinates in indices:
    numpossiblevalues = 0
    for value in board[coordinates[0]][coordinates[1]][coordinates[2]][coordinates[3]]:
      if type(value) == int:
        numpossiblevalues +=1 
    #detecting contradictions this way is slow (waits till we reach a 'locked' state that includes a contradiction, rather than immediately when the contradiction 'arises' through CP). Should be part of CP function, will change if time. Should also try to understan exactly why empty cells is how contradiction 'presents' so i can check if it is robust!
    if numpossiblevalues == 0:
      fewestvalues = 11
      candidateboxrow = 4
      candidateboxcolumn = 4
      candidaterow = 4
      candidatecolumn = 4
    elif numpossiblevalues == 1:
      continue
    elif numpossiblevalues < fewestvalues:
      fewestvalues = numpossiblevalues
      candidateboxrow = coordinates[0]
      candidateboxcolumn = coordinates[1]
      candidaterow = coordinates[2]
      candidatecolumn = coordinates[3]
      if numpossiblevalues == 2:
        break
  
  if fewestvalues == 10: #no guessing opps found
    candidateboxrow = 3
    candidateboxcolumn = 3
    candidaterow = 3
    candidatecolumn = 3

  guesscoordinates = [candidateboxrow,candidateboxcolumn,candidaterow,candidatecolumn]
  return guesscoordinates

#savedboards = []
#savedboxdicts = []
#savedrowdicts = []
#savedcolumndicts = []
      
#def saveposition(board,boxdicts,rowdicts,columndicts): #do we want to put the guess candidates in here as well? Probably right?
#  boxdictscopy = copy.deepcopy(boxdicts)
#  savedboxdicts.append(boxdictscopy)
#  rowdictscopy = copy.deepcopy(rowdicts)
#  savedrowdicts.append(rowdictscopy)
#  columndictscopy = copy.deepcopy(columndicts)
#  savedcolumndicts.append(columndictscopy)
#  boardcopy = copy.deepcopy(board) 
#  savedboards.append(boardcopy)

def constraintpropagation(board,boxdicts,rowdicts,columndicts):
  scsfruit = 1
  ndfruit = 1
  # i could just use booleans here, but i may want numerical info for guiding optimisation later
  while scsfruit > 0:
    while ndfruit > 0:
      ndfruit = 0
      for coordinates in indices: # indices is immutable/global no need to pass as argument 
        cell = board[coordinates[0]][coordinates[1]][coordinates[2]][coordinates[3]]
        if len(cell) == 1:
          value = cell[0]
          if type(value) == int: #test
           neighboursdelete(value,board,coordinates,boxdicts,rowdicts,columndicts)
           ndfruit += 1
         
        
      # Would be nice to have neighbourdelete check for clues and contradictions when it deletes, that way we don't scan whole grid just affected squares. Come back to this! 
    # if neighbourdelete is fruitful, run single candidatesearch. If SCS is fruitful, start loop again. Otherwise, we are 'locked'. We have propagated all constraints we can with these two rules. 
    scsfruit = singlecandidatesearch(board,boxdicts,rowdicts,columndicts)
    ndfruit = scsfruit
  return [board,boxdicts,rowdicts,columndicts]



def initialclueinput(ninexnine,board,boxdicts,rowdicts,columndicts):
  # input clues and propagate their constraints
  cluelocationresults = cluelocations(ninexnine)
  celllocations = cluelocationresults[0]
  values = cluelocationresults[1]
  for num in range(0,len(celllocations)):
    coordinates = celllocations[num]
    value = values[num]
    neighboursdelete(value,board,coordinates,boxdicts,rowdicts,columndicts)
  return [board,boxdicts,rowdicts,columndicts] 



#this section is copied from our tower of hanoi depth first search. I actually just wrote in that code as a skeleton and then replaced each line with the corresponding thing
def depthfirstsearch(ninexthreexthree,boxdicts,rowdicts,columndicts): 

  startstate = [ninexthreexthree,boxdicts,rowdicts,columndicts]
  frontier = [startstate]
 # explored = []
  validboardcoordinates = [0,1,2,3]
  sudokusolved = False

  currentstate = frontier.pop()
  
  while not sudokusolved: 
  #  explored.append(currentstate)
    guesscoordinates = findguesscoordinates(currentstate[0]) 
    guesses = currentstate[0][guesscoordinates[0]][guesscoordinates[1]][guesscoordinates[2]][guesscoordinates[3]] #action is 
    for guess in guesses:
      newboard = copy.deepcopy(currentstate[0]) 
      newboxdicts = copy.deepcopy(currentstate[1])
      newrowdicts = copy.deepcopy(currentstate[2])
      newcolumndicts = copy.deepcopy(currentstate[3])
      
      newboard[guesscoordinates[0]][guesscoordinates[1]][guesscoordinates[2]][guesscoordinates[3]] = [guess]

      newstate = constraintpropagation(newboard,newboxdicts,newrowdicts,newcolumndicts)
      newguesscoordinates = findguesscoordinates(newboard)
      if newguesscoordinates[0] in validboardcoordinates:
        frontier.append(newstate) 
      if newguesscoordinates[0] == 3:
        frontier.append(newstate) 
        sudokusolved = True
        print('This board is the solution!, going in frontier')
        print(f'sudoku solved is {sudokusolved}')
        solved_sudoku = cluestoninexnine(newstate[0])
      
    if len(frontier) == 0:
      print('No solution found!')
      solved_sudoku = invalidsudoku
      return solved_sudoku
  
    currentstate = frontier.pop() 

  print('Solution found!')
  return solved_sudoku




def newguessingsolve(ninexnine): 
  print(f'Attempting this sudoku \n {ninexnine}')
  cluedstate = initialclueinput(ninexnine,startboard,startboxdicts,startrowdicts,startcolumndicts)
  cpdstate = constraintpropagation(cluedstate[0],cluedstate[1],cluedstate[2],cluedstate[3])
  guesscoordinates = findguesscoordinates(cpdstate[0])
  if guesscoordinates[0] == 3: #solved without guessing/tree searching
    print('solved without guessing')
    solution = cluestoninexnine(cpdstate[0])
  elif guesscoordinates[0] == 4: #contradiction without guessing/tree searching, therefore invalid
    print('contradiction without guessing/tree searching, therefore invalid')
    solution = invalidsudoku
  else: # locked
    solution = depthfirstsearch(cpdstate[0],cpdstate[1],cpdstate[2],cpdstate[3])

  return solution




 
  
  

  
t1 = time.perf_counter()
print(newguessingsolve(sudoku))
t2 = time.perf_counter()
print(f'Solved in {t2-t1}')


  


