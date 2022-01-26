import socket
import threading

from tkinter import *
from tkinter import messagebox as mb
from datetime import datetime

from base.client import Client

# Client interface
class MainForm:
    def __init__(self):
        self.client = Client()

        # Main Chat window
        self.chat_window = Tk()
        self.chat_window.withdraw()
        self.chat_window.configure(width=500, height=340)

        # value for connection and authentication
        self.var_address = StringVar()
        self.var_login = StringVar()
        self.var_pass = StringVar()

        ##### auth window for sign on
        self.login_window = Toplevel()
        self.login_window.title("Sign On")
        self.login_window.resizable(width=False, height=False)
        self.login_window.configure(width=300, height=160)

        # main field for auth
        self.login_frame = Frame(self.login_window, bg='#fafafa')
        self.login_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        # field for ipv4 and port
        self.label_ip = Label(self.login_frame, text='IPv4:', bg='#fafafa', font=20)
        self.entry_ip = Entry(self.login_frame, justify='center', textvariable=self.var_address)
        # field for login name
        self.label_login = Label(self.login_frame, text='Login:', bg='#fafafa', font=20)
        self.entry_login = Entry(self.login_frame, justify='center', textvariable=self.var_login)
        # field passwor 
        self.label_password = Label(self.login_frame, text='Password:', bg='#fafafa', font=20)
        self.entry_password = Entry(self.login_frame, justify='center', textvariable=self.var_pass, show="*")

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
        self.btn_signon = Button(self.login_frame, text="Sign On", font=20,
                         command=lambda: self.__btn_connection())
        self.btn_signon.place(x=100, y=115, width=110, height=25)

        # close window event
        self.chat_window.protocol("WM_DELETE_WINDOW", self.on_closing)
        # show window
        self.chat_window.mainloop()


    def on_closing(self):
        if mb.askokcancel("Quit", "Do you want to quit?"):
            self.client.send_message('STATE:CLOSE')
            self.client.close_connect()
            self.chat_window.destroy()

    # Start connection
    def __btn_connection(self):
        # Check incorrect values
        if self.var_address.get() == '' or self.var_login.get() == ' ' or self.var_pass.get() == '':
            mb.showerror("Error", "Empty fields!")
            return
        self.ipv4, self.port = self.var_address.get().split(':')
        self.port = int(self.port)

        # check correct ipv4
        try:
            socket.inet_aton(self.ipv4)
        except socket.error:
            mb.showerror("Error", 'Ip address is not legal')
            return

        is_connect = self.client.connect_server(self.ipv4, self.port,
                                                self.var_login.get(), self.var_pass.get())

        if is_connect:
            self.login_window.destroy()
            self.show_chat()
        #else:
        #    self.login_window.destroy()

    # the main layout of the chat
    def show_chat(self):
        self.chat_window.deiconify()
        self.chat_window.title("Chat Client")
        self.chat_window.resizable(width=False, height=False)

        self.chat_frame = Frame(self.chat_window, bg='#17202a')
        self.chat_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.label_header = Label(self.chat_frame, text='Welcome to Chat, {}!'.format(self.var_login.get()),
                                  bg='#17202a', fg="#EAECEE", font=20)
        self.text_console = Text(self.chat_frame, bg="#17202A", fg="#EAECEE", state='disabled') # state='disabled'
 
        self.entry = Entry(self.chat_frame, bg="#2c3e50", fg="#EAECEE")
        self.entry.bind('<Return>', self.send_button)
        self.button = Button(self.chat_frame, text='Send', bg='gray', command=self.send_button)

        self.label_header.place(x=10, y=5)
        self.text_console.place(x=10, y=35, width=480, height=260)

        self.entry.place(x=10, y=308, width=390, height=22)
        self.button.place(x=410, y=308, width=80, height=22)

    # send message button
    def send_button(self, event=None):
        message = self.entry.get()
        if len(message) <= 0:
            return

        self.text_console.config(state='normal')
        time = datetime.now().strftime("[%H:%M:%S]")
        self.text_console.insert(END, f"{self.var_login.get()}{time}: {message}\n")
        self.text_console.config(state='disabled')
        self.entry.delete(0, END)

        snd = threading.Thread(target=self.send_message, args=(message,))
        snd.start()

    # send message method
    def send_message(self, message):
        self.client.send_message(message)