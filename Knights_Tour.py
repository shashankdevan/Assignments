#!/usr/bin/python
#Name: Shashank Devan (sdevan1)
#Course: CMSC 671
#Subject: Homework 2
#Program: Knight's Tour
#Instructions to run: python <filename>.py <size_of_board>

import sys

#increase the recursion stack depth to accomodate higher board sizes
sys.setrecursionlimit(9999999)

b_size=-1
board=[]
counter=1
neighbors=[]

#initialize the board with some value
def init_board():
	global board
	board=[[0 for i in range (0,b_size)] for j in range (0, b_size)]

#function to display the knight's tour
def show_board():
	print '\n'
	print b_size*'+-------' + '+'
	for x in xrange(0,b_size):
                for y in xrange(0,b_size):
                        print '|'+ repr(board[x][y]).rjust(6),
		print '|\n' + b_size*'+-------' + '+'

#function to check if the probable move is valid 
def IsValid(x,y):
	if (x>=0 and  x <b_size and y>=0 and y<b_size and board[x][y]==0):
		return 1

#function to calculate the no. of empty valid neighboring nodes 
def empty_neighbors(a,b):
	c=0
	moves=((-2,-1),(-2,1),(2,1),(2,-1),(1,2),(1,-2),(-1,-2),(-1,2))
        for move in moves:
                nx=a + move[0]
                ny=b+ move[1]
                if (IsValid(nx,ny)):
			c=c+1
	return c

#visit a square on the board
def seize(x,y,counter):
	board[x][y]=counter
	global neighbors

	#termination condition: stop when the knight completes board_size*board_size moves
	if(counter == b_size*b_size):
		show_board()
		sys.exit(1)
	
	moves=((-2,-1),(-2,1),(2,1),(2,-1),(1,2),(1,-2),(-1,-2),(-1,2))
	for move in moves:
		nx=x + move[0]
		ny=y + move[1]
		if (IsValid(nx,ny)):
			nz=empty_neighbors(nx,ny)
			neighbors.append([nx,ny,nz])
	
	#select the least lonely neighbor
	if(len(neighbors)):
		temp = neighbors[0]
		neighbors=sorted(neighbors, key=lambda temp:temp[2])
		temp2 = neighbors[0]
		while len(neighbors) > 0 : neighbors.pop()
		seize(temp2[0],temp2[1],counter+1)
			
	board[x][y]=0

def main():
        global b_size
	global board
	global counter

	if (len(sys.argv) !=2):
		b_size=8						#default board size=8
	else:
		b_size=int(sys.argv[1])

        init_board()
	seize(0,0,counter)	

main()
