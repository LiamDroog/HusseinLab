import tkinter as tk
from tkinter import font, messagebox
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
from datetime import date


class ControlHub:
    """Spawns a control hub for the laser system with various functionalities.
    Usage consists of instantiating a class and calling the .start() method

    """

    def __init__(self):
        self.window = tk.Tk(className='\Baldr Control Hub')
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
        self.laserArmed = False

        # title
        self.title_frame = tk.Frame(master=self.window, relief='raised', borderwidth=2)
        self.title_label = tk.Label(master=self.title_frame, text='Baldr Laser Control Hub Ver 0.0.1')
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
        self.startfile.insert(0, 'Config/startup.txt')
        self.startfile.grid(row=4, column=1, sticky='nsew')

        # hdf5 storage file
        today = date.today()
        self.h5filepath = 'datafiles/'+today.strftime("%b-%d-%Y")

        if self.__createdir(self.h5filepath):
            print('dir made')
        else:
            print('dir exists already')
        # shoot the laser button
        self.armLaser_btn = tk.Button(master=self.launch_frame, text='Arm Laser', fg='#C02f1d',
                                        command=self.__armLaser)
        self.armLaser_btn.grid(column=0, columnspan=2, row=6, sticky='nsew')

        self.shootLaser_btn = tk.Button(master=self.launch_frame, text='Fire Laser', bg='#BEBEBE')
        self.shootLaser_btn.grid(column=0, columnspan=2, row=7, sticky='nsew')

        # file browser gui button
        self.file_browser_btn = tk.Button(master=self.launch_frame, text='HDF5 File Browser',
                                          command=self.__launchHDFGUI)
        self.file_browser_btn.grid(row=5, column=0, columnspan=3, sticky='news')

        self.get_spectra_btn = tk.Button(master=self.window, text='Get shot spectra',
                                         command=lambda: self.__sendStageMove('g0 x10 y10'))
        self.get_spectra_btn.grid(row=1, column=4, columnspan=4, sticky='nsew')
        # self.window.protocol("WM_DELETE_WINDOW", self.__on_closing)
        self.filebrowser = None

        self.stage = None

    def start(self):
        """
        Calls tkinter's mainloop function to start GUI

        :return: None
        """
        self.window.mainloop()

    def __on_closing(self):
        if messagebox.askokcancel("Quit", "Quit? This will close all windows."):
            self.window.destroy()

    def __armLaser(self):
        if not self.laserArmed:
            self.armLaser_btn.config(bg='#228C22', fg='#FFFFFF')
            self.shootLaser_btn.config(command=lambda: print('Pew Pew!'), bg='#c02f1d', fg='#FFFFFF')
            self.laserArmed = True
        else:
            self.armLaser_btn.config(bg='#F0F0F0', fg='red')
            self.shootLaser_btn.config(command=tk.NONE, bg='#BEBEBE', fg='#000000')
            self.laserArmed = False

    def __fireLaser(self):
        """
        No functionality as of yet. This will need to assert laser actually fired, send triggers to spectrometers and
        sensors, and record all data coming back. Since python is a single-threaded monster, I have been toying around
        with the idea of an external script that is fed data via a multithreaded pipe into a queue, where the data
        has both a target file and data to write. This way we can increase laser firing speed as we dont always have
        to wait for all data to write. Though, I'm not sure if this is necessary. Really, it's contingent on bandwidth
        data being collected.
        :return: None
        """
        pass

    def __launchStageControl(self):
        """
        Instantiates a TwoAxisStage control GUI for the two axis stage from it's respective class

        :return: None
        """
        try:
            self.stage = TwoAxisStage(self.comval.get(), self.baudval.get(), self.startfile.get())

        except Exception as e:
            print(e)
        else:
            return

    def __launchHDFGUI(self):
        """
        Instantiates a FileBrowser control GUI from it's respective class. Used to interact with HDF5 files easily.
        Error handling is totally hacked and should be re-thought

        :return: None
        """
        try:
            if self.filebrowser.state():
                return
        except AttributeError:
            pass
        except FileNotFoundError:
            self.filebrowser = None

        if not self.filebrowser:
            self.filebrowser = FileBrowser()

    def __createdir(self, name):
        try:
            os.makedirs(name)
        except OSError:
            return False
        else:
            return True

    def __createShotFile(self, filename):
        pass

    def __sendStageMove(self, cmd):
        self.stage.sendCommand(cmd)

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

    def __getRunFile(self, filename):
        pass