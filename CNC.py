import tkinter as tk
from droogCNC import TwoAxisStage


def main():

    # initalize gui
    window = tk.Tk(className='\DRO Test')

    # pass window to gui class and initialize
    stagectrl = TwoAxisStage(window, 'COM4', 115200, 'startup.txt')


    # start the gui loop
    window.mainloop()


if __name__ == '__main__':
    main()
