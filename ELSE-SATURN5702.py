#!/usr/bin/python
# -*- coding: utf-8 -*-

# Módulo necessário

import redis
import requests
import socket
import sys
import threading
import time
import logging

# Definindo as viaveis

dataGamma = 0.0
dataNeutron = 0.0
dataTotal = 0.0

UDP_PORT = int(sys.argv[1])

r = redis.Redis(host = '10.0.6.48', port = 6379, db = 1)

# Log File for exceptions

logging.basicConfig(filename='app.log',level=logging.INFO)

# Thread Principal

def scanThread():

    # Global Variables
    global dataGamma
    global dataNeutron
    global dataTotal

    # Main Loop

    while (True) :

        try:

            time.sleep(1)

            # Send the pct for ELSE SATURN
            dataGamma = float(r.get('ELSE:Gamma'))

            dataNeutron = float(r.get('ELSE:Neutron'))

            # If receiver void menssage do nothing

            if dataNeutron != None and dataGamma != None:

                dataTotal = dataGamma + dataNeutron

        except Exception as e:
            print(e)
            logging.error("Error occurred" + str(e))
            pass


# Inicializa a Main Thread

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

        if (data == "RAD_E_Gamma?\n" and dataNeutron != None and dataGamma != None):
            answer = "{:.10f}".format(dataGamma)

        elif (data == "RAD_E_Neutron?\n" and dataNeutron != None and dataGamma != None):
            answer = "{:.10f}".format(dataNeutron)

        elif (data == "RAD_E_Total?\n" and dataNeutron != None and dataGamma != None):
            answer = "{:.10f}".format(dataTotal)

        else:
            continue

        answer += "\n"
        udp_server_socket.sendto(answer, address)

        # The end

