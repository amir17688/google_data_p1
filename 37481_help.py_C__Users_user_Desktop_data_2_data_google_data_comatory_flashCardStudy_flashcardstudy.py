def gethelp():
	print """
	-h, --help: See this screen

	File-based arguments	
	--------------------

	-d, --display: Start session in with cards in order. 
	
	You always need to pass `-d` or `--display` and stack file(s) (*.stk) to
	start session, except `-a` (see below).

	Optional arguments:
	-r, --random: Will display cards in random order.
	-s, --stack: Next stack will be randomly selected. 
	-v, --reverse: Shows side two of card(s) first.
	-w, --wildcard: Jumps between stacks AND cards in randomly. 

		Example: `python flashcard.py mystack.stk -d -r`

		This will launch flashcard with only one stack file
		named `mystack.stk' and it will display cards
		in random order. 
	
	-a, --all: Automatically passess all stack files in current dir. Use
		instead of `-d`. You can combine this with optional args.
	
		Example: `python flashcard.py -a -w`

		Will display all stacks in current dir in random order, program
                would be jumping randomly between stacks and cards.

	General arguments	
	-----------------
	You can't pass stack files when using these args:

	-n, --new: Create new stack (with cards).
	-l, --list: List stack(s) in current dir.
	-o, --order: Only for changing order of stacks in current dir.
	--author: Author info.

		Example: 'python flashcard.py -n`

		Launches flashCardStudy in a mode that allows you to create
		new stack and add cards into that stack.
	
	Edit argument
	-------------
	You can combine `-e` or `--edit` with only single stack file. It is
	used to edit given stack file.

        GUI mode
        --------
        When using arg `--gui`, you will be presented with graphical version
        of the program. GUI mode keeps all stacks in its own system folder (see
        `help` in the help menu for more info.)
"""

def author_data():
        data = {
                'year': '2015',
                'version': '1.0.6',
                'devname': 'Ondrej Synacek',
                'web': 'https://github.com/comatory/flashCardStudy',
                'twitter': '@ondrejsynacek',
                'thanks': 'Luke Maurits (PrettyTable), ActiveState (appdirs)'
}

        return data

def author():
        data = author_data()
        print '\n', 21 * '-' 
        print data['devname'], '-', data['year'], '\n', 'web: ', data['web'], '\n','twitter: ', data['twitter']
        print '\n', 'Thanks:','\n', data['thanks'],'\n'
