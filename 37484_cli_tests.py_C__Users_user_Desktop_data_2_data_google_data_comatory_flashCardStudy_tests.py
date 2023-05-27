import sys
import StringIO
import glob
import os
from nose.tools import *
import pickle
from flashcardstudy import stack, card, errors, cliparser, stack, sfile

# TOOLS
def parser_cleanup():
	"""Sets parser to empty lists."""
	cliparser.passed_files = [] 
	cliparser.passed_args = []
	cliparser.output = []

def files_cleanup():
	"""Truncates stack files."""
	files = sfile.lookup_stack_files()
	for file in files:
		truncfile = open(file, 'w')
		truncfile.truncate()
		truncfile.close()

def delete_files():
	"""Deletes all stack (.stk) files in CWD."""
	files = glob.glob('*.stk')
	for file in files:
		os.remove(file)

def create_test_files():
	"""Creates two blank files 'example.stk' and 'stack.stk'."""
	f1 = open('example.stk','w')
	f2 = open('stack.stk','w')
	f1.close()
	f2.close()

def create_stack_file_w_cards():
	sys.stdin = StringIO.StringIO('animals\ny\ndog\ncanine\n\nfrog\namphibian\nf\n')
	stack.new_stack_file()

# DATA TESTS (stack)

def test_lookup_stack_files():
	create_test_files()
	assert_equal(sfile.lookup_stack_files(),['example.stk','stack.stk'])
	delete_files()

def test_request_file_info():
	sys.stdin = StringIO.StringIO('example\nno\n')
	assert_equal(stack.requests(), (1, 'example', []))

def test_new_stack_file():
	sys.stdin = StringIO.StringIO('example\nno\n')
	stack.new_stack_file()
	assert_equal(sfile.lookup_stack_files(), ['example.stk'])
	delete_files()

def test_new_stack_file_and_add_cards():
	create_stack_file_w_cards()
	assert_equal(sfile.lookup_stack_files(), ['animals.stk'])
	delete_files()

def test_adding_cards_to_existing_stack():
	create_stack_file_w_cards()
	adding_cards = card.Helpers()
	sys.stdin = StringIO.StringIO('a\nwhale\nmammal\nf\nq\n')
	adding_cards.editing(['animals.stk'])
	f = open('animals.stk', 'rb')
	data = pickle.load(f)	
	assert_equal(data[0], 1)
	assert_equal(data[1], 'animals')
	assert_equal(data[2][2], [3, 'whale','mammal'])
	assert_equal(sfile.read_stack_files(['animals.stk']), [data])
	f.close()

def test_card_reordering():
	create_stack_file_w_cards()
	f = open('animals.stk', 'rb')
	data = pickle.load(f)	
	sys.stdin = StringIO.StringIO('2\n1\n\q\n')
	card.change_card_order(data)
	assert_equal(data[2][0], [1, 'frog', 'amphibian'])
	assert_equal(data[2][1], [2, 'dog', 'canine'])
	f.close()
	delete_files()

def test_deleting_cards():
	create_stack_file_w_cards()
	f = open('animals.stk', 'rb')
	data = pickle.load(f)	
	sys.stdin = StringIO.StringIO('1\nq\n')
	card.delete_card(data)
	assert_equal(len(data[2]), 1)
	assert_equal(data[2][0], [1, 'frog', 'amphibian'])
	f.close()
	delete_files()

def test_read_stack_file():
	create_stack_file_w_cards()
	f = open('animals.stk', 'rb')
	data = pickle.load(f)	
	assert_equal(sfile.read_stack_files(['animals.stk']), [data])
	f.close()
	delete_files()

# PARSER TESTS (cliparser)
def test_parser_with_no_arg():
	parser_cleanup()
	assert_raises(SystemExit, cliparser.parse, '-r')
	assert_raises(SystemExit, cliparser.parse, ' ')

def test_parser_with_single_type_arg():
	parser_cleanup()
	assert_equal(cliparser.parse(['--list']), [[],['--list']])
	
def test_parser_with_single_type_arg_and_file():
	parser_cleanup()
	assert_raises(SystemExit, cliparser.parse, ['stack.stk', '-n'])

