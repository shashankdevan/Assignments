#! /usr/bin/env python
import os
import sys
import copy
import time
from Queue import PriorityQueue
from Queue import Queue

fileExt="sdk" #The allowable file extension
puzzle=[] #Initialize the puzzle
blanks=[] #Initialize blank spots

blankValues={} #Initialize the dictionary for heuristic

pathLengths=[] #Hold all the path lengths for metrics
currentPathLength=0 #Hold the local path length
constraintChecks=0
runningTime=0


def create_blank_grid():
	global puzzle
	
	for i in range(9):	
		puzzle.append([])
		for j in range(9):
			puzzle[i].append([])
			puzzle[i][j]=0

def checkFiles(input, output):
#	print ("in checkFiles")
	inputGood=False
	outputGood=False
        #Check if input file exists and is a file not a directory
	if os.path.exists(input):
		if os.path.isfile(input):
			tokens=input.split(".")
          	#Check the file extension
			if tokens[len(tokens)-1]==fileExt :
				inputGood=True
			else:
				print "File extension for input must be '.sdk'"
        		        sys.exit(2)
       		else:
			print "Input is not a file."
			sys.exit(2)
	else:
		print "Input file does not exist."
		sys.exit(2)

	tokens=output.split(".")
	if tokens[len(tokens)-1]==fileExt:
		outputGood=True
	else:
		print "File extension for output must be '.sdk'"
		sys.exit(2)
        #Both input/output must be legit for it to work
	if not (inputGood and outputGood):
		sys.exit(2)

def loadPuzzle(puzzleFile):
	global puzzle

