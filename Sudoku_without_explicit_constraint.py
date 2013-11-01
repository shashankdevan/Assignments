#!/usr/bin/python
import os
import sys
import copy
import timeit
from Queue import PriorityQueue
from Queue import Queue


puzzle=[] #global puzzle grid
blanks=[] #holds all the blank cells in puzzle
blankValues={} #dictionary for all blank cells and allowed values (<blank> - <list of possible values> - <1,2>-<3,4,5,6>)

def ArcReduce(x, y): #reduce the domain of the blank cells, arcs are not consistent
	global blankValues
        change=False
        Dx=copy.deepcopy(blankValues[x])
        for vx in Dx:
		Dy=copy.deepcopy(blankValues[y]) #keep a copy for backtracking
		if vx in Dy:
			Dy.remove(vx) #reduce domain of blank
		if len(Dy)==0:
			blankValues[x].remove(vx)
			change=True
        return change

def Ac3(): #arc-consistency 3 algorithm (Reference: Wikipedia)
	worklist=Queue()
        for blank in blanks:
		neighbors=GetNeighbors(blank) #get neighbors of a particular blank cell
		for z in neighbors:
			worklist.put((blank,z)) #add blank cell and its neighbor to a worklist
        while not worklist.empty():
		arc=worklist.get() #remove an arc from worklist 
		x=arc[0] #current blank cell
 		y=arc[1] #neighbor
		if ArcReduce(x, y): #check if the arc removal results in reduction of domain
			neighbors=GetNeighbors(x) 
			neighbors.remove(y)
			for z in neighbors:
				worklist.put((z, x))

def GetVariableToInstantiate():
	q = PriorityQueue()
        for blank in blanks:
		possibles = GetValidValues(blank)
		q.put((len(possibles), blank))
        mrvBlanks = []
        mrvBlanks.append(q.get())
        minValue = mrvBlanks[0][0]
        while not q.empty():
		next = q.get()
		if next[0] == minValue:
	                mrvBlanks.append(next)
		else:
			break
	maxConstrainedNeighbors = len(GetNeighbors(mrvBlanks[0][1]))
        maxConstrainedNeighborsBlank = mrvBlanks[0]
        for b in mrvBlanks:
		degree = len(GetNeighbors(b[1]))
		if degree > maxConstrainedNeighbors:
			maxConstrainedNeighborsBlank = b
			maxConstrainedNeighbors = degree
        return maxConstrainedNeighborsBlank[1]

def StartConstraintPropogation(): #propagate current constraints to all variables
	global puzzle, blankValues, blanks
	if len(blanks)==0:
		print ('#'*6 + "Solution:" + '#'*6)
		ShowSudoku()
		stop = timeit.default_timer()
		print ("Running time:" + str(stop - start) + " seconds.")
		sys.exit(0)
        blank=GetVariableToInstantiate() #get blank with minimum remaining values  
        row=blank[0]
        col=blank[1]
        blankDomain=copy.deepcopy(blankValues[blank])
        for value in blankDomain:
		domainBackup=copy.deepcopy(blankValues)
		blankValues[blank]=[value]
		Ac3() #check arc-consistency
		puzzle[row][col]=value #instantiate the variable
		blanks.remove(blank)
		result=StartConstraintPropogation()
		if result!=None:
			return
		blankValues=domainBackup #backtrack
		blanks.append(blank)
		puzzle[row][col]=0
	return None

def GetRowBlanks(row):
	cells=[]
	for col in range(9):
		if puzzle[row][col]==0:
			cells.append((row, col))
	return cells

def GetColumnBlanks(col):
        cells=[]
        for row in range(9):
		if puzzle[row][col]==0:
			cells.append((row,col))
        return cells

def GetBlockBlanks(row, col):
	cells=[]
	row=(row/3)*3
	col=(col/3)*3
        for r in range(3):
		for c in range(3):
			if puzzle[row+r][col+c]==0:
				cells.append((row+r,col+c))
	return cells

