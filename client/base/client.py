import socket
import threading

from datetime import datetime, timedelta
from tkinter import *
from tkinter import filedialog as fd
from hashlib import md5

from config.config import settings
from tools.gen import generate_prime, generate_number
from cryptography.rsa import RSA

class Client:
	def __init__(self, console):
		self.console = console
		self.is_connect = False
		self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		self.rsa = RSA(settings['LENGTH_RSA'])
		self.e, self.n = self.rsa.get_public()

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

	# connection to the server
	def connect_server(self, ipv4: str, port: int, login: str, password: str) -> [bool, str]:
		self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.ADDRESS = (ipv4, port)
		
		# connection to server
		try:
			self.client.connect(self.ADDRESS)
		except ConnectionRefusedError:
			return False, 'Connection error!'

		# authentication process
		self.is_connect = self.auth_user(login, password)
		return self.is_connect, 'Authentication error!'

	# authentication
	def auth_user(self, login: str, password: str) -> bool:
		# send login to server
		self.client.send(login.encode(settings['FORMAT']))

		# receve nonse by server
		nonse_hash = self.client.recv(1024).decode(settings['FORMAT'])

		if nonse_hash == 'AUTH 404':
			self.client.close()
			return False

		pass_hash = md5(password.encode(settings['FORMAT'])).hexdigest()
		# final hash is nonse hash + password hash
		final_hash = md5((nonse_hash + pass_hash).encode(settings['FORMAT'])).hexdigest()
		self.client.send(final_hash.encode(settings['FORMAT']))

		# authentication result
		data_auth = self.client.recv(1024).decode(settings['FORMAT']).split(':')
		if data_auth[0] == 'AUTH 404':
			self.client.close()
			return False
		
		## Diffie–Hellman protocol
		b = generate_number(settings['LENGTH_B'])
		g, p, A = list(map(int, data_auth[1:]))
		B = pow(g, b, p)
		self.client.send(str(B).encode(settings['FORMAT']))
		Key = pow(A, b, p)

		## recv RSA public key by server
		pub_key_server = self.client.recv(1024).decode(settings['FORMAT']).split(':')
		pub_key_server = list(map(int, pub_key_server))
		## send RSA public key by client
		self.client.send(f"{self.e}:{self.n}".encode(settings['FORMAT']))

		thread = threading.Thread(target=self.handle, args=(pub_key_server,))
		thread.start()
		return True

	# handle the incoming messages
	def handle(self, pub_key, cipher=None):
		e, n = pub_key

		while True:
			try:
				message = self.client.recv(1024).decode(settings['FORMATMSG']).split(':')

				if message[0] == 'STATE CLOSE':
					self.close_connect()

				elif message[0] == 'STATE FILE':
					self.write_console(f"Server is sending the file!")
					file_info = self.recvall(self.client)
					file_info = file_info.split(b':')
					sign = int(file_info[0].decode(settings['FORMATMSG']))
					file_type = file_info[1].decode(settings['FORMATMSG'])

					# check digital signature
					sign_hash = pow(sign, e, n)
					if sign_hash != int(md5(file_info[-1]).hexdigest(), 16):
						self.write_console(f"Violation of Server's file integrity!")
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
					self.write_console(f"Server's file is saved!")

				elif len(message[0]) > 0:
					self.write_console(f"Server: {message[0]}")
			except Exception as e:
				print(e)
				break

	def close_connect(self):
		self.is_connect = False
		self.client.close()

	# send message method
	def send_message(self, message):
		#message = self.cipher.encode(message.encode(settings['FORMATMSG']))
		self.client.send(message.encode(settings['FORMATMSG']))

	# send file method
	def send_file(self, data, file_type):
		hash_file = int(md5(data).hexdigest(), 16)
		sign = self.rsa.decode(hash_file)
		self.client.send(f"{sign}:{file_type}".encode(settings['FORMAT']) + b':' + data)
