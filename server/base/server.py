import json
import socket
import threading

from datetime import datetime, timedelta
from tkinter import *
from hashlib import md5

from db.database import MySQL
from config.config import settings
from tools.gen import generate_prime, generate_number

class Server:
	def __init__(self, console):
		self.console = console
		self.online = {}

		self.ipv4 = socket.gethostbyname(socket.gethostname()) # IPv4 address
		self.ADDRESS = (self.ipv4, settings['PORT'])

		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # server socket
		self.server.bind(self.ADDRESS)

		self.database = MySQL()

	# recv all package in one
	def recvall(self, sock):
		BUFF_SIZE = 4096  # 4 KiB
		data = b''
		while True:
			part = sock.recv(BUFF_SIZE)
			data += part
			if len(part) < BUFF_SIZE: break
		return data

	# write status in console
	def write_console(self, text: str):
		self.console.config(state='normal')
		time = datetime.now().strftime("[%H:%M:%S]")
		self.console.insert(END, f"{time} {text}\n")
		self.console.see(END)
		self.console.config(state='disabled')

	# start server
	def start(self) -> bool:
		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server.bind(self.ADDRESS)
		self.server.listen()  # listening for connections

		self.console.config(state='normal')
		self.console.insert(END, "Starting server...\n")

		flag_db = self.database.create_connection('localhost', 'root', 'root')
		if not flag_db:
			self.console.insert(END, "MySQL Database error!\n")
			self.console.config(state='disabled')
			return False
		self.console.insert(END, "MySQL Database connected!\n")

		self.thread_listen = threading.Thread(target=self.listen, args=())
		self.thread_listen.start()

		self.console.insert(END, f"Server - {self.ipv4}:{settings['PORT']}\n")
		self.console.insert(END, "Server is started!\n")
		self.console.config(state='disabled')
		return True

	# stop server
	def stop(self):
		self.send_broadcast("STATE:CLOSE")
		self.server.close()
		for k, v in self.online.items():
			try:
				v.close()
			except Exception as e:
				pass
		self.online.clear()
		self.database.stop_connection()

		self.console.config(state='normal')
		self.console.insert(END, "Server is shutdown!\n")
		self.console.config(state='disabled')

	# listen thread
	def listen(self):
		while True:
			try:
				# waiting connect
				user, addr = self.server.accept()

				# wait login name
				data_login = user.recv(1024).decode(settings['FORMAT'])

				qr = self.database.select('SELECT * FROM Users WHERE Login = "{}"'.format(data_login))
				# check login name
				if len(qr) == 0:
					user.send("AUTH:404".encode(settings['FORMAT']))
					self.write_console(f"{'{}:{}'.format(*addr)} failed authentication!")
					continue # auth is failed
				id_user, login_user, pass_hash = qr[0]
				# challenge-response
				qr_ts = self.database.select('SELECT * FROM Sessions WHERE Id = "{}"'.format(id_user))
				if len(qr_ts) == 0: # create nonse
					nonse = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
					nonse_ts = (datetime.now() + timedelta(minutes=settings['TS'])).strftime("%Y-%m-%d %H:%M:%S")
					self.database.insert("INSERT INTO Sessions (Id, Nonse, NonseTS) VALUES (%s, %s, %s)",
						(id_user, nonse, nonse_ts))
					#self.write_console(f"{'{}:{}'.format(*addr)} create new nonse!")
					nonse_status = " (NEW)"
				else:
					_, nonse, nonse_ts = qr_ts[0]
					if nonse_ts < datetime.now():
						nonse = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
						nonse_ts = (datetime.now() + timedelta(minutes=settings['TS'])).strftime("%Y-%m-%d %H:%M:%S")
						self.database.insert("UPDATE Sessions SET Nonse = %s, NonseTS = %s WHERE Id = %s", 
							(nonse, nonse_ts, id_user))
						#self.write_console(f"{'{}:{}'.format(*addr)} update nonse!")
						nonse_status = " (UPDATE)"
					else:
						nonse = nonse.strftime("%Y-%m-%d %H:%M:%S")
						nonse_status = " (USE)"
				self.write_console(f"{'CR:{}:{}'.format(*addr)} nonse {nonse} timestamp {nonse_ts}" + nonse_status)

				# send time stamp
				ts_hash = md5(nonse.encode(settings['FORMAT'])).hexdigest()
				user.send(ts_hash.encode(settings['FORMAT']))
				# calculate final hash
				final_hash = md5((ts_hash + pass_hash).encode(settings['FORMAT'])).hexdigest()
				# waiting hash with TS and password by user
				hash_user = user.recv(1024).decode(settings['FORMAT'])

				# check hash
				if final_hash != hash_user:
					user.send("AUTH:404".encode(settings['FORMAT']))
					self.write_console(f"{'{}:{}'.format(*addr)} failed authentication!")
					continue

				user.send("AUTH:200".encode(settings['FORMAT']))

				### TODO: DH

				self.online[data_login] = user
				thread = threading.Thread(target=self.handle, args=(user, addr, data_login))
				thread.start()

			except Exception as e:
				break

	# handle the incoming messages
	def handle(self, user, addr, login, cipher=None):
		self.write_console(f'{login} is connected!')

		while True:
			try:
				message = user.recv(1024).decode(settings['FORMATMSG'])
				#message = cipher.encode(message).decode(settings['FORMATMSG'])

				if message == 'STATE:CLOSE':
					user.close() # close the connection
					del self.online[login]
					break
				elif len(message) > 0:
					self.write_console(f"{login}: {message}")
			except Exception as e:
				break

		self.write_console(f'{login} left server!')

	# send message for user
	def send_message(self, msg):
		for k, v in self.online.items():
			v.send(msg.encode(settings['FORMATMSG']))

	# send message for all users
	def send_broadcast(self, msg):
		for k, v in self.online.items():
			v.send(msg.encode(settings['FORMATMSG']))