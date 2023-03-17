import tkinter as tk
from tkVideoPlayer import TkinterVideo
import cv2

class VideoPlayer:
    def __init__(self, frame: tk.Frame, path, scale = 1):
        vid = cv2.VideoCapture(path)
        height = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
        width = vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        vid_frame = tk.Frame(frame, height=int(height * scale), width=int(width * scale))
        self.vid_player = TkinterVideo(vid_frame, keep_aspect=True)
        self.vid_player.place(relx=0, rely=0, relwidth=1, relheight=1)
        vid_frame.pack()

        self.vid_player.bind("<<Ended>>", self.play)

        self.load_video(path)
        self.play()

    def load_video(self, file_path):
        if file_path:
            self.vid_player.load(file_path)

    def play(self, event = None):
        self.vid_player.play()