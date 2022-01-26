import json
import socket
import threading

from datetime import datetime, timedelta
from tkinter import *
from hashlib import md5

from base.rc4 import RC4
from config.config import settings
from tools.gen import generate_prime, generate_number

class Server:
    def __init__(self, console):
        self.console = console
        self.load_database()
        self.timestamp = {}
        self.online = {}

        self.ipv4 = socket.gethostbyname(socket.gethostname()) # IPv4 address
        self.ADDRESS = (self.ipv4, settings['PORT'])

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # server socket
        self.server.bind(self.ADDRESS)

    def write_console(self, text: str):
        self.console.config(state='normal')
        time = datetime.now().strftime("[%H:%M:%S]")
        self.console.insert(END, f"{time} {text}\n")
        self.console.config(state='disabled')

    # load database with login and hash password
    def load_database(self):
        with open(settings['DATABASE'], "r") as read_file:
            self.database = json.load(read_file)

    # check exception login in database
    def find_login(self, login: str) -> bool:
        check = True
        try:
            self.database[login]
        except Exception as e:
            check = False
        return check

    # start server
    def start(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.ADDRESS)
        self.server.listen()  # listening for connections

        self.console.config(state='normal')
        self.console.insert(END, "Starting server...\n")

        self.thread_listen = threading.Thread(target=self.listen, args=())
        self.thread_listen.start()

        self.console.insert(END, f"Server - {self.ipv4}:{settings['PORT']}\n")
        self.console.insert(END, "Server is started!\n")
        self.console.config(state='disabled')

    # listen thread
    def listen(self):
        while True:
            try:
                # waiting connect
                user, addr = self.server.accept()

                # wait login name
                data_login = user.recv(1024).decode(settings['FORMAT'])

                # check login name
                if not self.find_login(data_login):
                    user.send("AUTH:404".encode(settings['FORMAT']))
                    self.write_console(f"{'{}:{}'.format(*addr)} failed authentication!")
                    #self.console.insert(END, f"{'{}: {}'.format(*addr)} failed authentication!\n")
                    continue # auth is failed

                # create time stamp
                ts = generate_number(16)
                self.timestamp[ts] = datetime.now() + timedelta(0, settings['TS'])
                # send time stamp
                user.send(str(ts).encode(settings['FORMAT']))
                # calculate final hash
                ts_hash = md5(str(ts).encode(settings['FORMAT'])).hexdigest()
                pass_hash = self.database[data_login]
                final_hash = md5((ts_hash + pass_hash).encode(settings['FORMAT'])).hexdigest()
                # waiting hash with TS and password by user
                hash_user = user.recv(1024).decode(settings['FORMAT'])

                if final_hash != hash_user:
                    user.send("AUTH:404".encode(settings['FORMAT']))
                    self.write_console(f"{'{}:{}'.format(*addr)} failed authentication!")
                    continue

                user.send("AUTH:200".encode(settings['FORMAT']))

                # create DH channel
                # generate b
                b = generate_number(64)
                # waiting params g, p, A by server
                g, p, A = user.recv(1024).decode(settings['FORMAT']).split(':')
                g, p, A = int(g), int(p), int(A)
                # B=g^b mod p
                B = pow(g, b, p)
                # send to server param B
                user.send(str(B).encode(settings['FORMAT']))
                # Key = A^b mod p
                self.key = pow(A, b, p)

                # RC4 init
                cipher = RC4(key=self.key)

                self.online[data_login] = user
                thread = threading.Thread(target=self.handle, args=(user, addr, data_login, cipher))
                thread.start()

            except Exception as e:
                break

    # stop server
    def stop(self):
        # self.server.shutdown(SHUT_RDWR)
        self.server.close()
        for k, v in self.online.items():
            v.close()

        self.console.config(state='normal')
        self.console.insert(END, "Server is shutdown!\n")
        self.console.config(state='disabled')

    # method to handle the
    # incoming messages
    def handle(self, user, addr, login, cipher):
        #self.console.insert(END, f'{login} is connected!\n')
        self.write_console(f'{login} is connected!')

        while True:
            try:
                message = user.recv(1024)
                message = cipher.encode(message).decode(settings['FORMATMSG'])

                if message == 'STATE:CLOSE':
                    break
                elif len(message) > 0:
                    self.write_console(f"{login}: {message}")
                    #self.console.config(state='normal')
                    #time = datetime.now().strftime("[%H:%M:%S]")
                    #self.console.insert(END, f"{login}{time}: {message}\n")
                    #self.console.config(state='disabled')

                #self.broadcastMessage('MSG:'.encode(settings['FORMAT']) + message)
            except Exception as e:
                break

        #self.console.insert(END, f'{login} left server!\n')
        self.write_console(f'{login} left server!')
        user.close()  # close the connection

    # send message for connection
    # def send(self, user, msg):
    #     user.send(msg.encode(settings['FORMAT']))

    # # recv all package in one
    # def recvall(self, sock):
    #     BUFF_SIZE = 4096  # 4 KiB
    #     data = b''
    #     while True:
    #         part = sock.recv(BUFF_SIZE)
    #         data += part
    #         if len(part) < BUFF_SIZE: break
    #     return data