import os
import timeit
import datetime
import sfile
import stack
import errors
from content import ContentObject

def prompt(session):

	action = raw_input("> ")
	
	if action.lower() == 'q':
		print "\nElapsed time h:mm:ss  %s" % session.get_time()
		exit(0)


def display(files, card_random, stack_random, wildcard, reverse):

	stacks = sfile.read_stack_files(files)
	stacks.sort()

	if card_random:
		card_random = 'random'
	if stack_random:
		stack_random = 'randomstack'
	if wildcard:
		wildcard = 'wildcard'
	if reverse:
		reverse = 'reverse'

	session = ContentObject(stacks, card_random, stack_random, wildcard, reverse)

	print """
	Type 'Q' to stop anytime, RETURN to continue studying.
	"""
	print "Your arguments:"
	print "\n", session.mode 

	prompt(session)

	while True:
		
		os.system('cls' if os.name == 'nt' else 'clear')

		print session.fetch()
		prompt(session)
		print session.fetch()
		prompt(session)
