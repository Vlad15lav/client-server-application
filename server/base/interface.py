import re
import time
import socket
import threading

from tkinter import *
from tkinter import filedialog as fd
from tkinter import messagebox as mb
from base.server import Server

from hashlib import md5
from config.config import settings

# server interface
class MainForm(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.frame = Frame(self, bg='#fafafa')
        self.parent = parent
        self.parent.resizable(width=False, height=False)

        # windows size
        self.window_w = 550
        self.window_h = 570

        self.centerWindow()
        self.initUI()
        self.showUI()

        self.is_running = False
        self.server = Server(self.text_console)

        self.sign_on_login = StringVar()
        self.sign_on_password = StringVar()

    def initUI(self):
        self.parent.title('Chat Server')
        self.parent['bg'] = '#fafafa'
        self.frame = Frame(self.parent, bg='#fafafa')

        # label for status info
        self.label_status = Label(self.frame, text='Status: disabled', fg='#FF0000', bg='#fafafa', font=20)

        # button for sign on
        self.btn_sign_on = Button(self.frame, text='Sign On', bg='gray', command=self.__button_sign_on)

        # button for start/stop
        self.btn = Button(self.frame, text='Start', bg='gray', command=self.__button_status)

        # output info - console
        self.lable_console = Label(self.frame, text='Console', bg='#fafafa', font=20)
        self.text_console = Text(self.frame, state='disabled')

        # entry commands
        self.entry = Entry(self.frame)
        self.entry.bind('<Return>', self.__button_send_message)
        self.btn_send = Button(self.frame, text='Send', bg='gray', command=self.__button_send_message)
        self.btn_file = Button(self.frame, text='File', bg='gray', command=self.__button_send_file)

    def showUI(self):
        self.frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        # label for status info
        self.label_status.place(x=10, y=17)

        # button for start/stop
        self.btn.place(x=400, y=20, width=130, height=50)

        # button for sign on
        self.btn_sign_on.place(x=260, y=20, width=130, height=50)

        # output info - console
        self.lable_console.place(x=10, y=50)
        self.text_console.place(x=10, y=80, width=530, height=455)

        # entry for commands
        self.entry.place(x=10, y=540, width=435-80, height=22)
        self.btn_send.place(x=450-80, y=540, width=80, height=22)
        self.btn_file.place(x=450+10, y=540, width=80, height=22)

    # centring window
    def centerWindow(self):
        sw = self.parent.winfo_screenwidth()
        sh = self.parent.winfo_screenheight()

        x = (sw - self.window_w) / 2
        y = (sh - self.window_h) / 2
        self.parent.geometry('%dx%d+%d+%d' % (self.window_w, self.window_h, x, y))

    ### action methods
    # start/stop server event
    def __button_status(self):
        if self.is_running:
            self.label_status.config(text='Status: disabled', fg='#FF0000')
            self.btn.config(text='Start')
            self.server.stop()
        else:
            if not self.server.start():
                return
            self.label_status.config(text='Status: active', fg='#00FF00')
            self.btn.config(text='Stop')
        self.is_running = not self.is_running

    # sign on event
    def __button_sign_on(self, event=None):
        # create window
        self.root_reg = Toplevel()
        self.root_reg.title('Sign On')
        self.root_reg.resizable(width=False, height=False)
        self.root_reg.configure(width=300, height=130)

        # main field for auth
        self.reg_frame = Frame(self.root_reg, bg='#fafafa')
        self.reg_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        # field for login name
        self.label_login = Label(self.reg_frame, text='Login:', bg='#fafafa', font=20)
        self.entry_login = Entry(self.reg_frame, justify='center', textvariable=self.sign_on_login)
        # field passwor 
        self.label_password = Label(self.reg_frame, text='Password:', bg='#fafafa', font=20)
        self.entry_password = Entry(self.reg_frame, justify='center', textvariable=self.sign_on_password, show="*")

        # set label for login name 
        self.label_login.place(x=10, y=17)
        self.entry_login.place(x=90, y=20, width=150)
        # set label password 
        self.label_password.place(x=10, y=47)
        self.entry_password.place(x=90, y=50, width=150)
        # set button sign on
        self.btn_sign_on = Button(self.reg_frame, text="Sign On", font=20,
                         command=lambda: self.__button_add_user())
        self.btn_sign_on.place(x=100, y=85, width=110, height=25)

    # add user to the database
    def __button_add_user(self):
        login = self.sign_on_login.get()
        password = self.sign_on_password.get()
        # check empty fields
        if login == '' or password == '':
            mb.showerror("Error", "Empty fields!")
            return
        # check database connection
        if self.server.database is None:
            mb.showerror("Error", "Start server!")
            return

        qr = self.server.database.select('SELECT * FROM Users WHERE Login = "{}"'.format(login))
        # user already exists
        if len(qr):
            mb.showerror("Error", "User {} already exists!".format(login))
            return
        # add user
        password_hash = md5(password.encode(settings['FORMAT'])).hexdigest()
        self.server.database.insert("INSERT INTO Users (Login, HashPass) VALUES (%s, %s)", (login, password_hash))
        
        self.sign_on_login.set("")
        self.sign_on_password.set("")
        self.text_console.config(state='normal')
        self.text_console.insert(END, "User {} created!\n".format(login))
        self.text_console.config(state='disabled')
        self.root_reg.destroy()
        
    # send message event
    def __button_send_message(self, event=None):
        # check connection
        if self.server.database.connection is None:
            return
            if self.server.database.connection.is_connected():
                return

        message = self.entry.get()

        self.server.send_message(message)
        self.server.write_console(f"Server: {message}")
        self.entry.delete(0, END)

    # send file event
    def __button_send_file(self, event=None):
        # check connection
        if self.server.database.connection is None:
            return
            if self.server.database.connection.is_connected():
                return

        file_path = fd.askopenfilename(
            title='Open a file',
            initialdir='/',
            filetypes=(('text files', '*.txt'), ('All files', '*.*')))
        
        if len(file_path) == 0:
            return

        file_type = file_path.split('.')[-1]
        with open(file_path, "rb") as f:
            file_bytes = f.read()

        snd_signal = threading.Thread(target=self.server.send_message, args=("STATE FILE",))
        snd_signal.start()
        snd = threading.Thread(target=self.server.send_file, args=(file_bytes, file_type))
        snd.start()