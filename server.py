#!/usr/bin/python3

import sys
import socket
import select
import json
import base64
import csv
import random
from urllib import request, response
from common_comm import send_dict, recv_dict, sendrecv_dict

from Crypto.Cipher import AES

# Dicionário com a informação relativa aos clientes
users = {}

# return the client_id of a socket or None
def find_client_id (client_sock):
	for key, value in users.items():
		if value["socket"].getsockname() == client_sock.getsockname():
			return key
	return None

# Função para encriptar valores a enviar em formato json com codificação base64
# return int data encrypted in a 16 bytes binary string and coded base64
def encrypt_intvalue (client_id, data):
	return None


# Função para desencriptar valores recebidos em formato json com codificação base64
# return int data decrypted from a 16 bytes binary string and coded base64
def decrypt_intvalue (client_id, data):
	return None


# Incomming message structure:
# { op = "START", client_id, [cipher] }
# { op = "QUIT" }
# { op = "NUMBER", number }
# { op = "STOP" }
#
# Outcomming message structure:
# { op = "START", status }
# { op = "QUIT" , status }
# { op = "NUMBER", status }
# { op = "STOP", status, min, max }


#
# Suporte de descodificação da operação pretendida pelo cliente
#
def new_msg (client_sock):
# read the client request
	message = recv_dict(client_sock)
# detect the operation requested by the client
	op = message["op"]
# execute the operation and obtain the response (consider also operations not available)
	if op == "START":
		response = new_client(client_sock, message)
	elif op == "NUMBER":
		response = number_client(client_sock, message)
	elif op == "STOP":
		response = stop_client(client_sock)
	elif op == "QUIT":
		response = quit_client(client_sock, message)
# send the response to the client
	send_dict(client_sock, response)


#
# Suporte da criação de um novo jogador - operação START
#
def new_client (client_sock, request):
# detect the client in the request
	client_id = find_client_id(client_sock)
# verify the appropriate conditions for executing this operation
	if client_id == None:
		client_info = { "socket": client_sock, "cipher": None, "numbers": []}
		client = {request["client_id"]: client_info}
# process the client in the dictionary
		users.update(client)
		message = {"op": "START", "status": True}
# return response message with or without error message
	else:
		message = {"op": "START", "status": False, "error": "Cliente existente"}
	return message



#
# Suporte da eliminação de um cliente
#
def clean_client (client_sock):
# obtain the client_id from his socket and delete from the dictionary
	client_id = find_client_id(client_sock)
	users.pop(client_id)

#
# Suporte do pedido de desistência de um cliente - operação QUIT
#
def quit_client (client_sock, request):
# obtain the client_id from his socket
	client_id = find_client_id(client_sock)
# verify the appropriate conditions for executing this operation
	if client_id != None:
# process the report file with the QUIT result
		result = find_results(client_sock)
		update_file(client_sock, result)
# eliminate client from dictionary
		response = {"op": "QUIT", "status": True}
	else:
		response = {"op": "QUIT", "status": False, "error": "Cliente inexixtente"}
# return response message with or without error message
	return response


#
# Suporte da criação de um ficheiro csv com o respectivo cabeçalho
#
def create_file ():
# create report csv file with header
	fout = open("report.csv","w")
	header_writer = csv.DictWriter(fout, fieldnames=["client_id", "numbers_received", "results"], delimiter="|")
	header_writer.writeheader()
	

#
# Suporte da actualização de um ficheiro csv com a informação do cliente e resultado
#
def update_file (client_id, result):
	fout = open("report.csv", "w")
# update report csv file with the result from the client


#
# Suporte do processamento do número de um cliente - operação NUMBER
#
def number_client (client_sock, request):
# obtain the client_id from his socket
	client_id = find_client_id(client_sock)
# verify the appropriate conditions for executing this operation
	if client_id != None:
	# return response message with or without error message
	#verificaçao?
		auxDict = users[client_id]
		auxDict["numbers"].append(request["number"])
		users.update({client_id: auxDict})
		response = { "op": "NUMBER", "status": True }
	else:
		response = { "op": "NUMBER", "status": False, "error": "Cliente inexistente" }
	return response

#
# Suporte do pedido de terminação de um cliente - operação STOP
#
def stop_client (client_sock):
# obtain the client_id from his socket
	client_id = find_client_id(client_sock)
# verify the appropriate conditions for executing this operation
	if client_id != None:
# process the report file with the result
		update_file(client_sock, qualquer coisa)
# eliminate client from dictionary
		clean_client(client_sock)
		#response = { "op": "STOP", "status": True, "min": número mínimo, "max": número máximo }
# return response message with result or error message


def main():
	# validate the number of arguments and eventually print error message and exit with error
	if len(sys.argv) < 2:
		print("Número inválido de argumentos!")
		print("O server.py está a espera de 2 argumentos!")
		print("Utilização: python3 server.py (número do porto a que se quer ligar)")
		sys.exit(1)
	elif len(sys.argv) > 2:
		print("Número inválido de argumentos!")
		print("O server.py está a espera de 2 argumentos!")
		print("Utilização: python3 server.py (porto a que se quer ligar)")
		exit(1)
	
	# verify type of of arguments and eventually print error message and exit with error
	if sys.argv[1].isdigit():
		port = (int)(sys.argv[1])
	else:
		print("Utilização inválida!")
		print("Porto nos argumentos deve ser um número!")
		print("Utilização: python3 server.py (número do porto a que se quer ligar)")
		sys.exit(2)

	server_socket = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
	server_socket.bind (("127.0.0.1", port))
	server_socket.listen (10)

	clients = []
	create_file ()

	while True:
		try:
			available = select.select ([server_socket] + clients, [], [])[0]
		except ValueError:
			# Sockets may have been closed, check for that
			for client_sock in clients:
				if client_sock.fileno () == -1: clients.remove (client_sock) # closed
			continue # Reiterate select

		for client_sock in available:
			# New client?
			if client_sock is server_socket:
				newclient, addr = server_socket.accept ()
				clients.append (newclient)
			# Or an existing client
			else:
				# See if client sent a message
				if len (client_sock.recv (1, socket.MSG_PEEK)) != 0:
					# client socket has a message
					##print ("server" + str (client_sock))
					new_msg (client_sock)
				else: # Or just disconnected
					clients.remove (client_sock)
					clean_client (client_sock)
					client_sock.close ()
					break # Reiterate select

if __name__ == "__main__":
	main()
