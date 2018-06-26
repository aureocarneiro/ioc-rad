#!/usr/bin/python
# -*- coding: utf-8 -*-

# Módulo necessário

import serial
import requests
import socket
import sys
import threading
import time
import datetime
import logging
import redis

# Definindo as viaveis

dataGamma = 0.0
dataNeutron = 0.0
ipGamma = "192.168.0.100"
ipNeutron = "192.168.0.200"

client_socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket1.connect((ipGamma, 10001))

client_socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket2.connect((ipNeutron, 10001))

# Log File for exceptions

logging.basicConfig(filename='app.log',level=logging.INFO)

r = redis.Redis(host = '10.0.6.48', port = 6379, db = 1)

# Função que inclui o checksum e o caractere <ETX> a qualquer mensagem que se deseja enviar

def format_message(message):

    checksum = ord(message[3]) ^ ord(message[4])
    for character in message[5:]:
        checksum ^= ord(character)
    return (message + "{0:02X}".format(checksum) + "\x03")


# Cria socket TCP/IP para comunicação com o SATURN I 5700 RTM da sonda de gamma

def cnct1(ip):

    # Requisita os valores das janelas de tempo para cáculo da média móvel
    # COLOCAR TB O VALOR O THRESHOLD LEVEL 01001GL RESPOSTA: (STX)01024GL1234.56:1234.56:1234.56
    # (CS)(CS) (ETX)

    client_socket1.send(format_message("\x0201001MI"))
    data = client_socket1.recv(1024)
    if data.find("K") != -1 or data.find("P") != -1 or data.find("B") != -1 or data.find("A") != -1 or  data.find("E") != -1 or  data.find("D") != -1 or  data.find("C") != -1 or  data.find("H") != -1:
        if data[9: len(data) - 3] != "" and data[0] == "\x02":
            return float(data[9: 15])
    else:
        pass

def cnct2(ip):

    # Requisita os valores das janelas de tempo para cáculo da média móvel
    # COLOCAR TB O VALOR O THRESHOLD LEVEL 01001GL RESPOSTA: (STX)01024GL1234.56:1234.56:1234.56
    # (CS)(CS) (ETX)

    client_socket2.send(format_message("\x0201001MI"))
    data = client_socket2.recv(1024)
    if data.find("K") != -1 or data.find("P") != -1 or data.find("B") != -1 or data.find("A") != -1 or data.find("E") != -1 or data.find("D") != -1 or data.find("C") != -1 or data.find("H") != -1:
        if data[9: len(data) - 3] != "" and data[0] == "\x02":
            return float(data[9: 15])
    else:
        pass

        # Funcao para calcular o delta time para integral

# Thread Principal

while (1):

    try:
        # Delay de 1s
        time.sleep(1)

        # Send the pct for ELSE SATURN
        dataGamma = cnct1(ipGamma)
        r.set('ELSE:Gamma', dataGamma)
        dataNeutron = cnct2(ipNeutron)
        r.set('ELSE:Neutron', dataNeutron)

    except Exception as e:
        print(e)
        logging.error("Error occurred" + str(e))
        pass

