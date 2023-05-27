import os
import glob
import pickle
from itertools import *
from prettytable import PrettyTable
from flashcardstudy import errors, card
import sfile

class StackFile(object):

	def __init__(self, id, name, cards):
		self.id = id
		self.name = name
		self.cards = cards

class Helpers(object):

	def id(self):
		stacks = sfile.lookup_stack_files()
		contents = sfile.read_stack_files(stacks)
		an_id = count(1)
		
		if len(stacks) == 0:
			return 1
		else:
			intersection = [s for s in contents if s[0] != an_id]
			for s in contents:
				if next(an_id) in intersection:
					return next(an_id)

		return next(an_id)


	def name(self):
		while True:
			prompt = raw_input("Stack name? ")

			if len(prompt) > 0:
				return prompt
			else:
				print "Cannot use blank name. Try again.\n"

	def create_cards(self):
		while True:
			prompt = raw_input("Add cards to stack? Y/N\n")

			if 'Y' in prompt or 'y' in prompt:
				cards = card.add_card()
			else:
				cards = [] 

			return cards


request = Helpers()

def requests():
	id = request.id()
	name = request.name()
	cards = request.create_cards()

	return id, name, cards

def new_stack_file(gui=False, filename=None, fileid=None):
	
	if gui:
		data = (fileid, filename,[])
		print "Added new stack: ", data
	else:
		data = requests()

	a_stack = StackFile(*data)

	#os.chmod(a_stack.name + '.stk', 0777)
	f = open(a_stack.name + '.stk', 'wb')
	
	data = [a_stack.id, a_stack.name, a_stack.cards]
	pickle.dump(data, f)
	f.close()

def delete_stack_file(gui=False, filenames=None):
	if gui:
		for file in filenames:
			os.remove(file + '.stk')
			print "Deleted stack: %s" % (file + '.stk')

def change_stack_order(files):
	stacks = sfile.read_stack_files(files)
	stacks.sort()
	try:
		select = int(raw_input("Select stack (ID) > "))
		moved_stack = stacks.pop(select - 1)
		new_position = int(raw_input("Select new position (ID) > "))
		stacks.sort()
		stacks.insert(new_position - 1, moved_stack)
	except ValueError, IndexError:
		errors.id(6)

	
	for a_stack in stacks:
		a_stack[0] = stacks.index(a_stack) + 1
		f = open(a_stack[1] + '.stk', 'wb')
		pickle.dump(a_stack, f)
		f.close()


def rename_stack_name(file, new_name):
	os.remove(file[1] + '.stk')
	file[1] = new_name
	f = open(new_name + '.stk', 'wb')
	print "To: ", file[1]
	pickle.dump(file, f)
	f.close()

def renumber_stacks(files):
	stacks = files 
	stacks.sort()
	count = 1

	for a_stack in stacks:
		a_stack[0] = 0
		a_stack[0] += count
		count += 1
		f = open(a_stack[1] + '.stk', 'wb')
		pickle.dump(a_stack, f)
		f.close()
		print "Renumbered stack /'%s/'" % a_stack[1]

def list_stacks():
	stacks = sfile.lookup_stack_files()
	contents = sfile.read_stack_files(stacks)
	
	table = PrettyTable(["Stack ID","Stack Name","Cards","Contents"])
	table.align["Contents"] = 'l'

	for stack in contents:
		stackname = (stack[1][:10] + '...') if len(stack[1]) > 10 else stack[1]
		stack_cards = [item[1:3] for item in stack[2]]
		display_cards = []
		for a_card in stack_cards:
			for card_cont in a_card:
				trunc_card = (card_cont[:15] + '...') if len(card_cont) > 15 else card_cont
				display_cards.append(trunc_card)

		table.add_row([stack[0],stackname, len(stack[2]), display_cards[0:4]])
	
	print '\n', table.get_string(sortby="Stack ID")

def move_stack_gui(stacks, index, up=True):
        print 'old stack order', stacks
	stacks.sort()
	selected_stack = stacks.pop(index)

        if up:
            new_position = index - 1
        else:
            new_position = index + 1
	stacks.insert(new_position, selected_stack)

        print 'new stack order', stacks

	for a_stack in stacks:
		a_stack[0] = stacks.index(a_stack) + 1
		f = open(a_stack[1] + '.stk', 'wb')
		pickle.dump(a_stack, f)
		f.close()

        renumber_stacks(stacks)

