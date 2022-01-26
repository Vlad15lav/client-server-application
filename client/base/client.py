import socket
import threading

from hashlib import md5

from base.rc4 import RC4
from config.config import settings
from tools.gen import generate_prime, generate_number

class Client:
	def __init__(self):
		self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	def connect_server(self, ipv4: str, port: int, login: str, password: str) -> bool:
		self.ADDRESS = (ipv4, port)
		
		# connection to server
		try:
			self.client.connect(self.ADDRESS)
		except ConnectionRefusedError:
			return False

		# authentication process
		is_connect = self.auth_user(login, password)
		return is_connect

	# authentication (return True if success)
	def auth_user(self, login: str, password: str) -> bool:
		# send login to server
		self.client.send(login.encode(settings['FORMAT']))

		# receve time stamp by server
		ts_server = self.client.recv(1024).decode(settings['FORMAT'])
		if ts_server == 'AUTH:404':
			self.client.close()
			return False

		ts_hash = md5(ts_server.encode(settings['FORMAT'])).hexdigest()
		pass_hash = md5(password.encode(settings['FORMAT'])).hexdigest()
		# final hash is TS hash + password hash
		final_hash = md5((ts_hash + pass_hash).encode(settings['FORMAT'])).hexdigest()
		self.client.send(final_hash.encode(settings['FORMAT']))

		# authentication result
		data_auth = self.client.recv(1024).decode(settings['FORMAT'])
		if data_auth == 'AUTH:404':
			self.client.close()
			return False
		
		# create DH channel
		# generate a, g, p, A=g^a mod p
		a, g = generate_number(64), generate_number(64)
		p = generate_prime(512)
		A = pow(g, a, p)
		# send to client param g, p, A
		self.client.send(f"{g}:{p}:{A}".encode(settings['FORMAT']))
		# waiting param B
		B = self.client.recv(1024).decode(settings['FORMAT'])
		B = int(B)
		# Key = B^a mod p
		self.key = pow(B, a, p)

		# RC4 init
		self.cipher = RC4(key=self.key)

		return True

	def close_connect(self):
		self.client.close()

	# send message method
	def send_message(self, message):
		message = self.cipher.encode(message.encode(settings['FORMATMSG']))
		self.client.send(message)

#########
	# def on_closing(self):
	#     if mb.askokcancel("Quit", "Do you want to quit?"):
	#         self.send_message('STATE:CLOSE')
	#         self.client.close()
	#         self.chat_window.destroy()

	# # Start connection
	# def __btn_connection(self):
	#     # Check incorrect values
	#     if self.var_address.get() == '' or self.var_login.get() == ' ' or self.var_pass.get() == '':
	#         mb.showerror("Error", "Empty fields!")
	#         return
	#     self.ipv4, self.port = self.var_address.get().split(':')
	#     self.port = int(self.port)

	#     # check correct ipv4
	#     try:
	#         socket.inet_aton(self.ipv4)
	#     except socket.error:
	#         mb.showerror("Error", 'Ip address is not legal')
	#         return

	#     self.ADDRESS = (self.ipv4, self.port)
	#     self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	#     # the thread to receive messages
	#     result_auth = self.auth_user()
	#     if result_auth:
	#         self.login_window.destroy()
	#         self.show_chat()
	#     #else:
	#     #    self.login_window.destroy()

	# # the main layout of the chat
	# def show_chat(self):
	#     self.chat_window.deiconify()
	#     self.chat_window.title("Chat")
	#     self.chat_window.resizable(width=False, height=False)

	#     self.chat_frame = Frame(self.chat_window, bg='#17202a')
	#     self.chat_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

	#     self.label_header = Label(self.chat_frame, text='Welcome to Chat, {}!'.format(self.var_login.get()),
	#                               bg='#17202a', fg="#EAECEE", font=20)
	#     self.text_console = Text(self.chat_frame, bg="#17202A", fg="#EAECEE") # state='disabled'
 
	#     self.entry = Entry(self.chat_frame, bg="#2c3e50", fg="#EAECEE")
	#     self.entry.bind('<Return>', self.send_button)
	#     self.button = Button(self.chat_frame, text='Send', bg='gray', command=self.send_button)

	#     self.label_header.place(x=10, y=5)
	#     self.text_console.place(x=10, y=35, width=480, height=260)

	#     self.entry.place(x=10, y=308, width=390, height=22)
	#     self.button.place(x=410, y=308, width=80, height=22)

	# # send message button
	# def send_button(self, event=None):
	#     message = self.entry.get()
	#     if len(message) <= 0:
	#         return

	#     self.text_console.config(state='normal')
	#     self.text_console.insert(END, f"{self.var_login.get()}:{message}\n")
	#     self.text_console.config(state='disabled')
	#     self.entry.delete(0, END)

	#     snd = threading.Thread(target=self.send_message, args=(message,))
	#     snd.start()

	# # to receive messages method
	# def auth_user(self):
	#     # connection to server
	#     try:
	#         self.client.connect(self.ADDRESS)
	#     except ConnectionRefusedError:
	#         mb.showerror("Error", 'Connection is not established!')
	#         return False

	#     # send login to server
	#     self.client.send(self.var_login.get().encode(settings['FORMAT']))

	#     # receve time stamp by server
	#     ts_server = self.client.recv(1024).decode(settings['FORMAT'])
	#     if ts_server == 'AUTH:404':
	#         mb.showerror("Error", "Authentication error!")
	#         self.client.close()
	#         return False

	#     ts_hash = md5(ts_server.encode(settings['FORMAT'])).hexdigest()
	#     pass_hash = md5(self.var_pass.get().encode(settings['FORMAT'])).hexdigest()
	#     # final hash is TS hash + password hash
	#     final_hash = md5((ts_hash + pass_hash).encode(settings['FORMAT'])).hexdigest()
	#     self.client.send(final_hash.encode(settings['FORMAT']))

	#     # auth result
	#     data_auth = self.client.recv(1024).decode(settings['FORMAT'])
	#     print(data_auth)
	#     if data_auth == 'AUTH:404':
	#         mb.showerror("Error", "Authentication error!")
	#         self.client.close()
	#         return False
	#     else:
	#         # create DH channel
	#         # generate a, g, p, A=g^a mod p
	#         a, g = generate_number(64), generate_number(64)
	#         p = generate_prime(512)
	#         A = pow(g, a, p)
	#         # send to client param g, p, A
	#         self.client.send(f"{g}:{p}:{A}".encode(settings['FORMAT']))
	#         # waiting param B
	#         B = self.client.recv(1024).decode(settings['FORMAT']) # error
	#         B = int(B)
	#         # Key = B^a mod p
	#         key = pow(B, a, p)

	#         return True

	# # send message method
	# def send_message(self, message):
	#     self.client.send(message.encode(settings['FORMAT']))

