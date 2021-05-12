import tkinter as tk
import tkinter.font as font
import serial
import time
import numpy as np

class TwoAxisStage:
    # todo queue implementaion for stopping stuff
    # g92 after jog fails

    def __init__(self, window, port, baud, startupfile):
        self.s = None
        self.window = window
        self.pos = [0., 0.]
        self.currentpos = 'X0 Y0'
        self.rate = 1
        self.rowLen = 6
        self.colLen = 5
        self.port = port
        self.baud = baud
        self.startupfile = startupfile
        self.connected = False
        self.queue = None
        self.parameters = {
            'stepPulseLength'   : [0, None],
            'stepIdleDelay'     : [1, None],
            'axisDirection'     : [3, None],
            'statusReport'      : [10, None],
            'feedbackUnits'     : [13, None],
            'xSteps/mm'         : [100, None],
            'ySteps/mm'         : [101, None],
            'xMaxRate'          : [110, None],
            'yMaxRate'          : [111, None],
            'xMaxAcc'           : [120, None],
            'yMaxAcc'           : [121, None],
            }
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
        self.connect_btn.grid(row=1, column=5)
        # 10 button
        self.btn_jog = tk.Button(master=self.window, text='10', command=lambda: self.switchRate(10))
        self.btn_jog.grid(row=3, column=0, sticky='nsew')

        # 1 button
        self.btn_1 = tk.Button(master=self.window, text='1', command=lambda: self.switchRate(1))
        self.btn_1.grid(row=3, column=1, sticky='nsew')

        # 0.1 button
        self.btn_01 = tk.Button(master=self.window, text='0.1', command=lambda: self.switchRate(0.1))
        self.btn_01.grid(row=3, column=2, sticky='nsew')

        # 0.01 button
        self.btn_001 = tk.Button(master=self.window, text='0.01', command=lambda: self.switchRate(0.01))
        self.btn_001.grid(row=3, column=3, sticky='nsew')

        self.btn_0001 = tk.Button(master=self.window, text='0.001', command=lambda: self.switchRate(0.001))
        self.btn_0001.grid(row=3, column=4, sticky='nsew')

        # DRO frame
        self.lbl_frame = tk.Frame(master=self.window, relief=tk.RAISED, borderwidth=3)
        self.lbl_pos = tk.Label(master=self.lbl_frame, text='X: %1.3f, Y:%1.3f' % (self.pos[0], self.pos[1]))
        self.lbl_pos['font'] = font.Font(size=15)

        self.lbl_frame.grid(row=0, column=0, columnspan=self.colLen, sticky='')
        self.lbl_pos.pack()

        # gcode input box
        self.gcode_entry = tk.Entry(master=self.window)
        self.gcode_entry.grid(row=4, columnspan=3, sticky='ew')

        # gcode button
        self.gcode_send = tk.Button(master=self.window, text='Send',
                                    command=lambda: self.sendCommand(self.gcode_entry.get().rstrip() + '\n', resetarg=True,
                                                                     entry=self.gcode_entry))
        self.gcode_send.grid(row=4, column=3, sticky='')

        # file input box
        self.file_entry = tk.Entry(master=self.window)
        self.file_entry.grid(row=5, columnspan=3, sticky='ew')

        # file input button
        self.file_input = tk.Button(master=self.window, text='Get File', command=lambda: self.getFile(self.file_entry.get()))
        self.file_input.grid(row=5, column=3)

        # file run button
        self.file_run = tk.Button(master=self.window, text='Run', command=lambda: self.runFile())
        self.file_run.grid(row=5, column=4)

        self.kill_btn = tk.Button(master=self.window, text='Kill', command=self.killSwitch)
        self.kill_btn.grid(row=5, column=5)

        self.Refresh()

    def setKeybinds(self):
        self.window.bind('<KeyPress>', self.onKeyPress)

    def Refresh(self):
        self.lbl_pos.configure(text='X: %1.3f, Y:%1.3f' % (float(self.pos[0]), float(self.pos[1])))
        # print(time.perf_counter_ns(), pos)
        self.window.after(50, self.Refresh)

    def onKeyPress(self, event, wasd=False):
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
        # increments the X counter by specified v, set by the rate
        c = 'G91 x' + str(v) + '\n'
        self.sendCommand(c)

    def jogY(self, v):
        # increments the Y counter by specified v, set by the rate
        c = 'G91 y' + str(v) + '\n'
        self.sendCommand(c)

    def switchRate(self, v):
        # used to switch the rate's order of magnitude corresponding to pressed button
        self.rate = v

    def readOut(self):
        # todo: Fix borked DRO feedback
        # implement own method?
        out = self.s.readline()  # Wait for grbl response with carriage return
        print('> ' + out.strip().decode('UTF-8'))

    def sendCommand(self, gcode, resetarg=False, entry=None):
        # check if it's a comment
        if gcode != '' and gcode.strip()[0] == ';':
            return

        # check if it's a manual entry to clear entry box
        if resetarg and entry is not None:
            entry.delete(0, 'end')

        print('Sent: ' + gcode.rstrip())

        self.s.write(gcode.encode('UTF-8'))
        self.readOut()
        self.setPos(gcode)

    def initSerial(self, port, baud, filename):
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
            self.s.close()
            self.s = None
            self.queue = None
            print('Connection closed')
            self.connect_btn.configure(fg='red', text='Connect')

    def setPos(self, cmd):
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
        # queue with timing calculation for next move
        # wipe queue
        self.queue = None
        try:
            f = open(filename, 'r')
            self.queue = Queue()
            for line in f:
                if line != '' and line[0] != ';':
                    self.queue.enqueue(line)
            print('Loaded ' + filename)
        except FileNotFoundError:
            self.file_entry.delete(0, 'end')
            self.file_entry.insert(0, 'File does not exist')

    def runFile(self):
        nextpos = self.queue.dequeue()
        self.sendCommand(nextpos)
        if self.queue.size() > 0:
            self.window.after(self.calcDelay(self.currentpos, nextpos), self.runFile)
            self.currentpos = nextpos
        else:
            return

    def killSwitch(self):
        self.queue.clear()
        print('Current motion was killed')

    def calcDelay(self, currentpos, nextpos):
        #   todo: parse positions from gcode
        #         parse feeds & speeds from startup file
        #         calculate (approximate?) time delay until next step

        ipos = self.__parsePosition(currentpos)
        fpos = self.__parsePosition(nextpos)
        assert len(ipos) == len(fpos), 'Input arrays must be same length'

        v = float(self.parameters['xMaxRate'][1]) / 60
        a = float(self.parameters['yMaxRate'][1])

        delta = list(ipos[i] - fpos[i] for i in range(len(ipos)))
        d = np.sqrt(sum(i ** 2 for i in delta))
        deltaT = ((2 * v) / a) + ((d - (v ** 2 / a)) / v)
        print('next move in ' + str(int(np.floor(deltaT * 1000))) + 'ms')
        return int(np.floor(deltaT * 1000))    # in ms

    def __parsePosition(self, ipos):
        pos = [0, 0]
        for i in ipos.split(' '):
            if i.lower()[0] == 'x':
                pos[0] = float(i[1:])
            if i.lower()[0] == 'y':
                pos[1] = float(i[1:])
        return pos

    def __parseParameters(self):
        tmp = []
        with open(self.startupfile, 'r') as f:
            pv = list(self.parameters.values())
            for line in f:
                if line != '' and line[0] == '$':
                    tmp.append(line.strip().strip('$'))
        f.close()
        for i in tmp:
            for key, value in self.parameters.items():
                if i.split('=')[0] == str(value[0]):
                    print(key, i, value)
                    self.parameters[key] = [i.split('=')[0], i.split('=')[1]]


