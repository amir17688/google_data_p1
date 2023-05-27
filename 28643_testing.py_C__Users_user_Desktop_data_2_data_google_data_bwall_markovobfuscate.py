__author__ = 'bwall'
import markovobfuscate.obfuscation as obf
import logging
import re
import random

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    # Regular expression to split our training files on
    split_regex = r'\n'

    # File/book to read for training the Markov model (will be read into memory)
    training_file = "datasets/lyrics.ts.txt"

    # Obfuscating Markov engine
    m1 = obf.MarkovKeyState()
    m2 = obf.MarkovKeyState()

    # Read the shared key into memory
    with open(training_file, "r") as f:
        text = f.read()

    # Split learning data into sentences, in this case, based on periods.
    map(m1.learn_sentence, re.split(split_regex, text))
    map(m2.learn_sentence, re.split(split_regex, text))

    try:
        logging.info("Hit CTRL-C to stop testing")
        while True:
            # Run a random test
            rand_string = "".join([chr(random.randint(0, 255)) for k in xrange(random.randint(1, 1024))])
            if rand_string != m2.deobfuscate_string(m1.obfuscate_string(rand_string)):
                print "Failed integrity test"
                raise
    except KeyboardInterrupt:
        pass