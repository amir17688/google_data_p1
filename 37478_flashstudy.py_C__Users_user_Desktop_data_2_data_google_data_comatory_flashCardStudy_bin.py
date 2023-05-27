import sys
from flashcardstudy import errors 
from flashcardstudy.help import gethelp
from flashcardstudy.cliparser import parse, ARGS
from flashcardstudy.processor import processor
from gui.main import flashCardStudyGUI

def flashcard():
	if len(sys.argv) == 1:
		errors.id(0)

	elif len(sys.argv) == 2 and sys.argv[1] == '-h' or sys.argv[1] == '--help':
		gethelp()

	elif len(sys.argv) == 2 and sys.argv[1] == '--gui':
                flashCardStudyGUI()

	elif len(sys.argv) >= 1:
		arguments = parse(sys.argv[1:])
		processor(arguments)

if __name__ == '__main__':
	flashcard()
