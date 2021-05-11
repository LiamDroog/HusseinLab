import tkinter as tk
import tkinter.font as font
import serial
import time


class TwoAxisStage:
    # todo queue implementaion for stopping stuff
    # g92 after jog fails

    def __init__(self, window, port, baud, startupfile):
        self.s = None
        self.window = window
        self.pos = [0., 0.]
        self.rate = 1
        self.rowLen = 6
        self.colLen = 5
        self.port = port
        self.baud = baud
        self.startupfile = startupfile

        # draws all on-screen controls and assigns their event commands
        self.rowarr = list(i for i in range(self.rowLen))
        self.colarr = list(i for i in range(self.colLen))

        self.window.rowconfigure(self.rowarr, minsize=50, weight=1)
        self.window.columnconfigure(self.colLen, minsize=50, weight=1)

        # On screen control grid
        self.btn_w = tk.Button(master=self.window, text="\u219F", command=lambda: self.incY(self.rate))
        self.btn_w['font'] = font.Font(size=18)
        self.btn_w.grid(row=1, column=2, sticky="nsew")

        self.btn_a = tk.Button(master=self.window, text="\u219E", command=lambda: self.incX(-1 * self.rate))
        self.btn_a['font'] = font.Font(size=18)
        self.btn_a.grid(row=2, column=1, sticky="nsew")

        self.btn_s = tk.Button(master=self.window, text="\u21A1", command=lambda: self.incY(-1 * self.rate))
        self.btn_s['font'] = font.Font(size=18)
        self.btn_s.grid(row=2, column=2, sticky="nsew")

        self.btn_d = tk.Button(master=self.window, text="\u21A0", command=lambda: self.incX(self.rate))
        self.btn_d['font'] = font.Font(size=18)
        self.btn_d.grid(row=2, column=3, sticky="nsew")

        # serial connect button
        self.connect_btn = tk.Button(master=self.window, text='connect',
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
        self.file_run = tk.Button(master=self.window, text='Run', command=lambda: self.runFile(self.file_entry.get()))
        self.file_run.grid(row=5, column=3)

        #self.initSerial(self.port, self.baud, self.startupfile)
        self.Refresh()


    def setKeybinds(self):
        self.window.bind('<KeyPress>', self.onKeyPress)
        # window.bind('<Return>', sendCommand(gcode_entry.get() + '\n', resetarg=True, entry=gcode_entry))

    def Refresh(self):
        self.lbl_pos.configure(text='X: %1.3f, Y:%1.3f' % (float(self.pos[0]), float(self.pos[1])))
        # print(time.perf_counter_ns(), pos)
        self.window.after(50, self.Refresh)

    def onKeyPress(self, event, wasd=False):
        if wasd:
            if event.char.lower() == 'w':
                self.incY(self.rate)
            elif event.char.lower() == 'a':
                self.incX(-1 * self.rate)
            elif event.char.lower() == 's':
                self.incY(-1 * self.rate)
            elif event.char.lower() == 'd':
                self.incX(self.rate)

    def incX(self, v):
        # increments the X counter by specified v, set by the rate
        # self.pos[0] += v
        c = 'G91 x' + str(v) + '\n'
        self.sendCommand(c)

    def incY(self, v):
        # increments the Y counter by specified v, set by the rate
        # self.pos[1] += v
        # increments the X counter by specified v, set by the rate
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

    def runFile(self, filename):
        # queue with timing calculation for next move
        try:
            with open(filename, 'r') as f:
                for line in f:
                    if line != '':
                        l = line.strip()
                        self.sendCommand(l + '\n')

        except FileNotFoundError:
            self.file_entry.delete(0, 'end')
            self.file_entry.insert(0, 'File does not exist')


class BoundedQueue:
    # Creates a new empty queue:
    def __init__(self, capacity):
        assert isinstance(capacity, int), (
                    'Error: Type error: %s' % (type(capacity)))  # throws an assertion error on not true
        assert capacity >= 0, ('Error: Illegal capacity: %d' % (capacity))
        self.__items = []  # init the  list / queue as empty
        self.__capacity = capacity

    # Adds a new item to the back of the queue, and returns nothing:
    def enqueue(self, item):
        '''
        Enqueue the element to the back of the queue
        :param item: the element to be enqueued
        :return: No returns
        '''
        if len(self.__items) >= self.__capacity:
            raise Exception('Error: Queue is full')
        else:
            self.__items.append(item)

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

    # Returns True if the queue is full, and False otherwise:
    def is_full(self):
        return len(self.__items) == self.__capacity

    # Returns the number of items in the queue:
    def size(self):
        return len(self.__items)

    # Returns the capacity of the queue:
    def capacity(self):
        return self.__capacity

    # Removes all items from the queue, and sets the size to 0
    # clear() should not change the capacity
    def clear(self):
        self.__items = []

    # Returns a string representation of the queue:
    def __str__(self):
        str_exp = ""
        for item in self.__items:
            str_exp += (str(item) + ", ")
        return str_exp

    # Returns a string representation of the object bounded queue:
    def __repr__(self):
        return str(self) + " Max=" + str(self.__capacity)