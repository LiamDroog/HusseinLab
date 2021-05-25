import h5py
import HDF5Methods as h5m
import os
import tkinter as tk
import time


class FileBrowser:

    # todo:
    #   Get file -done
    #   Create file -done (assertions?)
    #   rm File - opting for not right now
    #   create / edit metadata - done ( edge cases?)
    #   Create datasets
    #   Rename groups/sets?
    #   cd methods - done
    #   add visual cues for all
    #   export to csv or xlsx
    def __init__(self):
        self.window = tk.Tk(className='\HDF5 File Viewer')
        self.screenwidth = str(int(self.window.winfo_screenwidth() * 0.35))
        self.screenheight = str(int(self.window.winfo_screenheight() * 0.35))
        self.window.geometry(self.screenwidth + 'x' + self.screenheight)
        self.grid = [16, 9]
        self.rowarr = list(i for i in range(self.grid[1]))
        self.colarr = list(i for i in range(self.grid[0]))
        self.window.rowconfigure(self.rowarr, minsize=25, weight=1)
        self.window.columnconfigure(self.colarr, minsize=25, weight=1)
        self.currentfile = None
        self.currentpath = '/'
        self.currentgroup = None
        self.currentdataset = None
        self.wraplength = 60
        self.outpadlen = 6
        self.anchorPos = [0, 5]

        self.errmessage = 'Command not found. Try $help'

        self.entrybar = tk.Entry(master=self.window)
        self.entrybar.configure(width=40)
        self.entrybar.grid(row=self.grid[1], column=0, columnspan=4, sticky='wn')

        self.sendentrybtn = tk.Button(master=self.window, text='Send',
                                      command=lambda: self.__parseCommand(self.entrybar.get()))
        self.sendentrybtn.grid(row=self.grid[1], column=4, sticky='ew')

        self.output = tk.Listbox(master=self.window)
        self.output.grid(columnspan=5, rowspan=self.grid[1], row=0, column=0, sticky='nesw')
        self.output.configure(bg='white')
        self.window.bind('<Return>', (lambda x: self.__parseCommand(self.entrybar.get())))

        self.scrollbar = tk.Scrollbar(master=self.window)
        self.scrollbar.grid(column=5, row=0, rowspan=self.grid[1], sticky='nsw')
        self.output.config(yscrollcommand=self.scrollbar.set)

        self.cwd_label = tk.Label(master=self.window,
                                  text='Working Directory: ~/> /' + '/'.join(i for i in os.getcwd().split('\\')[-3:]))
        self.cwd_label.grid(row=self.anchorPos[0], column=self.anchorPos[1] + 1, columnspan=10, sticky='w')

        self.currentfile_label = tk.Label(master=self.window, text='Current file: ')
        self.currentfile_label.grid(row=self.anchorPos[0] + 1, column=self.anchorPos[1] + 1, columnspan=10, sticky='w')

        self.currentfile_tree = tk.Listbox(master=self.window, bg='#F0F0F0')
        self.currentfile_tree.grid(row=self.anchorPos[0]+2, column=self.anchorPos[1]+1,
                                   columnspan=6, rowspan=6, sticky='nsew')

        inputstr = ['       __  __    ______ _           __    ____    ______  _             __',
                 '      / / / /   / ____/  | |       / /   /  _/   / ____/  | |           / /',
                 '    / /_/  /  /___ \     | |     / /    / /    / __/        | |   /|    / / ',
                 '  / __  /   ____/ /      | |  / /   _/ /    / /___         | |  / |  / /  ',
                 '/_/ /_/  /_____/       |___/   /___/  /_____/        |__/|__/   ']
        for i in inputstr:
            self.__sendOutput(i, head=' '*8)
        self.__sendOutput(time.asctime(), head='>> ')
        self.__sendOutput('Written by Liam Droog', head='>> ')
        self.__sendOutput("HDF5 Methods Initialized", head='>> ')

    def start(self):
        self.window.mainloop()

    def __parseCommand(self, command):
        # parses commands from input box (typed). resets input box to nil
        self.__sendCommand(command)
        try:
            parsedcommand = command.lower().split('$')
            i = parsedcommand[1]
        except:
            self.__errmessage()
            return
        else:
            if i.strip() != '':
                i = i.lower().strip().split(' ')
                if i[0] == 'cls':
                    self.__cls()
                elif i[0] == 'ls':
                    self.__ls()
                elif i[0] == 'cd':
                    self.__cd(i[1])
                elif i[0] == 'getfile':
                    self.__getFile(i[1])
                elif i[0] == 'createfile':
                    self.__createFile(i[1])
                elif i[0] == 'setmetadata':
                    self.__setMetadata(' '.join(j for j in i[1:]))
                elif i[0] == 'getmetadata':
                    if len(i) == 1:
                        if self.currentfile is None:
                            self.__sendOutput('No file selected')
                            return
                        self.__getMetadata(self.currentfile)
                    else:
                        self.currentfile = i[1]
                        self.__getMetadata(i[1])
                elif i[0] == 'tree':
                    if len(i) == 1:
                        if self.currentfile is None:
                            self.__sendOutput('No file selected')
                            return
                        self.__tree(self.currentfile)
                    else:
                        self.__tree(i[1])
                else:
                    self.__errmessage()
                    return
        self.entrybar.delete(0, 'end')

    def __sendCommand(self, command):
        # executes command based off input command
        self.output.insert('end', '\n' + '~> ' + command.rstrip()[0:self.wraplength])
        for i in range(self.wraplength, len(command.rstrip()), self.wraplength):
            self.output.insert('end', '\n' + '      ' + command.rstrip()[i:i + self.wraplength])
        self.output.yview(tk.END)

    def __sendOutput(self, command, head='!>'):
        self.output.insert('end', '\n' + head + command.rstrip())
        self.output.yview(tk.END)

    def __cls(self):
        self.output.delete(0, tk.END)

    def __ls(self):
        self.__sendOutput(os.getcwd(), head='CWD: ')
        for i in os.listdir():
            self.__sendOutput(i, head=' ' * 9 + '\u21B3')

    def __cd(self, dir):
        if not os.path.isdir(dir):
            self.__sendOutput('Directory does not exist. Yet. ', head=' ' * self.outpadlen)
        else:
            os.chdir(dir)
            self.cwd_label.config(text='Working Directory: ~/> /' + '/'.join(i for i in os.getcwd().split('\\')[-3:]))
            self.currentfile = None
            self.currentfile_label.config(text='Current File: ')

    def __errmessage(self):
        self.__sendOutput(self.errmessage)

    def __getFile(self, filename):
        if os.path.exists(filename):
            self.currentfile = filename
            self.currentfile_label.config(text='Current File: ' + filename)
            self.__sendOutput('Got ' + filename, head=' ' * self.outpadlen)
        else:
            self.__sendOutput('File does not exist. What does it mean to exist, anyway?')

    def __createFile(self, filename):
        if filename[-5:].lower() != '.hdf5':
            self.__sendOutput('Invalid file format, must have extension .hdf5', head=' ' * self.outpadlen)
            return
        if h5m.createFile(filename):
            self.__sendOutput('File successfully created', head=' ' * self.outpadlen)
            self.__getFile(filename)
            return
        else:
            self.__sendOutput('Unable to create file. Horsefeathers.', head=' ' * self.outpadlen)
            return

    def __createGroup(self):
        pass

    def __getMetadata(self, filename):
        if self.currentfile:
            self.__sendOutput('/' + filename, head='')
            self.__sendOutput('File Metadata:')
            for key, val in h5m.getMetadata(filename):
                self.__sendOutput(' ' * 5 + "%s: %s" % (key, val), head='')
        else:
            self.__sendOutput('Metadata failed to appear. Fiddlesticks.')

    def __setMetadata(self, iput, path='/'):
        cmd = iput.split(',')
        print(cmd)
        if len(cmd) < 2:
            self.__sendOutput('Too few arguments, '
                              '$setmetadata must have an attribute and a corresponding value separated by commas')
        else:
            h5m.setMetadata(self.currentfile, cmd[0], cmd[1], path=path)

    def __tree(self, filename):
        if os.path.exists(filename):
            with h5py.File(filename, mode='a') as h5f:
                self.__getMetadata(filename)
                h5f.visititems(self.__print_attrs)
        else:
            self.__sendOutput('File does not exist')

    def __outputTree(self, filename):
        if os.path.exists(filename):
            with h5py.File(filename, mode='a') as h5f:
                self.__getMetadata(filename)
                h5f.visititems(self.__print_attrs)
        else:
            self.__sendOutput('File does not exist')

    def __rmFile(self):
        pass

    def __print_attrs(self, name, obj):
        try:
            self.__sendOutput('/' + name, head='')
            n = 5
            self.__sendOutput('Shape: ' + str(obj.shape), head=' ')
            self.__sendOutput('Type: ' + str(obj.dtype), head=' ')
            self.__sendOutput('Compression: ' + str(obj.compression), head=' ')
            self.__sendOutput(' ' * n + 'Metadata:', head='')
            for key, val in obj.attrs.items():
                self.__sendOutput(' ' * n + "%s: %s" % (key, val), head='')
            self.__sendOutput(' ', head='')
        except Exception as e:
            print(e)