def GetNeighbors(blank): # get all the peers of a blank by checking row,column and block
	row=blank[0]
	col=blank[1]
	neighbors=[]
	associatedBlanks=GetRowBlanks(row) + GetColumnBlanks(col) + GetBlockBlanks(row, col)
        for blank in associatedBlanks:
		if blank not in neighbors and blank!=(row,col):
			neighbors.append(blank)
        return neighbors

def ValidInRow(row, num ):
        for col in range(9):
		currentValue=puzzle[row][col]
                if num==currentValue:
			return False
	return True

def ValidInColumn(col, num ):
        for row in range(9):
                currentValue=puzzle[row][col]
                if num==currentValue:
			return False
        return True

def ValidInBlock(row, col, num): 
        row=(row/3)*3
        col=(col/3)*3
        for r in range(3):
		for c in range(3):
			if puzzle[row+r][col+c]==num:
				return False
        return True

def ValidInPuzzle(row, col ,num): # check if all rows columns and blocks values are possible
        if num==0:
		return True
        else:
		rowValid=ValidInRow(row, num)
                colValid=ValidInColumn(col, num)
                boxValid=ValidInBlock(row, col, num)
                valid=(rowValid & colValid & boxValid)
        return valid

def GetValidValues(cell): #get domain of the blanks
        row=cell[0]
        col=cell[1]
        allowed=[]
        for i in range(1,10):
		if ValidInPuzzle(row, col, i):
			allowed.append(i)
        return allowed

def GetValidBlankValues(): # put possible values of  blanks in the hash table
	global blankValues
 	for blank in blanks:
		validValues=GetValidValues(blank)
		blankValues[blank]=validValues

def GetBlanks(puzzle): #get all the blank cells
	emptyCells=[]
	for i in range(9):
		for j in range(9):
			if puzzle[i][j]==0:
				emptyCells.append((i, j))
	return emptyCells

def RenderRow(rowString):
	formattedString=""
	for i in range(0, len(rowString), 3):
		for j in range(0, 3):
			formattedString+=rowString[i+j]
		formattedString+="|"
	return formattedString

def ShowSudoku(): # print the puzzle 
	print "____________________" 
	rowStrings=[]
	for i in range(9):
		rowString=[]
		for j in range(9):
			rowString.append(str(puzzle[i][j])+" ")
		rowStrings.append(RenderRow(rowString))
	for i in range(0, len(rowStrings), 3):
		for j in range(0, 3):
			print rowStrings[i+j]
		print "--------------------" 

def LoadSudoku(puzzleFile): # load given sudoku in puzzle and blanks w0sith 
	global puzzle
	validCharacters=[1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
        filePtr=open(puzzleFile, 'r')
        puzzleLines=filePtr.readlines()
        for row in range (9):
		lineTokens=puzzleLines[row].split()
		if len(lineTokens)!=9:
			print "Input grid must be 9*9. Wrong input."
			sys.exit(1)
		for col in range(9):
			token=lineTokens[col].split()[0].strip()
			if token=='*':
				token=0 
			token=int(token)
			if token not in validCharacters:
				print "Invalid token found"
				print "Token: "+str(token)+" possible: ", validCharacters
				sys.exit(1) 
			puzzle[row][col]=int(token)
	print ""
	puzzle_ptr=open(puzzleFile, 'r')

	print ('#'*4 + "Input Sudoku:" + '#'*4)
	ShowSudoku()

def main():
	global puzzle, blanks, blankValues, pathLengths, currentPathLength, contraintChecks, outputFile

	#create a puzzle with all 0's
	puzzle = [[0 for i in range(0,9)] for j in range(0,9)] 
	
	#get user input puzzle from command-line argument
	if len(sys.argv)!=2:
		print ("Incorrect input. Please provide the input file.")
		sys.exit(2)
        inputFile=sys.argv[1]

	#load user-given sudoku in puzzle
        LoadSudoku(inputFile)
	
        blanks=GetBlanks(puzzle) #get all blank cells
        
	#get the list of blank cells with their possible values
	GetValidBlankValues()
	
	#propogate constraints to all vars, instantiate var, propogate constraints, resursively
	StartConstraintPropogation()

start = timeit.default_timer() #check running time
main()

