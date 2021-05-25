import tkinter as tk
from droogCNC import TwoAxisStage


def main():

    # initalize gui


    # pass window to gui class and initialize
    stagectrl = TwoAxisStage('COM4', 115200, 'startup.txt')

    # start the gui loop
    stagectrl.start()

    # popup window to manually add files or groups
if __name__ == '__main__':
    main()
