import tkinter as tk
import tkinter.font as font
import serial
import time


def main():

    def init_grbl():
        pass
    def incX(v):
        # increments the X counter by specified v, set by the rate
        pos[0] += v
        c = 'G91x' + str(v) + '\n'
        sendCommand(c)

    def incY(v):
        # increments the Y counter by specified v, set by the rate
        pos[1] += v
        # increments the X counter by specified v, set by the rate
        c = 'G91y' + str(v) + '\n'
        sendCommand(c)

    def switchRate(v):
        # used to switch the rate's order of magnitude corresponding to pressed button
        rate[0] = v

    def readOut():
        out = s.readline()  # Wait for grbl response with carriage return
        print('> ' + out.strip().decode('UTF-8'))

    def sendCommand(gcode, resetarg=False, entry=None):
        if resetarg and entry is not None:
            entry.delete(0, 'end')
        print('Sent: ' + gcode.strip())
        s.write(gcode.encode('UTF-8'))
        readOut()

    def Draw():
        # draws all on-screen controls, and assigns their event commands
        global lbl_pos, lbl_frame

        rowarr = list(i for i in range(rowLen))
        colarr = list(i for i in range(colLen))
        window.rowconfigure(rowarr, minsize=50, weight=1)
        window.columnconfigure(colarr, minsize=50, weight=1)

        # On screen control grid
        btn_w = tk.Button(master=window, text="\u219F", command=lambda: incY(rate[0]))
        btn_w['font'] = font.Font(size=18)
        btn_w.grid(row=1, column=2, sticky="nsew")

        btn_a = tk.Button(master=window, text="\u219E", command=lambda: incX(-1 * rate[0]))
        btn_a['font'] = font.Font(size=18)
        btn_a.grid(row=2, column=1, sticky="nsew")

        btn_s = tk.Button(master=window, text="\u21A1", command=lambda: incY(-1 * rate[0]))
        btn_s['font'] = font.Font(size=18)
        btn_s.grid(row=2, column=2, sticky="nsew")

        btn_d = tk.Button(master=window, text="\u21A0", command=lambda: incX(rate[0]))
        btn_d['font'] = font.Font(size=18)
        btn_d.grid(row=2, column=3, sticky="nsew")

        # jog button
        btn_jog = tk.Button(master=window, text='10', command=lambda: switchRate(10))
        btn_jog.grid(row=3, column=0, sticky='nsew')

        # 1 button
        btn_1 = tk.Button(master=window, text='1', command=lambda: switchRate(1))
        btn_1.grid(row=3, column=1, sticky='nsew')

        # 0.1 button
        btn_01 = tk.Button(master=window, text='0.1', command=lambda: switchRate(0.1))
        btn_01.grid(row=3, column=2, sticky='nsew')

        # 0.01 button
        btn_001 = tk.Button(master=window, text='0.01', command=lambda: switchRate(0.01))
        btn_001.grid(row=3, column=3, sticky='nsew')

        btn_0001 = tk.Button(master=window, text='0.001', command=lambda: switchRate(0.001))
        btn_0001.grid(row=3, column=4, sticky='nsew')

        # DRO frame
        lbl_frame = tk.Frame(master=window, relief=tk.RAISED, borderwidth=3)
        lbl_pos = tk.Label(master=lbl_frame, text='X: %1.3f, Y:%1.3f' % (pos[0], pos[1]))
        lbl_pos['font'] = font.Font(size=15)

        lbl_frame.grid(row=0, column=0, columnspan=colLen, sticky='EW')
        lbl_pos.pack()

        # gcode input box
        global gcode_entry
        gcode_entry = tk.Entry(master=window)
        gcode_entry.grid(row=4, columnspan=3, sticky='ew')

        # gcode button
        gcode_send = tk.Button(master=window, text='Send',
                               command=lambda: sendCommand(gcode_entry.get()+'\n',
                                                           resetarg=True, entry=gcode_entry))
        gcode_send.grid(row=4, column=3, sticky='')

    def setKeybinds():
        window.bind('<KeyPress>', onKeyPress)
        #window.bind('<Return>', sendCommand(gcode_entry.get() + '\n', resetarg=True, entry=gcode_entry))

    def Refresh():
        lbl_pos.configure(text='X: %1.3f, Y:%1.3f' % (pos[0], pos[1]))
        #print(time.perf_counter_ns(), pos)
        window.after(50, Refresh)

    def onKeyPress(event, wasd=False):
        if wasd:
            if event.char.lower() == 'w':
                incY(rate[0])
            elif event.char.lower() == 'a':
                incX(-1*rate[0])
            elif event.char.lower() == 's':
                incY(-1*rate[0])
            elif event.char.lower() == 'd':
                incX(rate[0])


    ####### Begin main script

    # defines inital conditions for rate and position
    # Possible to pull from file to 'remember' or have to manually calibrate each time
    pos = [0., 0.]

    rate = [1]

    rowLen = 5
    colLen = 5

    # Open grbl serial port
    s = serial.Serial('COM4', 115200)

    # Wake up grbl
    s.write(b"\r\n\r\n")
    time.sleep(2)  # Wait for grbl to initialize
    s.flushInput()  # Flush startup text in serial input
    s.write('g21g90\n'.encode('UTF-8'))
    readOut()
    s.write('g92x0y0\n'.encode('UTF-8'))
    readOut()

    # initialize parent window
    window = tk.Tk(className='\DRO Test')
    Draw()
    setKeybinds()
    Refresh()

    window.mainloop()



main()
