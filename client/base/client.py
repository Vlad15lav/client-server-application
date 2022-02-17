import socket
import threading

from datetime import datetime, timedelta
from tkinter import *
from hashlib import md5

from config.config import settings
from tools.gen import generate_prime, generate_number

class Client:
	def __init__(self, console):
		self.console = console
		self.is_connect = False
		self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

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

		if nonse_hash == 'AUTH:404':
			self.client.close()
			return False

		pass_hash = md5(password.encode(settings['FORMAT'])).hexdigest()
		# final hash is nonse hash + password hash
		final_hash = md5((nonse_hash + pass_hash).encode(settings['FORMAT'])).hexdigest()
		self.client.send(final_hash.encode(settings['FORMAT']))

		# authentication result
		data_auth = self.client.recv(1024).decode(settings['FORMAT'])
		if data_auth == 'AUTH:404':
			self.client.close()
			return False
		
		### TODO: DH
		thread = threading.Thread(target=self.handle, args=())
		thread.start()
		return True

	# handle the incoming messages
	def handle(self, cipher=None):
		while True:
			try:
				message = self.client.recv(1024).decode(settings['FORMATMSG'])
				if message == 'STATE:CLOSE':
					self.close_connect()
				elif len(message) > 0:
					self.write_console(f"Server: {message}")
			except Exception as e:
				break

	def close_connect(self):
		self.is_connect = False
		self.client.close()

	# send message method
	def send_message(self, message):
		#message = self.cipher.encode(message.encode(settings['FORMATMSG']))
		self.client.send(message.encode(settings['FORMATMSG']))