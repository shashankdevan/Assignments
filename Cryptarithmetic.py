#!/usr/bin/python
# Name: Shashank Devan(sdevan1)
# Instructions to run: python <filename>.py SEND+MORE=MONEY

import sys
from re import findall
from itertools import permutations
import timeit

def crypt_solver():

	#declarations of data structures
	puzzle = []
        temp_puzzle = []
        words = []
        first_letters = []
        first_positions = []
        characters = []

        #get the puzzle given by user
        if(len(sys.argv) == 2):
                puzzle = sys.argv[1]
        else:
                print("Enter valid argument.")

        #insert '=' so that eval can be called on puzzle later
        for x in puzzle:
                if (x == '='):
                        temp_puzzle.append(x)
                        temp_puzzle.append(x)
                else:
                        temp_puzzle.append(x)
        puzzle = ''.join(temp_puzzle)

        #separate the words in the puzzle
        words = findall('[A-Za-z]+', puzzle)

        #first letter cannot be a 0. Store locations of first letters. 
        for word in words:
                if word[0] not in first_letters:
                        first_letters.append(word[0])

        #create an ordered set of characters in puzzle
        for c in puzzle:
                if c.isalpha() and c not in characters:
                        characters.append(c)

        for f in first_letters:
                index = characters.index(f)
                if index >= 0:
                        first_positions.append(index)

        #generate possible assignments of the letter-digit associations, evaluate one by one
        for assignment in permutations("0123456789", len(characters)):
                temp=1
                for f in first_positions:
                        if (assignment[f] == "0"):
                                temp=0
                if (temp):
                        operation = puzzle
                        for char in characters:
                                position = characters.index(char)
                                if (position >= 0):
                                        operation = operation.replace(char,assignment[position])
                        result = eval(operation)
                        if (result):
                                print (puzzle)
                                print (operation)
                                break


def main():

	crypt_solver()


start = timeit.default_timer()			 
main()
stop = timeit.default_timer()
print ("Running time:" + str(stop - start) + " seconds.")
