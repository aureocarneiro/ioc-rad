#!/usr/bin/python
# -*- coding: utf-8 -*-

# Importando as bibliotecas

import redis
import serial
import socket
import sys
import threading
import datetime
import logging

# Definindo o pino do P9 14 como saída para o osciloscópio

SERIAL_PORT = str(sys.argv[1])

# Log File for exceptions
logging.basicConfig(filename='app.log',level=logging.INFO)

# Funcao para incluir o checksum no pacote

def incluirChecksum(entrada):
    soma = 0
    for elemento in entrada:
        soma += ord(elemento)
    soma = soma % 256
    return(entrada + "{0:02X}".format(soma) + "\x03")

# Thread Principal

serial_interface = serial.Serial(port = "{}".format(SERIAL_PORT),
                                 baudrate = 19200,
                                 bytesize = serial.SEVENBITS,
                                 parity = serial.PARITY_EVEN,
                                 stopbits = serial.STOPBITS_TWO,
                                 timeout = 0.5
                                )

# 01 Gamma ----------- 02 Neutron

r = redis.Redis(host = '10.0.6.48', port = 6379, db = 1)

while (True):
    try:

        pct1 = incluirChecksum("\x07" + "01RM1")

        #print(pct1)

        serial_interface.write(pct1)

        # Lê os oito caracteres enviados Gamma

        dataGamma = serial_interface.read(50)

        # Envia o pacote para a leitura Neutron

        pct2 = incluirChecksum("\x07" + "01RM2")

        #print(pct2)

        serial_interface.write(pct2)

        # Lê os oito caracteres enviados Neutron

        dataNeutron = serial_interface.read(50)

        # Calcula o valor da taxa de dose instantânea (em uSv/h)
        # descobrir como chegam os dados e trata-los
        # condicional caso a mensagem recebida for vazia por problema na sonda o algoritmo nao faz nada

        if dataGamma != "" and dataNeutron != "":
            dataG = float(dataGamma.split(" ")[1])
            dataN = float(dataNeutron.split(" ")[1])
        r.set('THERMO:Gamma', dataG)
        r.set('THERMO:Neutron', dataN)

            
    except Exception as e:
        print(e)
        logging.error("Error occurred" + str(e))
        pass


