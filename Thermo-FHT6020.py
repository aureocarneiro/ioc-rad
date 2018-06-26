#!/usr/bin/python
# -*- coding: utf-8 -*-

# Importando as bibliotecas
import redis
import socket
import sys
import threading
import datetime
import logging
import time

# Definindo o pino do P9 14 como saída para o osciloscópio

dataTotal = 0.0
dataG = 0.0
dataN = 0.0

r = redis.Redis(host = '10.0.6.48', port = 6379, db = 1)

UDP_PORT = int(sys.argv[1])

# Log File for exceptions
logging.basicConfig(filename='app.log',level=logging.INFO)

# Thread Principal

def scanThread():

    # Global Variables

    global dataTotal
    global dataN
    global dataG


    while (True):
        try:
            time.sleep(1)
            dataG = float(r.get('gamma'))
            dataN = float(r.get('neutron'))

            dataTotal = dataG + dataN


        except Exception as e:
            print(e)
            logging.error("Error occurred" + str(e))
            pass

# Exec as threads

auxiliary_thread = threading.Thread(target = scanThread)
auxiliary_thread.setDaemon(True)
auxiliary_thread.start()

# O programa em sua verção final irá dormir 500s para garantir a leitura certa da sonda

udp_server_address = ("0.0.0.0", UDP_PORT)
udp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_server_socket.bind(udp_server_address)

# Loop Principal

while (True):

    # Client (EPICS IOC) input data and address

    data, address = udp_server_socket.recvfrom(512)

    # There is a simple protocol for communication to the client

    if (data):

        if (data == "RAD_G?\n"):
            answer = "{:.10f}".format(dataG)

        elif (data == "RAD_N?\n"):
            answer = "{:.10f}".format(dataN)

        elif (data == "RAD_T?\n"):
            answer = "{:.10f}".format(dataTotal)

        else:
            continue

        answer += "\n"
        udp_server_socket.sendto(answer, address)

