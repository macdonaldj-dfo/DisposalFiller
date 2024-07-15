import sys, os

sys.path.append(os.getcwd() + '/src/lib/')

from gui import *

if __name__ == "__main__":

    if "debug" in sys.argv:
        debug = True
    else:
        debug = False

    App(debug)



