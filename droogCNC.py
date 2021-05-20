"""
@author Liam Droog
"""

import tkinter as tk
import tkinter.font as font
import serial
import time
import numpy as np
import os
import h5py


class TwoAxisStage:

    def __init__(self, window, port, baud, startupfile):
        self.s = None
        self.window = window
        self.pos = [0., 0.]
        self.currentpos = 'X0 Y0'
        self.rate = 1
        self.rowLen = 5
        self.colLen = 9
        self.port = port
        self.baud = baud
        self.startupfile = startupfile
        self.connected = False
        self.queue = None
        self.tempFile = None
        self.temprunning = False
        self.filename = None
        self.buttonx = 12
        self.buttony = 6
        self.feedrate = 0
        self.shotnum = 0
        #self.dro_text = 'X: %1.3f, Y:%1.3f, Feedrate: %d' % (self.pos[0], self.pos[1], self.feedrate)
        self.datafile = None
        self.datafilename = None
        self.parameters = {
            'stepPulseLength': [0, None],
            'stepIdleDelay': [1, None],
            'axisDirection': [3, None],
            'statusReport': [10, None],
            'feedbackUnits': [13, None],
            'xSteps/mm': [100, None],
            'ySteps/mm': [101, None],
            'xMaxRate': [110, None],
            'yMaxRate': [111, None],
            'xMaxAcc': [120, None],
            'yMaxAcc': [121, None],
        }

        self.param_number = 2  ###########

        # draws all on-screen controls and assigns their event commands
        self.rowarr = list(i for i in range(self.rowLen))
        self.colarr = list(i for i in range(self.colLen))

        self.window.rowconfigure(self.rowarr, minsize=50, weight=1)
        self.window.columnconfigure(self.colLen, minsize=50, weight=1)

        # On screen control grid
        self.btn_w = tk.Button(master=self.window, text="\u219F", command=lambda: self.jogY(self.rate))
        self.btn_w['font'] = font.Font(size=18)
        self.btn_w.grid(row=1, column=2, sticky="nsew")

        self.btn_a = tk.Button(master=self.window, text="\u219E", command=lambda: self.jogX(-1 * self.rate))
        self.btn_a['font'] = font.Font(size=18)
        self.btn_a.grid(row=2, column=1, sticky="nsew")

        self.btn_s = tk.Button(master=self.window, text="\u21A1", command=lambda: self.jogY(-1 * self.rate))
        self.btn_s['font'] = font.Font(size=18)
        self.btn_s.grid(row=2, column=2, sticky="nsew")

        self.btn_d = tk.Button(master=self.window, text="\u21A0", command=lambda: self.jogX(self.rate))
        self.btn_d['font'] = font.Font(size=18)
        self.btn_d.grid(row=2, column=3, sticky="nsew")

        # serial connect button
        self.connect_btn = tk.Button(master=self.window, text='connect', fg='red',
                                     command=lambda: self.initSerial(self.port, self.baud, self.startupfile))
        self.connect_btn.grid(row=1, column=5, sticky='nsew')

        # 10 button
        self.btn_10 = tk.Button(master=self.window, text='10', command=lambda: self.switchRate(10))
        self.btn_10.grid(row=3, column=1, sticky='nsew')
        self.btn_10.configure(width=self.buttonx, height=self.buttony)
        # 1 button
        self.btn_1 = tk.Button(master=self.window, text='1', command=lambda: self.switchRate(1))
        self.btn_1.grid(row=3, column=2, sticky='nsew')
        self.btn_1.configure(width=self.buttonx, height=self.buttony)

        # 0.1 button
        self.btn_01 = tk.Button(master=self.window, text='0.1', command=lambda: self.switchRate(0.1))
        self.btn_01.grid(row=3, column=3, sticky='nsew')
        self.btn_01.configure(width=self.buttonx, height=self.buttony)
        # 0.01 button
        self.btn_001 = tk.Button(master=self.window, text='0.01', command=lambda: self.switchRate(0.01))
        self.btn_001.grid(row=3, column=4, sticky='nsew')
        self.btn_001.configure(width=self.buttonx, height=self.buttony)

        self.btn_0001 = tk.Button(master=self.window, text='0.001', command=lambda: self.switchRate(0.001))
        self.btn_0001.grid(row=3, column=5, sticky='nsew')
        self.btn_0001.configure(width=self.buttonx, height=self.buttony)

        # DRO frame
        self.lbl_frame = tk.Frame(master=self.window, relief=tk.RAISED, borderwidth=3)
        self.lbl_pos = tk.Label(master=self.lbl_frame, text='X: %1.3f, Y:%1.3f, Feedrate: %d'
                                                            % (self.pos[0], self.pos[1], self.feedrate))
        self.lbl_pos['font'] = font.Font(size=18)

        self.lbl_frame.grid(row=0, column=0, columnspan=self.colLen + 1, sticky='ew')
        self.lbl_pos.pack()

        # gcode input box
        self.gcode_entry = tk.Entry(master=self.window)
        self.gcode_entry.configure(width=40)
        self.gcode_entry.grid(row=4, column=6, sticky='wn')


        # gcode button
        self.gcode_send = tk.Button(master=self.window, text='Send',
                                    command=lambda: self.sendCommand(self.gcode_entry.get().rstrip() + '\n',
                                                                     resetarg=True,
                                                                     entry=self.gcode_entry))
        self.gcode_send.grid(row=4, column=9, sticky='ewn')
        self.gcode_send.configure(width=5)

        # file input box
        self.file_entry = tk.Entry(master=self.window)
        self.file_entry.grid(row=4, columnspan=3, sticky='new')

        # file input button
        self.file_input = tk.Button(master=self.window, text='Get File',
                                    command=lambda: self.getFile(self.file_entry.get()))
        self.file_input.grid(row=4, column=3, sticky='new')
        #self.file_input.configure(width=self.buttonx, height=self.buttony)

        # file run button
        self.file_run = tk.Button(master=self.window, text='Run', command=lambda: self.runFile())
        self.file_run.grid(row=4, column=4, sticky='new')
        self.file_run.configure(width=self.buttonx)

        self.kill_btn = tk.Button(master=self.window, text='Kill', command=self.killSwitch)
        self.kill_btn.grid(row=4, column=5, sticky='new')
        self.kill_btn.configure(width=self.buttonx)

        self.increment_btn = tk.Button(master=self.window, text='G91', command=self.setG91)
        self.increment_btn.grid(row=1, column=1, sticky='nsew')
        self.increment_btn.configure(width=self.buttonx, height=self.buttony)

        self.absolute_btn = tk.Button(master=self.window, text='G90', command=self.setG90)
        self.absolute_btn.grid(row=1, column=3, sticky='nsew')
        self.absolute_btn.configure(width=self.buttonx, height=self.buttony)

        # go home button
        self.home_btn = tk.Button(master=self.window, text='Go\nHome', command=lambda: self.sendCommand('G90 X0 Y0 F'
                                                                                                        + str(
            self.parameters['xMaxRate'][1])))
        self.home_btn.grid(row=2, column=4, sticky='nsew')
        self.home_btn.configure(width=self.buttonx, height=self.buttony)

        # set home button
        self.set_home = tk.Button(master=self.window, text='Set\nHome', command=lambda: self.sendCommand('G92 X0 Y0'))
        self.set_home.grid(row=1, column=4, sticky='nsew')
        self.set_home.configure(width=self.buttonx, height=self.buttony)

        self.start_from_death_btn = tk.Button(master=self.window, text='No temp\nfile found',
                                              command=self.__startFromDeath)
        self.start_from_death_btn.grid(row=2, column=5, sticky='nesw')
        self.start_from_death_btn['font'] = font.Font(size=10)
        self.start_from_death_btn.configure(width=self.buttonx, height=self.buttony)

        self.output = tk.Label(master=window, height=19, width=3*self.buttonx, anchor=tk.SW, justify=tk.LEFT)
        self.output.grid(columnspan=4, rowspan=4, row=1, column=6, sticky='new')
        self.output.configure(bg='white')
        self.window.bind('<Return>', (lambda x: self.sendCommand(self.gcode_entry.get(), entry=self.gcode_entry,
                                                                 resetarg=True)))



        self.__setTempFile()
        self.setKeybinds()
        self.Refresh()

    def setKeybinds(self):
        """
        binds keypress event to the onKeyPress function
        :return: None
        """
        self.window.bind('<KeyPress>', self.onKeyPress)

    def Refresh(self):
        """
        Sets recurring event to update GUI every 50ms
        :return: None
        """
        self.lbl_pos.configure(text='X: %1.3f, Y:%1.3f, Feedrate: %d' % (self.pos[0], self.pos[1], self.feedrate))
        self.window.after(5, self.Refresh)

    def onKeyPress(self, event, wasd=False):
        """
        Allows for stage control via WASD - Not sure if keeping implementation
        :param event: onKeyPress event
        :param wasd: if True, wasd controls the stage
        :return: None
        """
        if wasd:
            if event.char.lower() == 'w':
                self.jogY(self.rate)
            elif event.char.lower() == 'a':
                self.jogX(-1 * self.rate)
            elif event.char.lower() == 's':
                self.jogY(-1 * self.rate)
            elif event.char.lower() == 'd':
                self.jogX(self.rate)

    def jogX(self, v):
        """
        Jogs the X stage by the specified rate within the GUI
        :param v: float rate
        :return: None
        """
        if not self.temprunning:
            c = 'G91 x' + str(v) + '\n'
            self.sendCommand(c)

    def jogY(self, v):
        """
        Jogs the Y stage by the specified rate within the GUI
        :param v: float rate
        :return: None
        """
        if not self.temprunning:
            c = 'G91 y' + str(v) + '\n'
            self.sendCommand(c)

    def switchRate(self, v):
        """
        Switches current jog rate to specified input
        :param v: float jog rate
        :return:
        """
        # used to switch the rate's order of magnitude corresponding to pressed button
        self.rate = v

    def readOut(self):
        """
        Reads out the reply from GRBL
        :return: None
        """
        # implement own method?
        out = self.s.readline()  # Wait for grbl response with carriage return
        #print('> ' + out.strip().decode('UTF-8'))
        self.output['text'] += '\n>' + out.decode('UTF-8').strip()

    def sendCommand(self, gcode, resetarg=False, entry=None):
        """
        Sends command to GRBL. Checks if it is a comment, then sends command and updates DRO position accordingly
        :param gcode: command to be sent
        :param resetarg: used to detect if a command was sent via the input box so it knows to clear it
        :param entry: entry box instance to clear
        :return: None
        """
        # check if it's a comment
        if self.s:
            if gcode.strip() == '' or gcode.strip()[0] == ';':
                return
            t = gcode.rstrip().lower().split(' ')
            # check if it's a manual entry to clear entry box
            if resetarg and entry is not None:
                entry.delete(0, 'end')

            if 'g90' in t:
                self.setG90(cmd=False)
            if 'g91' in t:
                self.setG91(cmd=False)
            for i in t:
                if i.lower().strip()[0] == 'f':
                    self.__setFeed(int(i.strip()[1:]))

            #self.output['text'] += '\n' + time.strftime('%H:%M:%S', time.localtime()) + ': ' + gcode.rstrip()
            self.output['text'] += '\n' + '~> ' + gcode.rstrip()
            gcode = gcode.rstrip() + '\n'
            self.s.write(gcode.encode('UTF-8'))
            self.readOut()
            # self.__writeData([time.time_ns(), gcode.rstrip()])
            self.setPos(gcode)

    def initSerial(self, port, baud, filename):
        """
        Initalizes serial connection with grbl doohickey. Parses all startup commands from a text file input
        :param port: USB port board is plugged into
        :param baud: communication baud rate
        :param filename: startup filename containing startup grbl code
        :return: None
        """
        if not self.connected:
            try:
                self.s = serial.Serial(port, baud)
            except:
                print('Borked connection, try again.')
            else:
                # Wake up grbl
                self.s.write(b"\r\n\r\n")
                # allow grbl to initialize
                time.sleep(2)
                # flush startup from serial
                self.s.flushInput()
                # open startup file
                with open(filename, 'r') as f:
                    for line in f:
                        # strip EOL chars
                        l = line.strip()
                        self.sendCommand(l + '\r')
                print('Connected to GRBL')
                self.connect_btn.configure(fg='green', text='Connected')
                self.connected = True
                self.__parseParameters()

        else:
            self.connected = False
            self.s.close()
            self.s = None
            self.queue = None
            print('Connection closed')
            self.connect_btn.configure(fg='red', text='Connect')

    def setG91(self, cmd=True):
        """
        Sets relative movements active
        :param cmd: If true, send the G91 command, regardless, switch button text color to match
        :return: None
        """
        if self.s:
            if cmd:
                self.sendCommand('G91')
            self.increment_btn.configure(fg='green')
            self.absolute_btn.configure(fg='black')

    def setG90(self, cmd=True):
        """
        Sets absolute movements active
        :param cmd: If true, send the G90 command, regardless, switch button text color to match
        :return: None
        """
        if self.s:
            if cmd:
                self.sendCommand('G90')
            self.increment_btn.configure(fg='black')
            self.absolute_btn.configure(fg='green')

    def setPos(self, cmd):
        """
        sets position of table on DRO
        :param cmd: gcode command containing new location
        :return: None
        """
        # g91 iterates, not sets
        if cmd[:3].lower() == 'g91':
            for i in cmd.split(' '):
                if i.lower()[0] == 'x':
                    self.pos[0] += float(i[1:])
                if i.lower()[0] == 'y':
                    self.pos[1] += float(i[1:])
        else:
            for i in cmd.split(' '):
                if i.lower()[0] == 'x':
                    self.pos[0] = float(i[1:])
                if i.lower()[0] == 'y':
                    self.pos[1] = float(i[1:])

    def getFile(self, filename):
        """
        Opens file containing gcode. Does not parse for correctness.
        Inputs all non blank lines / comments into a queue for usage
        :param filename: File to open
        :return: None
        """
        # queue with timing calculation for next move
        # wipe queue
        self.queue = None
        try:
            self.filename = filename
            f = open(filename, 'r')
            self.queue = Queue()
            for line in f:
                if line != '' and line[0] != ';':
                    self.queue.enqueue(line)
            print('Loaded ' + filename)
            self.output['text'] += '\n~>' + ' Loaded '+filename
        except FileNotFoundError:
            self.file_entry.delete(0, 'end')
            self.output['text'] += '\n!> File does not exist'

    def runFile(self):
        """
        Used to run a file obained with getFile()
        :return: None
        """
        if self.s:
            if not self.temprunning:
                print('calling savetemp')
                self.temprunning = True
                self.__saveTempData()

            nextpos = self.queue.dequeue()
            self.sendCommand(nextpos)

            if self.queue.size() > 0:
                self.window.after(self.calcDelay(self.currentpos, nextpos), self.runFile)
                self.currentpos = nextpos

            elif self.queue.size() == 0:
                self.window.after(self.calcDelay(self.currentpos, nextpos), self.finishRun)

            else:
                self.temprunning = False
                return

    def finishRun(self):
        """
        Runs after file completion, removes contingency file since it is not needed.
        :return: None
        """
        print('File run complete')
        self.__removeTempFile()

    def killSwitch(self):
        """
        effectively kills current gcode run by clearing queue. Note this isn't instantaneous
        :return: None
        """
        if self.s:
            self.queue.clear()
            self.temprunning = False
            self.output['text'] += '\n!> Current motion killed'

    def calcDelay(self, currentpos, nextpos):
        """
        Calculates a lower end of the required delay between moved for the queue command system
        :param currentpos: Current position
        :param nextpos: Next position
        :return: time delay in ms
        """
        #   todo: parse feeds & speeds from startup file
        #         calculate (approximate?) time delay until next step
        #         circular motion

        ipos = self.__parsePosition(currentpos)
        fpos = self.__parsePosition(nextpos)
        assert len(ipos) == len(fpos), 'Input arrays must be same length'

        v = float(self.parameters['xMaxRate'][1]) / 60
        a = float(self.parameters['xMaxRate'][1]) # becomes very choppy changing to xMaxAcc... idk wtf

        delta = list(ipos[i] - fpos[i] for i in range(len(ipos)))
        d = np.sqrt(sum(i ** 2 for i in delta))
        deltaT = ((2 * v) / a) + ((d - (v ** 2 / a)) / v)
        print('next move in ' + str(int(np.floor(deltaT * 1000))) + 'ms')
        return int(np.floor(deltaT * 1000))  # in ms

    def __parsePosition(self, ipos):
        """
        Parses position for use with DRO
        :param ipos: input position
        :return: [x, y] list of current position
        """
        pos = [0, 0]
        for i in ipos.split(' '):
            if i.lower()[0] == 'x':
                pos[0] = float(i[1:])
            if i.lower()[0] == 'y':
                pos[1] = float(i[1:])
        return pos

    def __parseParameters(self):
        """
        Parses parameters from a given input file into the parameters dictionary for usage
        :return: None
        """
        tmp = []
        with open(self.startupfile, 'r') as f:
            for line in f:
                if line != '' and line[0] == '$':
                    tmp.append(line.strip().strip('$'))
        f.close()
        for i in tmp:
            for key, value in self.parameters.items():
                if i.split('=')[0] == str(value[0]):
                    self.parameters[key] = [i.split('=')[0], i.split('=')[1]]

        self.feedrate = int(self.parameters['xMaxRate'][1])
        print(self.feedrate)
        print(self.parameters['xMaxRate'])
        print(self.parameters['xMaxAcc'])

    def __setTempFile(self):
        """
        Sets the temporary file name, unless it exists
        :return: None
        """
        if os.path.exists('temp.npy') or self.tempFile is not None:
            self.start_from_death_btn.configure(text='Load\nData?', fg='red')
            self.__blinkButton(self.start_from_death_btn, 'red', 'blue', 1000)
        else:
            self.tempFile = 'temp.npy'

    def __saveTempData(self):
        """
        Saves temp data to temp file, if program is currently running it calls itself every 1000ms
        :return: None
        """
        if self.temprunning:
            if self.queue.size() > 0:
                np.save(self.tempFile, [self.queue.peek(), time.asctime(), self.filename, self.shotnum])
                self.window.after(1000, self.__saveTempData)
                return True
        else:
            return False

    def __retrieveTempData(self):
        """
        Retrieves temp data from temp.npy if it exists and user calls it. Needs to be updated
        to reflect final changes in temp data stored once integrated into laser system
        :return: Last line that runfile stored before unexpected power loss
        #todo save position and reload it
        """
        self.tempFile = 'temp.npy'
        currentline, t, self.filename, self.shotnum = np.load(self.tempFile)
        print(currentline, t, self.filename)
        return currentline

    def __startFromDeath(self):
        """
        Starts from an unexpected power loss. Retreives last known position from temp file.
        Issues: Target stage *could* be manually moved on us prior to reviving. User initiative to ensure
        nothing moves.
        :return: None
        """
        if self.s:
            self.queue = None
            currentline = self.__retrieveTempData()
            try:
                f = open(self.filename, 'r')
                self.queue = Queue()
                positionFound = False
                for line in f:
                    if line == currentline:
                        positionFound = True
                    if positionFound:
                        if line != '' and line[0] != ';':
                            self.queue.enqueue(line)
                print('Loaded ' + self.filename)
                self.start_from_death_btn.configure(text='Start?', fg='green', command=self.runFile)
            except FileNotFoundError:
                self.file_entry.delete(0, 'end')
                self.file_entry.insert(0, 'File does not exist')
        else:
            self.start_from_death_btn.configure(text='Not\nconnected')
            self.window.after(5000, lambda: self.start_from_death_btn.configure(text='Load\nData?'))

    def __removeTempFile(self):
        """
        removes temp file at end of program run
        :return: None
        """
        os.remove(self.tempFile)
        self.tempFile = None

    def __blinkButton(self, button, c1, c2, delay):
        """
        Blinks a button between two colors, c1 and c2. Has logic for specific buttons to cease switching given a
        specific string as the text.
        :param button: target button instance
        :param c1: First color to switch to, string
        :param c2: Second color to switch to, string
        :param delay: Delay in ms
        :return: None
        """
        if button['text'] == 'Start?':
            return
        else:
            if button['fg'] == c1:
                button.configure(fg=c2)
            else:
                button.configure(fg=c1)
            self.window.after(delay, lambda: self.__blinkButton(button, c1, c2, delay))

    def __createDataFile(self):
        self.datafilename = str('-'.join(list(i.replace(':', '-') for i in time.asctime().split(' ')))) + '.hdf5'
        self.datafile = HDF5File(self.datafilename)

    def __createGroup(self, name):
        self.datafile.createGroup(name)

    def __setMetadataFromFile(self, mdfile, path='/'):
        metadata = self.__parseMetadataFile(mdfile)
        for key, value in metadata.items():
            self.datafile.setMetadata(key, value, path=path)

    def __setMetadata(self, key, value, path='/'):
        self.datafile.setMetadata(key, value, path=path)

    def __createDataSet(self, Group, Data):
        self.datafile.create_dataset(Group, Data, Data.shape)

    def __parseMetadataFile(self, filename):
        md = {}
        try:
            with open(filename, 'r') as f:
                for i in f.readlines():
                    j = i.rstrip().split(';')
                    md[j[0]] = j[1]
            return md

        except:
            print('metadata file broken, fix and try again')

    def __writeData(self, data):
        """
        Writes data to the class instances datafile
        :param data: Data to write
        :return: None
        """
        self.datafile.append(data)

    def __setFeed(self, feedrate):
        """
        Sets feedrate based on input
        :param feedrate: New feedrate in mm/min
        :return: None
        """
        self.feedrate = feedrate