#	print ("in loadPuzzle")
	possibleTokens=[1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
        puzzle1=open(puzzleFile, 'r')
        puzzleText=puzzle1.readlines()
        for row in range (9):
		lineTokens=puzzleText[row].split()
		if len(lineTokens)!=9:
			print "Improper file format! Line length must always be 9"
			sys.exit(1)
		for col in range(9):
			token=lineTokens[col].split()[0].strip()
			if token=='*':
				token=0 # Change the '-'s to 0s
			token=int(token)
			if token not in possibleTokens:
				print "Invalid token found"
				print "Token: "+str(token)+" possible: ", possibleTokens
				sys.exit(1)
			puzzle[row][col]=int(token)
	print ""

def getEmptyCells(puzzle):
#	print ("in getEmptyCells")
	emptyCells=[]
	for i in range(9):
		for j in range(9):
			if puzzle[i][j]==0:
				emptyCells.append((i, j))
	return emptyCells	
	
def start():
	global blanks
	
#	print ("in start")
	if len(sys.argv)!=3:
		print ("Wrong input.")
		sys.exit(2)

        #Get arguments for input-output
        inputFile=sys.argv[1]
        outputFile=sys.argv[2]

        #Make sure filenames are ok
        checkFiles(inputFile, outputFile)
        #Load the puzzle file into array
        loadPuzzle(inputFile)
        #Construct the list of blanks
        blanks=getEmptyCells(puzzle)

        print "Solving file: "+inputFile
        print str(len(blanks))+" blanks."
        print ""
        solve(puzzle)

def getPossibleValues(cell):

#	print ("in getPossibleValues")
        row=cell[0]
        col=cell[1]
        allowed=[]
        for i in range(1,10):
		if puzzleValid(row, col, i):
			allowed.append(i)
        return allowed

def checkRow(row, num ):
        for col in range(9):
		currentValue=puzzle[row][col]
                if num==currentValue:
			return False
	return True

def checkColumn(col, num ):
        for row in range(9):
                currentValue=puzzle[row][col]
                if num==currentValue:
			return False
        return True

def checkBox(row, col, num):
        row=(row/3)*3
        col=(col/3)*3

        for r in range(3):
		for c in range(3):
			if puzzle[row+r][col+c]==num:
				return False
        return True

def puzzleValid(row, col ,num):
        if num==0:
		return True
        else:
            #Return true if row, column, and box have no violations
		rowValid=checkRow(row, num)
                colValid=checkColumn(col, num)
                boxValid=checkBox(row, col, num)
                valid=(rowValid & colValid & boxValid)

        return valid

def processVariablesFH():
	global blankValues

#	print ("in processVariablesFH")
	#print blanks
	for blank in blanks:
		possibleValues=getPossibleValues(blank)
		blankValues[blank]=possibleValues

def getRowBlanks(row):
	cells=[]
	for col in range(9):
		if puzzle[row][col]==0:
			cells.append((row, col))
	return cells

def getColumnBlanks(col):
        cells=[]
        for row in range(9):
		if puzzle[row][col]==0:
			cells.append((row,col))
        return cells

def getBoxBlanks(row, col):
	cells=[]
	row=(row/3)*3
	col=(col/3)*3

        for r in range(3):
		for c in range(3):
			if puzzle[row+r][col+c]==0:
				cells.append((row+r,col+c))
	return cells

def getNeighborBlanks(blank):

#	print ("in getNeighborBlanks")
	row=blank[0]
	col=blank[1]

	neighbors=[]
	associatedBlanks=getRowBlanks(row) + getColumnBlanks(col) + getBoxBlanks(row, col)
        for blank in associatedBlanks:
		if blank not in neighbors and blank!=(row,col):
                #Might be that box collided with row / col so check here
			neighbors.append(blank)
        return neighbors

def getMRV():
	q = PriorityQueue()
        for blank in blanks:
		possible = getPossibleValues(blank)
		q.put((len(possible), blank))

        #Get the first one among (possibly equal)
        min_blanks = []
        min_blanks.append(q.get())
        minVal = min_blanks[0][0]

        #Build max Degree list
        while not q.empty(): #Get all equally-prioritized blanks
		next = q.get()
		if next[0] == minVal:
	                min_blanks.append(next)
		else:
			break

        maxDeg = len(getNeighborBlanks(min_blanks[0][1]))
        maxDegBlank = min_blanks[0]

        for blank1 in min_blanks:
		degree = len(getNeighborBlanks(blank1[1]))
		if degree > maxDeg:
			maxDegBlank = blank1
			maxDeg = degree
        return maxDegBlank[1]

def removeInconsistencies(orig, dest):
	global blankValues

        removed=False
        originDomain=copy.deepcopy(blankValues[orig])
        for val in originDomain:
		neighborDomain=copy.deepcopy(blankValues[dest])
		if val in neighborDomain:
			neighborDomain.remove(val)
		if len(neighborDomain)==0: #Any value of original domain caused neighbor domain to become 0
			blankValues[orig].remove(val)
			removed=True
        return removed


def propagateConstraints():

#	print ("in propagateConstraints")
	queue=Queue() #Build a queue of all arcs in the grid
        for blank in blanks:
		neighbors=getNeighborBlanks(blank)
		for neighbor in neighbors:
			queue.put((blank, neighbor))
	#while not queue.empty():
	#	print queue.get()
	#print queue.qsize()
        while not queue.empty():
		arc=queue.get()
		orig=arc[0]
		dest=arc[1]
		if removeInconsistencies(orig, dest): #Removal occurred from orig
			neighbors=getNeighborBlanks(orig) #Go through neighbors, add an arc from neighbor->orig to detect possibl inconsistencies
			neighbors.remove(dest)
			for neighbor in neighbors:
				queue.put((neighbor, orig))

def outputSolutionFile():
#	outFile=open(outputFile, 'w')
	for i in range(9):
		rowString=""
		for j in range(9):
			rowString+=str(puzzle[i][j])+" "
		print (rowString+'\n')

def endAlgorithm():
	pathLengths.append(currentPathLength) #Append the final path's length
	#runningTime=time.clock()-runningTime
	print "Solution found."
            #print ""
	outputSolutionFile()
	#printMetrics()
	sys.exit(0)

def constraintProp():
	global puzzle, blankValues, blanks, pathLengths, currentPathLength

#	print ("in constraintProp")

	#print (blankValues)
	if len(blanks)==0:
		endAlgorithm()

        #Haven't found a solution yet; get coords of the blank
        blank=getMRV()
        row=blank[0]
        col=blank[1]

        #Try numbers in the domain.
        blankDomain=copy.deepcopy(blankValues[blank])
	#print blankDomain
#	print ("did it print blankdomain?")
        for num in blankDomain:
		tempDomain=copy.deepcopy(blankValues) #Copy of current domain before pruning
		blankValues[blank]=[num]
            #Propagate the constraints
		propagateConstraints()
            #Assign value
		puzzle[row][col]=num
		currentPathLength+=1
		blanks.remove(blank)
	
		result=constraintProp()
		if result!=None:
			return
            #Restore the domain and backtrack
		blankValues=tempDomain
		blanks.append(blank)
		puzzle[row][col]=0
		pathLengths.append(currentPathLength) #Add the current path length to the overall list.
		currentPathLength-=1
	return None

def solve(puzzleArray):
#	print ("in solve")
	processVariablesFH()
	constraintProp()

def main():

	global fileExt, puzzle, blanks, blankValues, pathLengths, currentPathLength, contraintChecks, outputFile
	create_blank_grid()
	start()
	
main()
