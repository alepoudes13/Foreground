from win32gui import GetWindowText, GetForegroundWindow, GetWindowRect, FindWindow
import asyncio
import threading
from sys import exit
loop = asyncio.get_event_loop()


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
                if oldRect == None or oldRect[0] != window.rect[0] or oldRect[1] != window.rect[1]:
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
    def relocate(self, event = None):
        w = self.relx_slider.get() / 100
        h = self.rely_slider.get() / 100
        x = self.rect[0] + (self.rect[2] - self.rect[0]) * (w if self.anchors[0] == 0 else 1 - w) - self.topFrame.winfo_width() * self.anchors[0]
        y = self.rect[1] + (self.rect[3] - self.rect[1]) * (h if self.anchors[1] == 0 else 1 - h) - self.topFrame.winfo_height() * self.anchors[1]
        self.topFrame.geometry("+%d+%d" %(x, y))
    
    def NW(self):
        self.anchors = [0, 0]
        self.relocate()

    def NE(self):
        self.anchors = [1, 0]
        self.relocate()

    def SW(self):
        self.anchors = [0, 1]
        self.relocate()

    def SE(self):
        self.anchors = [1, 1]
        self.relocate()

    def __init__(self) -> None:
        self.isDiscordActive = False
        self.file = None
        self.rect = None
        self.topFrame = None
        self.hidden = False
        self.started = False
        self.anchors = [1, 1]
        self.window = Tk()
        self.window.title('-----')
        self.window.config(background = "white")
        self.button_explore = Button(self.window, text = "Browse Files", command = self.openFile)
        self.button_explore.grid(column = 1, row = 1)  
        self.button_start = Button(self.window, text = "Start", command = self.startPopupBase)
        self.button_start.grid(column = 2, row = 1)
        self.button_stop = Button(self.window, text = "Stop", command = self.closePopupBase)
        self.button_stop.grid(column = 3, row = 1)  
        self.button_exit = Button(self.window, text = "Exit program", command = exit)
        self.button_exit.grid(column = 4, row = 1) 

        self.relx_label = Label(self.window, text='RelX (%)', background = "white") 
        self.rely_label = Label(self.window, text='RelY (%)', background = "white")
        self.relx_label.grid(row = 2, column=1, columnspan=2) 
        self.rely_label.grid(row = 2, column=3, columnspan=2) 
        self.relx_slider = Scale(self.window, from_=0, to=100, orient=HORIZONTAL)
        self.relx_slider.grid(row=3, column=1, columnspan=2)
        self.rely_slider = Scale(self.window, from_=0, to=100, orient=HORIZONTAL)
        self.rely_slider.grid(row=3, column=3, columnspan=2)
        self.relx_slider.bind('<ButtonRelease>', self.relocate)
        self.rely_slider.bind('<ButtonRelease>', self.relocate)

        self.anchor_label = Label(self.window, text='Anchors', background = "white")
        self.anchor_label.grid(columnspan = 4, row = 4, column = 1)

        self.button_NW = Button(self.window, text = "NW", command = self.NW)
        self.button_NW.grid(column = 1, row = 5, sticky=E)  
        self.button_NE = Button(self.window, text = "NE", command = self.NE)
        self.button_NE.grid(column = 2, row = 5)
        self.button_SW = Button(self.window, text = "SW", command = self.SW)
        self.button_SW.grid(column = 3, row = 5)  
        self.button_SE = Button(self.window, text = "SE", command = self.SE)
        self.button_SE.grid(column = 4, row = 5, sticky=W) 

    def openFile(self):
        self.file = filedialog.askopenfilename(title='Select a file to display')

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
        self.topFrame.bind('<FocusIn>', self.onPopupFocus)

        try:
            if self.file.split('.')[-1] == 'gif':
                assert(0)
            thumb = Image.open(self.file)
            tk_thumb = ImageTk.PhotoImage(thumb)
            label = Label(self.topFrame, image=tk_thumb)
            label.image = tk_thumb
            label.pack()
            self.relocate()
        except:
            try:
                video = VideoPlayer(self.topFrame, self.file)
            except Exception as e:
                print(e)
                pass

    def onPopupFocus(self, event):
        self.isDiscordActive = True
        return "break"

    def startPopupBase(self):
        self.started = True
        self.hidden = True

    def closePopup(self):
        if self.topFrame != None:
            self.topFrame.destroy()
            self.topFrame = None

    def closePopupBase(self):
        self.started = False
        self.closePopup()

    def changeTag(self):
        self.topFrame = Toplevel(self.window)
        self.topFrame.geometry("+%d+%d" %(self.window.winfo_x()+self.listFrame.winfo_width(),self.window.winfo_y()+self.button_explore.winfo_height() * 2))

if __name__ == '__main__':
    window = Window()
    x = threading.Thread(target=CheckActiveWindow, daemon=True)
    x.start()
    window.window.mainloop()