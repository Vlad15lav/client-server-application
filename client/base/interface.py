import socket
import threading

from tkinter import *
from tkinter import messagebox as mb
from tkinter import filedialog as fd
from datetime import datetime

from base.client import Client

# client interface
class MainForm(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.frame = Frame(self, bg='#fafafa')
        self.parent = parent
        self.parent.resizable(width=False, height=False)

        # windows size
        self.window_w = 500
        self.window_h = 340

        self.centerWindow()
        self.initUI()
        self.showUI()

        self.client = Client(self.text_console)

        # values for connection and authentication
        self.var_address = StringVar()
        self.var_login = StringVar()
        self.var_pass = StringVar()

    def initUI(self):
        self.parent.deiconify()
        self.parent.title("Chat Client")
        self.parent.resizable(width=False, height=False)

        self.chat_frame = Frame(self.parent, bg='#17202a')

        self.label_header = Label(self.chat_frame, text='Welcome to Chat. Please, Sign In!',
                                  bg='#17202a', fg="#EAECEE", font=20)
        self.button_sign_in = Button(self.chat_frame, text='Sign In', bg='gray', command=self.__button_sign_in)
        self.text_console = Text(self.chat_frame, bg="#17202A", fg="#EAECEE", state='disabled')
        
        self.entry = Entry(self.chat_frame, bg="#2c3e50", fg="#EAECEE")
        self.entry.bind('<Return>', self.__button_send_message)
        self.btn_send = Button(self.chat_frame, text='Send', bg='gray', command=self.__button_send_message)
        self.btn_file = Button(self.chat_frame, text='File', bg='gray', command=self.__button_send_file)

        self.parent.protocol("WM_DELETE_WINDOW", self.on_closing)

    def showUI(self):
        self.chat_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.label_header.place(x=10, y=5)
        self.button_sign_in.place(x=410, y=5, width=80, height=22)
        self.text_console.place(x=10, y=35, width=480, height=260)

        self.entry.place(x=10, y=308, width=310, height=22)
        self.btn_send.place(x=325, y=308, width=80, height=23)
        self.btn_file.place(x=410, y=308, width=80, height=23)

    # centring window
    def centerWindow(self):
        sw = self.parent.winfo_screenwidth()
        sh = self.parent.winfo_screenheight()

        x = (sw - self.window_w) / 2
        y = (sh - self.window_h) / 2
        self.parent.geometry('%dx%d+%d+%d' % (self.window_w, self.window_h, x, y))

    ### action methods

    # close window
    def on_closing(self):
        if mb.askokcancel("Quit", "Do you want to quit?"):
            if self.client.is_connect:
                self.client.send_message('STATE CLOSE')
                self.client.close_connect()
                self.client.write_console('Close connection!')
            self.parent.destroy()

    # sign in event
    def __button_sign_in(self, event=None):
        self.root_auth = Toplevel()
        self.root_auth.title("Sign In")
        self.root_auth.resizable(width=False, height=False)
        self.root_auth.configure(width=300, height=160)

        # main field for auth
        self.auth_frame = Frame(self.root_auth, bg='#fafafa')
        self.auth_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        # field for ipv4 and port
        self.label_ip = Label(self.auth_frame, text='IPv4:', bg='#fafafa', font=20)
        self.entry_ip = Entry(self.auth_frame, justify='center', textvariable=self.var_address)
        # field for login name
        self.label_login = Label(self.auth_frame, text='Login:', bg='#fafafa', font=20)
        self.entry_login = Entry(self.auth_frame, justify='center', textvariable=self.var_login)
        # field passwor 
        self.label_password = Label(self.auth_frame, text='Password:', bg='#fafafa', font=20)
        self.entry_password = Entry(self.auth_frame, justify='center', textvariable=self.var_pass, show="*")

        ##### set UI auth on position
        self.label_ip.place(x=10, y=17)
        self.entry_ip.place(x=90, y=20, width=150)
        # set label for login name 
        self.label_login.place(x=10, y=47)
        self.entry_login.place(x=90, y=50, width=150)
        # set label password 
        self.label_password.place(x=10, y=77)
        self.entry_password.place(x=90, y=80, width=150)
        # set button sign on
        self.btn_sign_in = Button(self.auth_frame, text="Sign In", font=20,
                         command=lambda: self.__btn_connection())
        self.btn_sign_in.place(x=100, y=115, width=110, height=25)

    # start connection with server
    def __btn_connection(self):
        # check incorrect values
        if self.var_address.get() == '' or self.var_login.get() == ' ' or self.var_pass.get() == '':
            mb.showerror("Error", "Empty fields!")
            return

        self.ipv4, self.port = self.var_address.get().split(':')
        self.port = int(self.port)
        # check correct ipv4
        try:
            socket.inet_aton(self.ipv4)
        except socket.error:
            mb.showerror("Error", 'Ip address is not legal!')
            return
        #print(self.ipv4, self.port, self.var_login.get(), self.var_pass.get())
        is_connect, status = self.client.connect_server(self.ipv4, self.port,
                                                self.var_login.get(), self.var_pass.get())
        if not is_connect:
            mb.showerror("Error", status)
            return

        self.client.write_console('Connection successful!')
        self.label_header.config(text="Welcome to Chat, {}!".format(self.var_login.get()))
        self.button_sign_in.place_forget()
        self.root_auth.destroy()

    # send message button
    def __button_send_message(self, event=None):
        # check connection
        if not self.client.is_connect:
            return

        message = self.entry.get()
        if len(message) <= 0:
            return

        self.client.write_console(f"{self.var_login.get()}: {message}")
        self.entry.delete(0, END)

        snd = threading.Thread(target=self.__send_message, args=(message,))
        snd.start()

    def __button_send_file(self, event=None):
        # check connection
        if not self.client.is_connect:
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

        snd_signal = threading.Thread(target=self.__send_message, args=("STATE FILE",))
        snd_signal.start()
        snd = threading.Thread(target=self.__send_file, args=(file_bytes, file_type))
        snd.start()

    # send message method
    def __send_message(self, message):
        self.client.send_message(message)

    # send file method
    def __send_file(self, data, file_type):
        self.client.send_file(data, file_type)