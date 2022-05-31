#!/usr/bin/python3

import os
import re
import sys
import socket
import json
import base64
from common_comm import send_dict, recv_dict, sendrecv_dict

#from Crypto.Cipher import AES

# Função para encriptar valores a enviar em formato jsos com codificação base64
# return int data encrypted in a 16 bytes binary string coded in base64
def encrypt_intvalue (cipherkey, data):
	cipher = AES.new(cipherkey, AES.MODE_ECB)
	tosend = cipher.encrypt(bytes("%16d" % (data), "utf-8"))
	return str(base64.b64encode(tosend), "utf-8")


# Função para desencriptar valores recebidos em formato json com codificação base64
# return int data decrypted from a 16 bytes binary strings coded in base64
def decrypt_intvalue (cipherkey, data):
	cipher = AES.new(cipherkey, AES.MODE_ECB)
	data = base64.b64decode(data)
	data = cipher.decrypt(data)
	return int(str(data, "utf-8"))	


# verify if response from server is valid or is an error message and act accordingly
def validate_response (client_sock, response):
	if response["op"] == "START" and response["status"]:
		return "NUMBER"
	elif response["op"] == "START" and not(response["status"]):
		# Something went wrong with the START operation, inform client and close client.py
		print("ERRO: " + response["error"])
		sys.exit(3)
	elif response["op"] == "NUMBER" and response["status"]:
		return "NUMBER"
	elif response["op"] == "NUMBER" and not(response["status"]):
		print("ERRO: " + response["error"])
		sys.exit(3)
	elif response["op"] == "STOP" and response["status"]:
		return "STOP"
	elif response["op"] == "STOP" and not(response["status"]):
		print("ERRO: " + response["error"])
		sys.exit(3)
	elif response["op"] == "QUIT" and response["status"]:
		return "QUIT"
	elif response["op"] == "QUIT" and not(response["status"]):
		print("ERRO: " + response["error"])
		sys.exit(3)


# process QUIT operation
def quit_action (client_sock):
	print("Terminou a conexao com o servidor!")
	client_sock.close()
	sys.exit(4)


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


def check_number_input(number):
	if re.match("[-+]?\d+$", number):
		return False
	else:
		if number == "q" or number == "s":
			return False
		else:
			return True


#
# Suporte da execução do cliente
#
def run_client (client_sock, client_id):
	numbers = []
	
	# Check if user wants encryption
	user_input = ""
	while(user_input != "s" and user_input != "n"):
		user_input = input("Pretente utilizar encriptação nas mensagens com o servidor? (s/n): ")
	
	# Send START and wait response
	if user_input == "s":
		cifra = True
		# Criação da cifra de encriptação
		cipherkey = os.urandom(16)
		cipherkey_tosend = str(base64.b64encode(cipherkey), "utf-8")
		print(cipherkey_tosend)
		start_message = { "op": "START", "client_id": client_id, "cipher": cipherkey_tosend }	#COMPLETAR COM O CIPHER
	elif user_input == "n":
		cifra = False
		start_message = { "op": "START", "client_id": client_id, "cipher": None }
	
	response = sendrecv_dict(client_sock, start_message)

	# loop to interact with the server
	loop = True
	while(loop):
		# flag is a variable that holds what operation the client has to do next
		flag = validate_response(client_sock, response)
	
		if flag == "NUMBER":
    		# Input do utilizador
			number = input("Introduza o número inteiro a enviar: ('q' para forçar o encerramento e 's' para parar o envio de novos números): ")
			while check_number_input(number):
				print("Valor inválido!")
				number = input("Introduza o número inteiro a enviar: ('q' para forçar o encerramento e 's' para parar o envio de novos números): ")
			# Operaçao pretendida pelo utilizador
			if number == "q":	
				message = { "op": "QUIT" }
			elif number == "s":
				message = { "op": "STOP" }
			else:
				if cifra:
					numbers.append((int)(number))
					message = { "op": "NUMBER", "number": encrypt_intvalue(cipherkey ,(int)(number)) }
				else:
					numbers.append((int)(number))
					message = { "op": "NUMBER", "number": (int)(number) }
		elif flag == "STOP":
			# Print dos resultados
			if cifra:
				print("Total de números: " + str(numbers) + ", Mínimo: " + str(decrypt_intvalue(cipherkey, response["min"])) + ", Máximo: " + str(decrypt_intvalue(cipherkey, response["max"])))
			else:
				print("Total de números: " + str(numbers) + ", Mínimo: " + str(response["min"]) + ", Máximo: " + str(response["max"]))
			quit_action(client_sock)
		elif flag == "QUIT":
			quit_action(client_sock)

		# send message to server
		response = sendrecv_dict(client_sock, message)
    			

def main():
	# validate the number of arguments and eventually print error message and exit with error
	if len(sys.argv) < 3 or len(sys.argv) > 4:
		print("Número inválido de argumentos!")
		print("O client.py está a espera de 3 ou 4 argumentos!")
		print("Utilização: python3 client.py (client_id) (número do porto a que se quer ligar) [(maquina)(não utilizar caso o servidor esteja na mesma máquina)]")
		sys.exit(1)
	
	
	# verify type of of arguments and eventually print error message and exit with error
	if len(sys.argv) == 3 and sys.argv[2].isdigit():
		if (int)(sys.argv[2]) >= 0 and (int)(sys.argv[2]) <= 65535:
			hostname = "127.0.0.1"
			port = (int)(sys.argv[2])
		else:
			print("Utilização inválida!")
			print("Número do porto deve estar compreendido entre 0 e 65535!")
			sys.exit(2)
	elif len(sys.argv) == 4 and sys.argv[2].isdigit() and sys.argv[3].isascii():
		if (int)(sys.argv[2]) >= 0 and (int)(sys.argv[2]) <= 65535:
			hostname = sys.argv[3]
			port = sys.argv[2]
		else:
			print("Utilização inválida!")
			print("Número do porto deve estar compreendido entre 0 e 65535!")
			sys.exit(2)
	else:
		print("Utilização inválida!")
		print("Porto nos argumentos deve ser um número!")
		print("Utilização: python3 client.py (client_id) (número do porto a que se quer ligar) [(maquina)(não utilizar caso o servidor esteja na mesma máquina)]")
		sys.exit(2)

	client_sock = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
	client_sock.connect ((hostname, port))

	##TRY CATCH
	run_client (client_sock, sys.argv[1])

	client_sock.close ()
	sys.exit (0)

if __name__ == "__main__":
    main()
