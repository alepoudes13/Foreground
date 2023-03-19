from win32gui import GetWindowText, GetForegroundWindow, GetWindowRect, FindWindow
import asyncio
import threading
from sys import exit
loop = asyncio.get_event_loop()

from configparser import ConfigParser
config = ConfigParser()
config.read('config.ini')

from tkinter import *
from tkinter import filedialog
from video import VideoPlayer
from PIL import Image, ImageTk

def CheckActiveWindow():
    oldRect = None
    while True:
        currentWindow = GetWindowText(GetForegroundWindow())
        handle = FindWindow(0, currentWindow)
        try:
            window.isDiscordActive = True if currentWindow.split()[-1] == 'Discord' else False
        except:
            window.isDiscordActive = False
        if currentWindow == '' or currentWindow == None or currentWindow == '-----':
            continue
        if window.isDiscordActive:
            if window.started and not window.hidden:
                oldRect = window.rect
                try:
                    rect = GetWindowRect(handle)
                    window.isDiscordActive = True if currentWindow.split()[-1] == 'Discord' else False
                    if window.isDiscordActive:
                        window.rect = rect
                except:
                    continue
                if (oldRect == None or oldRect[0] != window.rect[0] or oldRect[1] != window.rect[1]):
                    if window.topFrame == None:
                        window.startPopup()
                    window.relocate()
            if window.started and window.hidden:
                oldRect = window.rect
                window.rect = GetWindowRect(handle)
                window.startPopup()
                window.relocate()
                window.hidden = False
        elif window.started and not window.hidden:
            window.closePopup()
            window.hidden = True

