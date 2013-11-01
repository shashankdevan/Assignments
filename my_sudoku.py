#! /usr/bin/env python
import os
import sys
import copy
import time
from Queue import PriorityQueue
from Queue import Queue

fileExt="sdk" #The allowable file extension
grid=[] #Initialize the grid
blanks=[] #Initialize blank spots
blank_values={} #Initialize the dictionary for heuristic
pathLengths=[] #Hold all the path lengths for metrics
currentPathLength=0 #Hold the local path length
constraintChecks=0
runningTime=0
q = PriorityQueue()


def CreateBlankGrid():
	global grid
	
	for i in range(9):	
		grid.append([])
		for j in range(9):
			grid[i].append([])
			grid[i][j]=0

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

def LoadGrid(input_file):
	global grid

#	print ("in LoadGrid")
	common_domain=[1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
        file_ptr=open(input_file, 'r')
        lines_array=file_ptr.readlines()
        for row in range (9):
		line_tokens=lines_array[row].split()
		if len(line_tokens)!=9:
			print "Input grid must be 9*9. Wrong input."
			sys.exit(1)
		for col in range(9):
			token=line_tokens[col].split()[0].strip()
			if token=='*':
				token=0 # Change the '-'s to 0s
			token=int(token)
			if token not in common_domain:
				print "Invalid token found"
				print "Token: "+str(token)+" possible_values: ", common_domain
				sys.exit(1)
			grid[row][col]=int(token)
	print ""

def GetEmptyCells(grid):
#	print ("in GetEmptyCells")
	empty_cells=[]
	for i in range(9):
		for j in range(9):
			if grid[i][j]==0:
				empty_cells.append((i, j))
	return empty_cells	

# finds the allowable values that a cell can take to keep the sudoku valid
def GetAllowedValuesOfBlank(cell):

#	print ("in GetAllowedValuesOfBlank")
        row=cell[0]
        col=cell[1]
        allowed=[]
        for i in range(1,10):
		if IsSudokuValid(row, col, i):
			allowed.append(i)
        return allowed

#checks if num is present in grid[row][]
def new_in_row(row, num ):
        for col in range(9):
		currentValue=grid[row][col]
                if num==currentValue:
			return False
	return True

def new_in_column(col, num ):
        for row in range(9):
                currentValue=grid[row][col]
                if num==currentValue:
			return False
        return True

def new_in_box(row, col, num):
        row=(row/3)*3
        col=(col/3)*3

        for r in range(3):
		for c in range(3):
			if grid[row+r][col+c]==num:
				return False
        return True

#check whether for grid[row][col] = num, is the sudoku still valid
def IsSudokuValid(row, col ,num): 
        if num==0:
		return True
        else:
            #Return true if row, column, and box have no violations
		valid_in_row=new_in_row(row, num)
                valid_in_col=new_in_column(col, num)
                valid_in_box=new_in_box(row, col, num)
 
                valid_in_grid = (valid_in_row & valid_in_col & valid_in_box)

        return valid_in_grid

def Getpossible_valuesValuesOfBlanks():
	global blank_values

	for blank in blanks:
		#get a list of possible_values values for each blank cell
		possible_values_values=GetAllowedValuesOfBlank(blank)
		blank_values[blank]=possible_values_values

def getRowBlanks(row):
	cells=[]
	for col in range(9):
		if grid[row][col]==0:
			cells.append((row, col))
	return cells

def getColumnBlanks(col):
        cells=[]
        for row in range(9):
		if grid[row][col]==0:
			cells.append((row,col))
        return cells

def getBoxBlanks(row, col):
	cells=[]
	row=(row/3)*3
	col=(col/3)*3

        for r in range(3):
		for c in range(3):
			if grid[row+r][col+c]==0:
				cells.append((row+r,col+c))
	return cells

def GetBlankNeighbors(blank):

#	print ("in GetBlankNeighbors")
	row=blank[0]
	col=blank[1]

	neighbors=[]
	associatedBlanks=getRowBlanks(row) + getColumnBlanks(col) + getBoxBlanks(row, col)
        for blank in associatedBlanks:
		if blank not in neighbors and blank!=(row,col):
                #Might be that box collided with row / col so check here
			neighbors.append(blank)
        return neighbors

def GetMinRemainingValueBlank():

	global q
	
	#'q' contains ((#possible_values, blank), ..)
        for blank in blanks:
		possible_values = GetAllowedValuesOfBlank(blank)
		q.put((len(possible_values), blank))

def GetMostConstrainingVariable():
	global q
	
        #Get the first one among the blanks with minimum number of possible values
        min_blanks = []
        min_blanks.append(q.get())
        minVal = min_blanks[0][0]

        #Build max Degree list
        while not q.empty(): #Get all equally-prioritized blanks with least number of possible values
		next = q.get()
		if next[0] == minVal:
	                min_blanks.append(next)
		else:
			break

        maxDeg = len(GetBlankNeighbors(min_blanks[0][1]))
        maxDegBlank = min_blanks[0]

        for blank1 in min_blanks:
		degree = len(GetBlankNeighbors(blank1[1]))
		if degree > maxDeg:
			maxDegBlank = blank1
			maxDeg = degree
        return maxDegBlank[1]

def removeInconsistencies(orig, dest):
	global blank_values

        removed=False
        originDomain=copy.deepcopy(blank_values[orig])
        for val in originDomain:
		neighborDomain=copy.deepcopy(blank_values[dest])
		if val in neighborDomain:
			neighborDomain.remove(val)
		if len(neighborDomain)==0: #Any value of original domain caused neighbor domain to become 0
			blank_values[orig].remove(val)
			removed=True
        return removed


def IsSudokuValid():

#	print ("in IsSudokuValid")
	queue=Queue() #Build a queue of all arcs in the grid
        for blank in blanks:
		neighbors=GetBlankNeighbors(blank)
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
			neighbors=GetBlankNeighbors(orig) #Go through neighbors, add an arc from neighbor->orig to detect possibl inconsistencies
			neighbors.remove(dest)
			for neighbor in neighbors:
				queue.put((neighbor, orig))

def ShowSudoku():
#	outFile=open(outputFile, 'w')
	for i in range(9):
		rowString=""
		for j in range(9):
			rowString+=str(grid[i][j])+" "
		print (rowString+'\n')

def EndAlgorithm():
	pathLengths.append(currentPathLength) #Append the final path's length
	#runningTime=time.clock()-runningTime
	print "Solution found."
            #print ""
	ShowSudoku()
	#printMetrics()
	sys.exit(0)

def PropogateConstraints():
	global grid, blank_values, blanks, pathLengths, currentPathLength

#	print ("in PropogateConstraints")

	#print (blank_values)
	if len(blanks)==0:
		EndAlgorithm()

        #Haven't found a solution yet; get coords of the blank
        GetMinRemainingValueBlank()
	blank=GetMostConstrainingVariable()
        row=blank[0]
        col=blank[1]

        #Try numbers in the domain.
        blankDomain=copy.deepcopy(blank_values[blank])
	#print blankDomain
#	print ("did it print blankdomain?")
        for num in blankDomain:
		tempDomain=copy.deepcopy(blank_values) #Copy of current domain before pruning
		blank_values[blank]=[num]
            #Propagate the constraints
		IsSudokuValid()
            #Assign value
		grid[row][col]=num
		currentPathLength+=1
		blanks.remove(blank)
	
		result=PropogateConstraints()
		if result!=None:
			return
            #Restore the domain and backtrack
		blank_values=tempDomain
		blanks.append(blank)
		grid[row][col]=0
		pathLengths.append(currentPathLength) #Add the current path length to the overall list.
		currentPathLength-=1
	return None

def main():

	global fileExt, grid, blanks, blank_values, pathLengths, currentPathLength, contraintChecks, outputFile
	
	CreateBlankGrid()
	
	if len(sys.argv)!=2:
		print ("Wrong input.")
		sys.exit(2)

        #Get arguments for input
        input_file=sys.argv[1]

        #Load the given grid into blank grid
        LoadGrid(input_file)
        #Construct the list of blanks
        blanks=GetEmptyCells(grid)

        print "File is: "+input_file
        print str(len(blanks))+" blanks."
        print ""
	
	#get the possible_values values that can be taken by each of the blank cells in grid
	Getpossible_valuesValuesOfBlanks()
	
	#based on the grid values, propogate the constraints that the variables must obey
	PropogateConstraints()
	
main()