class Queue:
    # Creates a new empty queue:
    def __init__(self):
        self.__items = []  # init the  list / queue as empty

    # Adds a new item to the back of the queue, and returns nothing:
    def enqueue(self, item, idx=None):
        """
        Enqueue the element to the back of the queue
        :param item: the element to be enqueued
        :return: No returns
        """
        if item.strip() == '':
            return
        if idx is None:
            self.__items.append(item)
        else:
            self.__items.insert(idx, item)

    # Removes and returns the front-most item in the queue.
    # Returns nothing if the queue is empty.
    def dequeue(self):
        """
        Dequeue the element from the front of the queue and return it
        :return: The object that was dequeued
        """
        if len(self.__items) <= 0:
            raise Exception('Error: Queue is empty')
        return self.__items.pop(0)

    def peek(self):
        """
        Returns the front-most item in the queue, and DOES NOT change the queue.
        :return: front-most item in the queue
        """
        if len(self.__items) <= 0:
            raise Exception('Error: Queue is empty')
        return self.__items[0]

    def is_empty(self):
        """
        :return: True if the queue is empty, and False otherwise
        """
        return len(self.__items) == 0

    def size(self):
        """
        :return: The number of items in the queue
        """
        return len(self.__items)

    #
    def clear(self):
        """
        Removes all items from the queue
        :return: None
        """
        self.__items = []

    # Returns a string representation of the queue:
    def __str__(self):
        """
        :return: String representation of the queue
        """
        str_exp = ""
        for item in self.__items:
            str_exp += ('> ' + str(item))
        return str_exp


class HDF5File:

    def __init__(self, datapath):
        self.datapath = datapath

    def append(self, group, dataset, values):
        with h5py.File(self.datapath, mode='a') as h5f:
            i = 0
            dset = h5f[group][dataset]
            dset.resize((i + 1,) + values.shape)
            dset[i] = [values]
            i += 1
            h5f.flush()

    def setMetadata(self, attribute, value, path='/'):
        with h5py.File(self.datapath, mode='a') as h5f:
            h5f[path].attrs[attribute] = value

    def createDataset(self, group, dataset, shape, compression='gzip'):
        with h5py.File(self.datapath, mode='a') as h5f:
            h5f[group].create_dataset(
                dataset,
                shape=(0,) + shape,
                maxshape=(None,) + shape,
                compression=compression)

    def createGroup(self, name):
        with h5py.File(self.datapath, mode='a') as h5f:
            h5f.create_group(name)