class Queue:
    # Creates a new empty queue:
    def __init__(self):
        self.__items = []  # init the  list / queue as empty

    # Adds a new item to the back of the queue, and returns nothing:
    def enqueue(self, item, idx=None):
        '''
        Enqueue the element to the back of the queue
        :param item: the element to be enqueued
        :return: No returns
        '''
        if idx is None:
            self.__items.append(item)
        else:
            self.__items.insert(idx, item)

    # Removes and returns the front-most item in the queue.
    # Returns nothing if the queue is empty.
    def dequeue(self):
        '''
        Dequeue the element from the front of the queue and return it
        :return: The object that was dequeued
        '''
        if len(self.__items) <= 0:
            raise Exception('Error: Queue is empty')
        return self.__items.pop(0)

    # Returns the front-most item in the queue, and DOES NOT change the queue.
    def peek(self):
        if len(self.__items) <= 0:
            raise Exception('Error: Queue is empty')
        return self.__items[0]

    # Returns True if the queue is empty, and False otherwise:
    def is_empty(self):
        return len(self.__items) == 0

    # Returns the number of items in the queue:
    def size(self):
        return len(self.__items)

    # Removes all items from the queue, and sets the size to 0
    # clear() should not change the capacity
    def clear(self):
        self.__items = []

    # Returns a string representation of the queue:
    def __str__(self):
        str_exp = ""
        for item in self.__items:
            str_exp += (str(item))
        return str_exp
