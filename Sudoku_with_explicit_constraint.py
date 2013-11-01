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

def GetBlanks(puzzle): #get all the blank cells
	emptyCells=[]
	for i in range(9):
		for j in range(9):
			if puzzle[i][j]==0:
				emptyCells.append((i, j))
	return emptyCells	
	
def GetValidValues(cell): #get domain of the blanks
        row=cell[0]
        col=cell[1]
        allowed=[]
        for i in range(1,10):
		if ValidInPuzzle(row, col, i):
			allowed.append(i)
        return allowed

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

def GetValidBlankValues(): # put possible values of  blanks in the hash table
	global blankValues
 	for blank in blanks:
		validValues=GetValidValues(blank)
		blankValues[blank]=validValues

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

def RenderRow(rowString):
	formattedString=""
	for i in range(0, len(rowString), 3):
		for j in range(0, 3):
			formattedString+=rowString[i+j]
		formattedString+="|"
	return formattedString

def PropogateThroughColumns(col): #propogate constraint explicitly through column

	column_blanks = {}	
	all_values = []
	flag =0
	flag1 = 0
	unique_value = 0
	exit_loop = False
	my_blank =[]
	for blank in blanks:#get all the blank cells in column
		if blank[1] == col:
			temp0=GetValidValues(blank)
			column_blanks[blank]=temp0
	while exit_loop == False:
		deletion_list = []
		for col_blank in column_blanks:
			if len(column_blanks[col_blank]) == 1: #if only single possible value, assign it to the cell
				r=col_blank[0]
				c=col_blank[1]			
				puzzle[r][c]=column_blanks[col_blank][0]
				currentPathLength+=1
				blanks.remove(col_blank)
				deletion_list.append(col_blank)
				flag = 1
		
		if flag == 0:
			exit_loop = True

		if flag:
			for element in deletion_list:
				del column_blanks[element]
			flag = 0
		for blank in blanks:
			if blank[1] == col:
				temp1=GetValidValues(blank)
				column_blanks[blank]=temp1
	#search for a value in domains of blank cells such that no other blank has the same value in their domains
	for cb in column_blanks:		
		for value in list(column_blanks[cb]):
			all_values.append(value)

	set_of_all_values = set(all_values)
	for value in set_of_all_values:
		if (all_values.count(value) == 1):
				unique_value = value	
	for cb in column_blanks:
		if unique_value in column_blanks[cb]:
			my_blank = cb
			break
	if unique_value: #assign that unique value to the blank cell
		puzzle[my_blank[0]][my_blank[1]]=unique_value
		blanks.remove(my_blank)
		to_delete=my_blank
		del column_blanks[to_delete]

def PropogateThroughRows(row): #propogate constraint explicitly through row

	row_blanks = {}
	all_row_blankValues = []
	all_values = []
	flag =0
	flag1 = 0
	unique_value = 0
	exit_loop = False
	my_blank =[]

	for blank in blanks: #get all the blank cells in row
		if blank[0] == row:
			row_blanks[blank]=blankValues[blank]
	while exit_loop == False:
		deletion_list = []
		for row_blank in row_blanks:
			if len(row_blanks[row_blank]) == 1: #if only single possible value, assign it to the cell
				row=row_blank[0]
				col=row_blank[1]			
				puzzle[row][col]=row_blanks[row_blank][0]
				currentPathLength+=1
				blanks.remove(row_blank)
				deletion_list.append(row_blank)
				flag = 1
		
		if flag == 0:
			exit_loop = True

		if flag:
			for element in deletion_list:
				del row_blanks[element]
			flag = 0
		for blank in blanks:
			if blank[0] == row:
				temp1=GetValidValues(blank)
				row_blanks[blank]=temp1
	#search for a value in domains of blank cells such that no other blank has the same value in their domains
	for rb in row_blanks:
		for value in list(row_blanks[rb]):
			all_values.append(value)

	set_of_all_values = set(all_values)
	for value in set_of_all_values: 
		if (all_values.count(value) == 1):
				unique_value = value	
	for rb in row_blanks:
		if unique_value in row_blanks[rb]:
			my_blank = rb
			break
	if unique_value: #assign that unique value to the blank cell
		puzzle[my_blank[0]][my_blank[1]]=unique_value
		blanks.remove(my_blank)
		to_delete=my_blank
		del row_blanks[to_delete]

def PropogateThroughBlocks(block): #structure same as functions for row and column 

	block_blanks = {}	
	all_values = []
	flag =0
	flag1 = 0
	exit_loop = False
	unique_value = 0
	my_blank =[]
	for blank in blanks:
		if blank in block:
			temp0=GetValidValues(blank)
			block_blanks[blank]=temp0
		
	while exit_loop == False:
		deletion_list = []
		for box_blank in block_blanks:
			if len(block_blanks[box_blank]) == 1:
				row=box_blank[0]
				col=box_blank[1]			
				puzzle[row][col]=block_blanks[box_blank][0]
				currentPathLength+=1
				blanks.remove(box_blank)
				deletion_list.append(box_blank)
				flag = 1
		
		if flag == 0:
			exit_loop = True

		if flag:
			for element in deletion_list:
				del block_blanks[element]
			flag = 0
		for blank in blanks:
			if blank in block:
				temp1=GetValidValues(blank)
				block_blanks[blank]=temp1
	for bb in block_blanks:		
		for value in list(block_blanks[bb]):
			all_values.append(value)

	set_of_all_values = set(all_values)
	for value in set_of_all_values:
		if (all_values.count(value) == 1):
				unique_value = value	
	for bb in block_blanks:
		if unique_value in block_blanks[bb]:
			my_blank = bb
			break
	if unique_value:
		puzzle[my_blank[0]][my_blank[1]]=unique_value
	#	currentPathLength+=1
		blanks.remove(my_blank)
		to_delete=my_blank
		del block_blanks[to_delete]

def DoExplicitConstraintPropogation(): #propogate the constraint (all rows, columns, blocks must have all 9 values) explicitly

	block_list = []
	for col in range(0,9):
		PropogateThroughColumns(col) #propogate through all columns
	for row in range(0,9):
		PropogateThroughRows(row) #propogate through all rows
	
	for i in range(3):
		for j in range(3):
			row = i*3	
			col = j*3
			for r in range(3):
				for c in range(3):
					block_list.append((row+r,col+c))
			PropogateThroughBlocks(block_list) #propogate through all blocks

def main():
	global puzzle, blanks, blankValues, pathLengths, currentPathLength, contraintChecks, outputFile

	#create a puzzle with all 0's
	puzzle = [[0 for i in range(0,9)] for j in range(0,9)] 
	
	#get user input puzzle from command-line argument
	if len(sys.argv)!=2:
		print ("Incorrect input. Please provide the input file.")
		sys.exit(2)
        inputFile=sys.argv[1]

	#load user-given puzzle in puzzle
        LoadSudoku(inputFile)
	
        blanks=GetBlanks(puzzle) #get all blank cells
        
	#get the list of blank cells with their possible values
	GetValidBlankValues()
	
	#propogate the constraint (all rows, columns, blocks must have all 9 values) explicitly
	DoExplicitConstraintPropogation()

	#get the list of blank cells with their possible values
	GetValidBlankValues()	

	#propogate constraints to all vars, instantiate var, propogate constraints, resursively
	StartConstraintPropogation()
	
start = timeit.default_timer() #check running time
main()

