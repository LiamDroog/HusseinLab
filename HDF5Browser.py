import h5py
import HDF5Methods as h5m
import tkinter as tk


class FileBrowser:

    def __init__(self):
        self.window = tk.Tk(className='\HTF5 File Viewer')
        self.screenwidth = str(int(self.window.winfo_screenwidth() * 0.35))
        self.screenheight = str(int(self.window.winfo_screenheight() * 0.35))
        self.window.geometry(self.screenwidth + 'x' + self.screenheight)
        self.grid = [16, 9]
        self.rowarr = list(i for i in range(self.grid[1]))
        self.colarr = list(i for i in range(self.grid[0]))
        self.window.rowconfigure(self.rowarr, minsize=50, weight=1)
        self.window.columnconfigure(self.colarr, minsize=50, weight=1)
        self.cuurentfile = None
        self.currentpath = None
        self.currentgroup = None
        self.currentdataset = None

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
        self.output.config(yscrollcommand= self.scrollbar.set)



    def start(self):
        self.window.mainloop()

    def __parseCommand(self, command):
        # parses commands from input box (typed). resets input box to nil
        self.entrybar.delete(0, 'end')
        self.__sendCommand(command)
        try:
            i = command.split('$')[1].lower()
        except:
            self.__errmessage()
        else:
            if i.strip() != '':
                if i == 'cls':
                    self.__cls()
                if i == 'hellothere':
                    self.__sendOutput('General Kenobi')
                if i == 'tree' and i[2] is not None:
                    self.__tree('testshot001.hdf5')
                else:
                    self.__errmessage()

    def __sendCommand(self, command):
        # executes command based off input command
        self.output.insert('end', '\n' + '~> ' + command.rstrip())
        self.output.yview(tk.END)

    def __sendOutput(self, command, head='!>'):
        self.output.insert('end', '\n' + head + command.rstrip())
        self.output.yview(tk.END)

    def __cls(self):
        self.output.delete(0, tk.END)

    def __errmessage(self):
        self.__sendOutput(self.errmessage)

    def __createFile(self):
        pass

    def __createGroup(self):
        pass

    def __getMetadata(self):
        pass

    def __setMetadata(self):
        pass

    def __tree(self, filename):
        with h5py.File(filename, mode='a') as h5f:
            h5f.visititems(self.__print_attrs)

    def __rmFile(self):
        pass

    def __print_attrs(self, name, obj):
        try:
            self.__sendOutput('/' + name, head='')
            n = 5
            self.__sendOutput(' ' * n + 'Metadata:', head='')

            for key, val in obj.attrs.items():
                self.__sendOutput(' ' * n + "%s: %s" % (key, val), head='')
            self.__sendOutput(' ', head='')

        except Exception as e:
            print(e)