class Window:
    #INIT=======================================

    def ex(self):
        self.write()
        exit()

    def openFile(self):
        self.file = filedialog.askopenfilename(title='Select a file to display')

    def __init__(self) -> None:
        self.isDiscordActive = False
        self.rect = None
        self.topFrame = None
        self.hidden = False
        self.started = True
        self.scaleMultiplier = 1
        self.relx, self.rely = 0, 0
        self.anchors = [1, 1]
        
        self.window = Tk()
        self.window.title('-----')
        self.window.config(background = "white")
        self.window.protocol("WM_DELETE_WINDOW", self.ex)
        self.button_explore = Button(self.window, text = "Browse Files", command = self.openFile)
        self.button_explore.grid(column = 1, row = 1)  
        self.button_start = Button(self.window, text = "Start", command = self.startPopupBase)
        self.button_start.grid(column = 2, row = 1)
        self.button_stop = Button(self.window, text = "Stop", command = self.closePopupBase)
        self.button_stop.grid(column = 3, row = 1)  
        self.button_exit = Button(self.window, text = "Exit program", command = self.ex)
        self.button_exit.grid(column = 4, row = 1)

        self.anchor_label = Label(self.window, text='Anchors', background = "white")
        self.anchor_label.grid(columnspan = 4, row = 2, column = 1)

        self.anchor_buttons = [None, None, None, None]
        self.anchor_buttons[0] = Button(self.window, text = "NW", command = self.NW)
        self.anchor_buttons[0].grid(column = 1, row = 3, sticky=E)  
        self.anchor_buttons[1] = Button(self.window, text = "NE", command = self.NE)
        self.anchor_buttons[1].grid(column = 2, row = 3)
        self.anchor_buttons[2] = Button(self.window, text = "SW", command = self.SW)
        self.anchor_buttons[2].grid(column = 3, row = 3)  
        self.anchor_buttons[3] = Button(self.window, text = "SE", command = self.SE)
        self.anchor_buttons[3].grid(column = 4, row = 3, sticky=W) 

        self.scale_label = Label(self.window, text='Scale (%)', background = "white")
        self.scale_label.grid(row = 4, column=1, columnspan=4) 
        self.scale_slider = Scale(self.window, from_=100, to=0, orient=HORIZONTAL)
        self.scale_slider.grid(row=5, column=1, columnspan=4) 
        self.scale_slider.bind('<ButtonRelease>', self.resize)

        try:
            self.read()
            self.started = True
            self.scale_slider.set(int(self.scaleMultiplier * 100))
            self.buttonState(self.anchors[0] + self.anchors[1] * 2)
        except:
            self.file = None
            self.anchors = [1, 1]
            self.relx, self.rely = 0, 0
            self.scale_slider.set(100)
            self.buttonState(3)

    #CONFIG=======================================

    def write(self):
        try:
            config.add_section('main')
        except:
            pass
        config.set('main', 'file', self.file)
        config.set('main', 'anchorX', str(self.anchors[0]))
        config.set('main', 'anchorY', str(self.anchors[1]))
        config.set('main', 'relX', str(self.relx))
        config.set('main', 'relY', str(self.rely))
        config.set('main', 'scale', str(self.scaleMultiplier))

        with open('config.ini', 'w') as f:
            config.write(f)

    def read(self):
        file = config.get('main', 'file')
        self.file = file
        self.anchors = [config.getint('main', 'anchorX'), config.getint('main', 'anchorY')]
        self.relx = config.getfloat('main', 'relX')
        self.rely = config.getfloat('main', 'relY')
        self.scaleMultiplier = config.getfloat('main', 'scale')

    #TOP LEVEL CHANGES=======================================

    def relocate(self, event = None):
        w = self.relx
        h = self.rely
        x = self.rect[0] + (self.rect[2] - self.rect[0]) * (w if self.anchors[0] == 0 else 1 - w) - self.topFrame.winfo_width() * self.anchors[0]
        y = self.rect[1] + (self.rect[3] - self.rect[1]) * (h if self.anchors[1] == 0 else 1 - h) - self.topFrame.winfo_height() * self.anchors[1]
        self.topFrame.geometry("+%d+%d" %(x, y))

    def resize(self, event = None):
        self.scaleMultiplier = self.scale_slider.get() / 100
        try:
            if self.file.split('.')[-1] == 'gif':
                assert(0)
            thumb = Image.open(self.file).convert("RGBA")
            w, h = int(thumb.width * self.scaleMultiplier), int(thumb.height * self.scaleMultiplier)
            thumb = thumb.resize((int(w), int(h)))
            tk_thumb = ImageTk.PhotoImage(thumb)
            for widget in self.topFrame.winfo_children():
                widget.destroy()
            self.label = Label(self.topFrame, image=tk_thumb)
            self.label.image = tk_thumb
            self.label.pack()       
        except:
            try:
                for widget in self.topFrame.winfo_children():
                    widget.destroy()
                video = VideoPlayer(self.topFrame, self.file, self.scaleMultiplier)
            except:
                pass
        self.topFrame.update_idletasks()
        self.relocate()

    def NW(self):
        self.anchors = [0, 0]
        self.relocate()
        self.buttonState(0)

    def NE(self):
        self.anchors = [1, 0]
        self.relocate()
        self.buttonState(1)

    def SW(self):
        self.anchors = [0, 1]
        self.relocate()
        self.buttonState(2)

    def SE(self):
        self.anchors = [1, 1]
        self.relocate()
        self.buttonState(3)

    def buttonState(self, active: int):
        for i in range(4):
            if i == active:
                self.anchor_buttons[i]['state'] = DISABLED
            else:
                self.anchor_buttons[i]['state'] = NORMAL

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        self.x = None
        self.y = None

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.topFrame.winfo_x() + deltax
        y = self.topFrame.winfo_y() + deltay
        if self.anchors[0] == 0:
            self.relx = (x - self.rect[0]) / (self.rect[2] - self.rect[0])
        else:
            self.relx = (self.rect[2] - x - self.topFrame.winfo_width()) / (self.rect[2] - self.rect[0])
        if self.anchors[1] == 0:
            self.rely = (y - self.rect[1]) / (self.rect[3] - self.rect[1])
        else:
            self.rely = (self.rect[3] - y - self.topFrame.winfo_height()) / (self.rect[3] - self.rect[1])
        self.topFrame.geometry(f"+{x}+{y}")

    #TOP LEVEL=======================================

    def startPopup(self):
        if self.topFrame != None:
            self.closePopup()
        self.started = True
        self.hidden = True
        self.topFrame = Toplevel(self.window)
        self.topFrame.title('-----')        
        self.topFrame.attributes('-transparentcolor','#f0f0f0')
        self.topFrame.attributes('-topmost', True)
        self.topFrame.overrideredirect(True)
        self.topFrame.update()
        self.topFrame.bind('<ButtonPress-1>', self.start_move)
        self.topFrame.bind('<B1-Motion>', self.do_move)
        self.topFrame.bind('<ButtonRelease-1>', self.stop_move)

        self.resize()

    def closePopup(self):
        if self.topFrame != None:
            self.topFrame.destroy()
            self.topFrame = None

    def startPopupBase(self):
        self.started = True
        self.hidden = True

    def closePopupBase(self):
        self.started = False
        self.closePopup()

if __name__ == '__main__':
    window = Window()
    x = threading.Thread(target=CheckActiveWindow, daemon=True)
    x.start()
    window.window.mainloop()