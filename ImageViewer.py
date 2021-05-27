import tkinter as tk
from tkinter import font
from PIL import Image, ImageTk


class ImageFrame:
    def __init__(self, text, image):
        self.window = tk.Toplevel()
        self.window.title('Spectra View-o-matic 9000')
        self.screenwidth = str(int(self.window.winfo_screenwidth() * 0.3))
        self.screenheight = str(int(self.window.winfo_screenheight() * 0.3))
        self.window.geometry(self.screenwidth + 'x' + self.screenheight)
        self.grid = [16, 9]
        self.rowarr = list(i for i in range(self.grid[1]))
        self.colarr = list(i for i in range(self.grid[0]))
        self.window.rowconfigure(self.rowarr, minsize=25, weight=1)
        self.window.columnconfigure(self.colarr, minsize=25, weight=1)
        self.imageList = []
        self.currentimage = None

        self.factor = 0.8
        self.canvas = tk.Canvas(self.window, height=300, width=400)
        self.canvas.grid(row=1, column=6, rowspan=8, columnspan=16, sticky='nswe')
        im = Image.open(image)
        self.canvas.image = ImageTk.PhotoImage(
            im.resize((int(self.factor * im.size[0]), int(self.factor * im.size[1]))))
        im = self.canvas.create_image(0, 0, image=self.canvas.image, anchor='nw')
        self.imageList.append(image)
        self.image_on_canvas = im

        self.attributes_frame = tk.Frame(master=self.window, relief='raised', borderwidth=3)
        self.attributes_frame.grid(row=1, column=0, columnspan=6, rowspan=7, sticky='nsew')
        self.atext = tk.Label(master=self.attributes_frame, text='yeet')
        self.atext.pack()

        self.nextbutton = tk.Button(master=self.window, text='>>', command=lambda: self.__changeimg('fwd'))
        self.nextbutton.grid(row=8, column=4, columnspan=2, sticky='nsew')

        self.prevbutton = tk.Button(master=self.window, text='<<', command=lambda: self.__changeimg('bck'))
        self.prevbutton.grid(row=8, column=0, columnspan=2, sticky='nsew')


        #self.window.mainloop()

    def changepos(self):
        pass

    def getsize(self):
        return len(self.imageList)

    def addImage(self, image):
        self.imageList.append(image)
        self.currentimage = image
        self.__showImage(image)

    def __showImage(self, image):
        img = Image.open(image)
        img2 = ImageTk.PhotoImage(img.resize((int(self.factor * img.size[0]), int(self.factor * img.size[1]))))
        im = self.canvas.create_image(0, 0, image=img2, anchor='nw')
        self.canvas.itemconfig(self.image_on_canvas, image=im)
        #  self.canvas.create_image(0, 0, image=im)

    def __changeimg(self, dir):
        print(self.imageList)
        idx = self.imageList.index(self.currentimage)
        print(idx)
        if dir == 'fwd':
            if idx < len(self.imageList):
                self.__showImage(self.imageList[idx+1])

        elif dir == 'bck':
            if idx > 0:
                self.__showImage(self.imageList[idx-1])
