#!/usr/bin/python3

import os
import sys
import socket
import json
import base64
from urllib import response
from common_comm import send_dict, recv_dict, sendrecv_dict

from Crypto.Cipher import AES

# Função para encriptar valores a enviar em formato jsos com codificação base64
# return int data encrypted in a 16 bytes binary string coded in base64
def encrypt_intvalue (cipherkey, data):
	return None


# Função para desencriptar valores recebidos em formato json com codificação base64
# return int data decrypted from a 16 bytes binary strings coded in base64
def decrypt_intvalue (cipherkey, data):
	return None


# verify if response from server is valid or is an error message and act accordingly
def validate_response (client_sock, response):
	if response["op"] == "START" and response["status"]:
		return "NUMBER"
	elif response["op"] == "START" and not(response["status"]):
		return "START"
	elif response["op"] == "NUMBER" and response["status"]:
		return "NUMBER"
	elif response["op"] == "QUIT" and response["status"]:
		return "QUIT"

# process QUIT operation
def quit_action (client_sock):
	return None


# Outcomming message structure:
# { op = "START", client_id, [cipher] }
# { op = "QUIT" }
# { op = "NUMBER", number }
# { op = "STOP" }
#
# Incomming message structure:
# { op = "START", status }
# { op = "QUIT" , status }
# { op = "NUMBER", status }
# { op = "STOP", status, min, max }


#
# Suporte da execução do cliente
#
def run_client (client_sock, client_id):
	# Check if user wants encryption
	user_input = ""
	while(user_input != "s" and user_input != "n"):
		user_input = input("Pretente utilizar encriptação nas mensagens com o servidor? (s/n): ")
	
	# Send START and wait response
	if user_input == "s":
		start_message = { "op": "START", "client_id": client_id, "cipher": None }	#COMPLETAR COM O CIPHER
	elif user_input == "n":
		start_message = { "op": "START", "client_id": client_id, "cipher": None }
	
	response = sendrecv_dict(client_sock, start_message)

	# loop to interact with the server
	loop = True
	while(loop):
		# flag is a variable that holds what operation the client has to do next
		flag = validate_response(client_sock, response)

		if flag == "START":
			# Something went wrong with the START operation, inform client and close client.py
			print("ERRO: " + response["error"])
			sys.exit(1)
		elif flag == "NUMBER":
    		# Input do utilizador
			number = input("Introduza o número inteiro a enviar: ('q' para forçar o encerramento e 's' para parar o envio de novos números): ")
			if number == "q":	
				message = { "op": "QUIT" }
			elif number == "s":
				message = { "op": "STOP" }
			elif not(number.isnumeric()):
				return None
			else:
				message = { "op": "NUMBER", "number": number }
		elif flag == "STOP":
			return None
		elif flag == "QUIT":
			quit_action(client_sock)

		# send message to server
		response = sendrecv_dict(client_sock, message)
    			

def main():
	# validate the number of arguments and eventually print error message and exit with error
	if len(sys.argv) < 3:
		print("Número inválido de argumentos!")
		print("O client.py está a espera de 3 ou 4 argumentos!")
		print("Utilização: python3 client.py (client_id) (número do porto a que se quer ligar) [(maquina)(não utilizar caso o servidor esteja na mesma máquina)]")
		sys.exit(1)
	elif len(sys.argv) > 4:
		print("Número inválido de argumentos!")
		print("O client.py está a espera de 3 ou 4 argumentos!")
		print("Utilização: python3 client.py (client_id) (número do porto a que se quer ligar) [(maquina)(não utilizar caso o servidor esteja na mesma máquina)]")
		sys.exit(1)
	
	# verify type of of arguments and eventually print error message and exit with error
	if len(sys.argv) == 3 and sys.argv[2].isdigit():
		hostname = "127.0.0.1"
		port = (int)(sys.argv[2])
	elif len(sys.argv) == 4 and sys.argv[2].isdigit() and sys.argv[3].isascii():
		hostname = sys.argv[3]
		port = sys.argv[2]
	else:
		print("Utilização inválida!")
		print("Porto nos argumentos deve ser um número!")
		print("Utilização: python3 client.py (client_id) (número do porto a que se quer ligar) [(maquina)(não utilizar caso o servidor esteja na mesma máquina)]")
		sys.exit(1)

	client_sock = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
	client_sock.connect ((hostname, port))

	run_client (client_sock, sys.argv[1])

	client_sock.close ()
	sys.exit (0)

if __name__ == "__main__":
    main()
