import json
import socket
import threading

from datetime import datetime, timedelta
from tkinter import *
from tkinter import filedialog as fd
from hashlib import md5

from db.database import MySQL
from config.config import settings
from tools.gen import generate_prime, generate_number, generate_primitive
from protection.rsa import RSA
from protection.des import DES

class Server:
	def __init__(self, console):
		self.console = console
		self.online = {}
		self.ciphers = {}

		self.ipv4 = socket.gethostbyname(socket.gethostname()) # IPv4 address
		self.ADDRESS = (self.ipv4, settings['PORT'])

		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # server socket
		self.server.bind(self.ADDRESS)

		self.database = MySQL()

		# thread for calculate RSA and DH
		self.thread_cryp = threading.Thread(target=self.__init_cryptography, args=())
		self.thread_cryp.start()

	def __init_cryptography(self):
		self.g, self.p = generate_primitive(settings['LENGTH_G'], settings['LENGTH_P'], count_div=8)
		self.rsa = RSA(settings['LENGTH_RSA'])
		self.e, self.n = self.rsa.get_public()

	# recv all package in one
	def recvall(self, sock, cipher):
		BUFF_SIZE = 1024  # 4 KiB
		data = b''
		while True:
			part = cipher.encode(sock.recv(BUFF_SIZE), False)
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

		self.thread_cryp.join() # wait calculate
		self.thread_listen = threading.Thread(target=self.listen, args=())
		self.thread_listen.start()

		self.console.insert(END, f"Server - {self.ipv4}:{settings['PORT']}\n")
		self.console.insert(END, "Server is started!\n")
		self.console.config(state='disabled')
		return True

	# stop server
	def stop(self):
		self.send_broadcast("STATE CLOSE")
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
					user.send("AUTH 404".encode(settings['FORMAT']))
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
					user.send("AUTH 404".encode(settings['FORMAT']))
					self.write_console(f"{'{}:{}'.format(*addr)} failed authentication!")
					continue

				# Diffie–Hellman protocol
				a = generate_number(settings['LENGTH_A'])
				A = pow(self.g, a, self.p)
				# send parameters
				user.send(f"AUTH 200:{self.g}:{self.p}:{A}".encode(settings['FORMAT']))
				# recv parameters by client
				B = int(user.recv(1024).decode(settings['FORMAT']))
				Key = str(pow(B, a, self.p))
				Key = md5(Key.encode()).digest()[:8] # 8 byte for DES
				print('DES Key - {}'.format(Key))

				## send RSA public key by server
				user.send(f"{self.e}:{self.n}".encode(settings['FORMAT']))
				## recv RSA public key by client
				pub_key_client = user.recv(1024).decode(settings['FORMAT']).split(':')
				pub_key_client = list(map(int, pub_key_client))

				self.online[data_login] = user
				self.ciphers[data_login] = DES(Key)
				thread = threading.Thread(target=self.handle, args=(user, addr,
																	data_login,
																	pub_key_client))
				thread.start()

			except Exception as e:
				print(e)
				break

	# handle the incoming messages
	def handle(self, user, addr, login, pub_key_client):
		self.write_console(f'{login} is connected!')
		e, n = pub_key_client
		print('{} public key:\ne - {}\nn - {}'.format(login, e, n))

		while True:
			try:
				message = user.recv(1024)#.decode(settings['FORMATMSG']).split(':')
				message = self.ciphers[login].encode(message, False).decode(settings['FORMATMSG']).split(':')

				if message[0] == 'STATE CLOSE':
					user.close() # close the connection
					del self.online[login]
					del self.ciphers[login]
					break

				elif message[0] == 'STATE FILE':
					self.write_console(f"{login} is sending the file!")
					file_info = self.recvall(user, self.ciphers[login])
					file_info = file_info.split(b':')
					sign = int(file_info[0].decode(settings['FORMATMSG']))
					file_type = file_info[1].decode(settings['FORMATMSG'])

					# check digital signature
					sign_hash = pow(sign, e, n)
					if sign_hash != int(md5(file_info[-1]).hexdigest(), 16):
						self.write_console(f"Violation of {login}'s file integrity!")
						continue

					# dialog for path of save
					f = fd.asksaveasfile(
						mode='wb',
						title='Save a file',
						initialdir='/',
						defaultextension=f".{file_type}",
						filetypes=((f'{file_type} files', f"*.{file_type}"),))
					if f is None:
						continue

					f.write(file_info[-1])
					f.close()
					self.write_console(f"{login}'s file is saved!")

				elif len(message[0]) > 0:
					self.write_console(f"{login}: {message[0]}")
			except Exception as e:
				print(e)
				break

		self.write_console(f'{login} left server!')

	# send message for user
	def send_message(self, msg):
		for k, v in self.online.items():
			message = msg.encode(settings['FORMATMSG'])
			v.send(self.ciphers[k].encode(message, True))

	# send message for all users
	def send_broadcast(self, msg):
		for k, v in self.online.items():
			message = msg.encode(settings['FORMATMSG'])
			v.send(self.ciphers[k].encode(message, True))

	# send file method
	def send_file(self, data, file_type):
		hash_file = int(md5(data).hexdigest(), 16)
		sign = self.rsa.decode(hash_file)
		message = f"{sign}:{file_type}".encode(settings['FORMAT']) + b':' + data

		for k, v in self.online.items():
			v.send(self.ciphers[k].encode(message, True))