def test_parser_with_invalid_arg():
	assert_raises(SystemExit, cliparser.parse, ['stack.stk','-q'])

def test_parser_with_files_only():
	assert_raises(SystemExit, cliparser.parse, ['stack.stk'])
	assert_raises(SystemExit, cliparser.parse, ['stack.stk','notes.stk'])

def test_parser_with_invalid_file():
	assert_raises(SystemExit, cliparser.parse, ['notes.stk','-r', '-d'])
	assert_raises(SystemExit, cliparser.parse, ['stack.stk','notes.stk','-r', '-d'])
	assert_raises(SystemExit, cliparser.parse, ['fail.stk', '-v', '-d'])

def test_parser_with_valid_file():
	parser_cleanup()
	create_test_files()
	assert_equal(cliparser.parse(['stack.stk', '-d', '-r']), [['stack.stk'],['-d', '-r']])

def test_parser_with_valid_file_and_args():
	parser_cleanup()
	assert_equal(cliparser.parse(['stack.stk', '-d', '-r', '-s', '-v']),[['stack.stk'],['-d', '-r', '-s', '-v']])

def test_parser_without_display_arg():
	parser_cleanup()
	assert_raises(SystemExit, cliparser.parse, ['stack.stk', '-r', '-s'])

def test_parser_and_long_args():
	parser_cleanup()
	assert_equal(cliparser.parse(['stack.stk', '--display', '--random']),[['stack.stk'],['--display','--random']])

def test_parser_with_valid_file_and_invalid_arg():
	parser_cleanup()
	assert_raises(SystemExit, cliparser.parse, ['stack.stk', '-r', '-s', '-fail'])

def test_parser_with_invalid_single_type_arg():
	parser_cleanup()
	assert_raises(SystemExit, cliparser.parse, ['stack.stk', '-r', '--author'])
	parser_cleanup()
	assert_raises(SystemExit, cliparser.parse, ['stack.stk', 'example.stk', '-r', '--author'])
	parser_cleanup()
	assert_raises(SystemExit, cliparser.parse, ['stack.stk', 'fail.stk', '-e', '--list'])

def test_parser_with_edit_arg():
	parser_cleanup()
	assert_raises(SystemExit, cliparser.parse, ['stack.stk', '-d', '--edit'])
	parser_cleanup()
	assert_raises(SystemExit, cliparser.parse, ['stack.stk', '-d', '-r', '-e'])
	parser_cleanup()
	assert_equal(cliparser.parse(['stack.stk','-e']),[['stack.stk'],['-e']])
	parser_cleanup()
	assert_equal(cliparser.parse(['stack.stk','--edit']),[['stack.stk'],['--edit']])

def test_parser_with_wildcard():
	parser_cleanup()
	assert_equal(cliparser.parse(['stack.stk','-d','-w']),[['stack.stk'],['-d','-w']])
	parser_cleanup()
	assert_equal(cliparser.parse(['-a','-w']),[[],['-a','-w']])
	parser_cleanup()
	assert_equal(cliparser.parse(['stack.stk', 'example.stk', '--display', '--wildcard']),[['stack.stk', 'example.stk'],['--display', '--wildcard']])
	parser_cleanup()
	assert_raises(SystemExit, cliparser.parse, ['stack.stk', '-d', '-r', '-w'])
	parser_cleanup()
	assert_raises(SystemExit, cliparser.parse, ['stack.stk', 'example.stk', '-d', '-r', '-s', '-w'])
	parser_cleanup()
	assert_raises(SystemExit, cliparser.parse, ['-a','-s', '-w'])

def test_parser_with_all_arg():
	parser_cleanup()
	assert_equal(cliparser.parse(['--all']),[[],['--all']])
	parser_cleanup()
	assert_equal(cliparser.parse(['-a', '-r', '-s', '-v']), [[], ['-a', '-r', '-s', '-v']])
	parser_cleanup()
	assert_raises(SystemExit, cliparser.parse, ['-a', '-e'])
	parser_cleanup()
	assert_raises(SystemExit, cliparser.parse, ['stack.stk', 'fail.stk', '-a'])
	parser_cleanup()
	assert_raises(SystemExit, cliparser.parse, ['fail.stk', '--all'])
	delete_files()


