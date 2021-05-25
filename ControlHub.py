import tkinter as tk
from tkinter import font
from droogCNC import TwoAxisStage
from HDF5Browser import FileBrowser
import numpy as np
import matplotlib.pyplot as plt
import serial
import time
import os

class ControlHub:
    def __init__(self):
        self.window = tk.Tk(className='Control Hub')
        self.screenwidth = str(int(self.window.winfo_screenwidth() * 0.35))
        self.screenheight = str(int(self.window.winfo_screenheight() * 0.35))
        self.window.geometry(self.screenwidth + 'x' + self.screenheight)
        self.grid = [16, 9]
        self.rowarr = list(i for i in range(self.grid[1]))
        self.colarr = list(i for i in range(self.grid[0]))
        self.window.rowconfigure(self.rowarr, minsize=25, weight=1)
        self.window.columnconfigure(self.colarr, minsize=25, weight=1)

        # title
        self.title_frame = tk.Frame(master=self.window, relief='raised', borderwidth=2)
        self.title_label = tk.Label(master=self.title_frame, text='Control Hub Ver.0.1')
        self.title_frame.grid(row=0, column=0, columnspan=self.grid[0], sticky='new')
        self.title_label['font'] = font.Font(size=18)
        self.title_label.pack()

        # frame for launch buttons
        self.launch_frame = tk.Frame(master=self.window, relief='groove', borderwidth=3)
        self.launch_frame.grid(row=1, column=2, rowspan=9, columnspan=3, sticky='nsew')
        # stage gui launch btn
        self.start_stage_btn = tk.Button(master=self.launch_frame, text='Launch Stage GUI',
                                         command=self.__launchStageControl)
        self.start_stage_btn.grid(row=0, column=0, sticky='nsew')
        # file browser gui button
        self.file_browser_btn = tk.Button(master=self.launch_frame, text='HDF5 File Browser',
                                          command=self.__launchHDFGUI)
        self.file_browser_btn.grid(row=1, column=0, sticky='news')

    def start(self):
        self.window.mainloop()

    def __launchStageControl(self):
        x = TwoAxisStage('COM4', 115200, 'startup.txt')
        x.start()

    def __launchHDFGUI(self):
        x = FileBrowser()
        x.start()
