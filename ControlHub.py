import tkinter as tk
from tkinter import font
from droogCNC import TwoAxisStage
from HDF5Browser import FileBrowser
import serial.tools.list_ports
from ImageViewer import ImageFrame
from PIL import Image, ImageTk
import numpy as np
import matplotlib.pyplot as plt
import serial
import time
import os
import cv2


class ControlHub:
    """Spawns a control hub for the laser system with various functionalities.
    Usage consists of instantiating a class and calling the .start() method

    """

    def __init__(self):
        self.window = tk.Tk(className='\Control Hub')
        self.screenwidth = str(int(self.window.winfo_screenwidth() * 0.35))
        self.screenheight = str(int(self.window.winfo_screenheight() * 0.35))
        self.window.geometry(self.screenwidth + 'x' + self.screenheight)
        self.grid = [16, 9]
        self.rowarr = list(i for i in range(self.grid[1]))
        self.colarr = list(i for i in range(self.grid[0]))
        self.window.rowconfigure(self.rowarr, minsize=25, weight=1)
        self.window.columnconfigure(self.colarr, minsize=25, weight=1)
        self.shotnum = 0
        self.imageframe = None
        self.imageframerunning = False

        # title
        self.title_frame = tk.Frame(master=self.window, relief='raised', borderwidth=2)
        self.title_label = tk.Label(master=self.title_frame, text='Control Hub Ver.0.1')
        self.title_frame.grid(row=0, column=0, columnspan=self.grid[0], sticky='new')
        self.title_label['font'] = font.Font(size=18)
        self.title_label.pack()

        # frame for launch buttons
        self.launch_frame = tk.Frame(master=self.window, relief='groove', borderwidth=3)
        self.launch_frame.grid(row=1, column=0, rowspan=9, columnspan=3, sticky='nsew')
        # stage gui launch btn
        self.start_stage_btn = tk.Button(master=self.launch_frame, text='Launch Stage Control',
                                         command=self.__launchStageControl)
        self.start_stage_btn.grid(row=0, column=0, columnspan=3, sticky='nsew')

        # Com port
        comlist = [comport.device for comport in serial.tools.list_ports.comports()]
        self.comval = tk.StringVar(self.launch_frame)
        # comval.set('Select Com Port')
        self.comval.set('COM4')
        self.comlabel = tk.Label(master=self.launch_frame, text='COM Port:')
        self.comlabel.grid(row=2, column=0, sticky='news')
        self.com = tk.OptionMenu(self.launch_frame, self.comval, *comlist)
        self.com.grid(row=2, column=1, sticky='nsew')

        # baud
        baudlist = [9600, 115200]
        self.baudval = tk.IntVar(self.launch_frame)
        self.baudval.set('115200')
        self.baudlabel = tk.Label(master=self.launch_frame, text='Baud Rate: ')
        self.baudlabel.grid(row=3, column=0, sticky='news')
        self.baud = tk.OptionMenu(self.launch_frame, self.baudval, *baudlist)
        self.baud.grid(row=3, column=1, sticky='nsew')

        # startup file
        self.filelabel = tk.Label(master=self.launch_frame, text='Startup File: ')
        self.filelabel.grid(row=4, column=0, sticky='news')
        self.startfile = tk.Entry(master=self.launch_frame)
        self.startfile.insert(0, 'Data\\startup.txt')
        self.startfile.grid(row=4, column=1, sticky='nsew')

        # file browser gui button
        self.file_browser_btn = tk.Button(master=self.launch_frame, text='HDF5 File Browser',
                                          command=self.__launchHDFGUI)
        self.file_browser_btn.grid(row=5, column=0, columnspan=3, sticky='news')

        self.get_spectra_btn = tk.Button(master=self.window, text='Get shot spectra', command=self.__captureimage)
        self.get_spectra_btn.grid(row=1, column=4, columnspan=4, sticky='nsew')

    def start(self):
        """
        Calls tkinter's mainloop function to start GUI

        :return: None
        """
        self.window.mainloop()

    def __launchStageControl(self):
        """
        Instantiates a TwoAxisStage control GUI for the two axis stage from it's respective class

        :return: None
        """
        try:
            x = TwoAxisStage(self.comval.get(), self.baudval.get(), self.startfile.get())

        except Exception as e:
            print(e)
        else:
            x.start()

    def __launchHDFGUI(self):
        """
        Instantiates a FileBrowser control GUI from it's respective class. Used to interact with HDF5 files easily

        :return: None
        """
        x = FileBrowser()
        x.start()

    def __captureimage(self):
        cam = cv2.VideoCapture(0)
        ret, frame = cam.read()
        if not ret:
            print("failed to grab frame")
        else:
            imgname = 'images/spectra_shot_00' + str(self.shotnum) + '.png'
            cv2.imwrite(imgname, frame)
            self.shotnum += 1
            print(self.imageframerunning)

            if not self.imageframerunning:
                self.imageframerunning = True
                self.imageframe = ImageFrame('Chad ->', imgname)
            else:
                print('added')
                self.imageframe.addImage(imgname)

    def __getspectra(self):
        # this will get the plot of most recent shot spectra
        pass
