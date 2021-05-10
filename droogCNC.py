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
        self.pos = [0, 0]
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
                                    command=lambda: self.sendCommand(self.gcode_entry.get() + '\n', resetarg=True,
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
        #self.getPos()

    def setKeybinds(self):
        self.window.bind('<KeyPress>', self.onKeyPress)
        # window.bind('<Return>', sendCommand(gcode_entry.get() + '\n', resetarg=True, entry=gcode_entry))

    def Refresh(self):
        self.lbl_pos.configure(text='X: %1.3f, Y:%1.3f' % (self.pos[0], self.pos[1]))
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
        self.pos[0] += v
        c = 'G91x' + str(v) + '\n'
        self.sendCommand(c)

    def incY(self, v):
        # increments the Y counter by specified v, set by the rate
        self.pos[1] += v
        # increments the X counter by specified v, set by the rate
        c = 'G91y' + str(v) + '\n'
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
        if resetarg and entry is not None:
            entry.delete(0, 'end')
        print('Sent: ' + gcode.strip())

        self.s.write(gcode.encode('UTF-8'))
        self.readOut()

    def initSerial(self, port, baud, filename):
        try:
            self.s = serial.Serial(port, baud)
        except:
            print('Bungled connection, try again.')
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
                    self.sendCommand(l + '\n')
            print('Connected to GRBL')

    def getPos(self):
        self.s.write('$?'.encode('UTF-8'))
        response = self.s.readline().decode('UTF-8')
        print('pos:' + str(response))
        self.window.after(2000, self.getPos)

    def runFile(self, filename):
        try:
            with open(filename, 'r') as f:
                for line in f:
                    l = line.strip()
                    self.sendCommand(l + '\n')
        except FileNotFoundError:
            print('File does not exist, try again')
