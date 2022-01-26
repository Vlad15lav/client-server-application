import re
import time
import socket
import threading

from tkinter import *
from base.server import Server

# Tkinter interface
class MainForm(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.frame = Frame(self, bg='#fafafa')
        self.parent = parent
        self.parent.resizable(width=False, height=False)

        self.window_w = 550
        self.window_h = 570

        self.centerWindow()
        self.initUI()
        self.showUI()

        self.isRunning = False
        self.server = Server(self.text_console)

    def initUI(self):
        self.parent.title('Chat Server')
        self.parent['bg'] = '#fafafa'
        self.frame = Frame(self.parent, bg='#fafafa')

        # label for status info
        self.label_status = Label(self.frame, text='Status: disabled', fg='#FF0000', bg='#fafafa', font=20)

        # button for start/stop
        self.btn = Button(self.frame, text='Start', bg='gray', command=self.__button_status)

        # output info - console
        self.lable_console = Label(self.frame, text='Console', bg='#fafafa', font=20)
        self.text_console = Text(self.frame, state='disabled')

        # entry commands
        self.entry = Entry(self.frame)
        self.entry.bind('<Return>', self.__send_button)
        self.button = Button(self.frame, text='Send', bg='gray', command=self.__send_button)

    def showUI(self):
        self.frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        # label for status info
        self.label_status.place(x=10, y=17)

        # button for start/stop
        self.btn.place(x=400, y=20, width=130, height=50)

        # output info - console
        self.lable_console.place(x=10, y=50)
        self.text_console.place(x=10, y=80, width=530, height=455)

        # entry for commands
        self.entry.place(x=10, y=540, width=435, height=22)
        self.button.place(x=450, y=540, width=80, height=22)

    def __button_status(self):
        if self.isRunning:
            self.label_status.config(text='Status: disabled', fg='#FF0000')
            self.btn.config(text='Start')
            self.isRunning = not self.isRunning
            self.server.stop()
        else:
            self.label_status.config(text='Status: active', fg='#00FF00')
            self.btn.config(text='Stop')
            self.isRunning = not self.isRunning
            self.server.start()

    def __send_button(self, event=None):
        pass
        #self.entry.delete(0, END)

    # Centring window
    def centerWindow(self):
        sw = self.parent.winfo_screenwidth()
        sh = self.parent.winfo_screenheight()

        x = (sw - self.window_w) / 2
        y = (sh - self.window_h) / 2
        self.parent.geometry('%dx%d+%d+%d' % (self.window_w, self.window_h, x, y))