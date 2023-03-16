#!/usr/bin/env python3

'''
Name: CLPI ("Clippy") 
Author: Zachary Bowditch (Edargorter) 
Date: 2020
Description: Command-line (network) packet inspector 
Status: Incomplete

'''

import socket
import json
import urllib.request 
#import urllib3 #Connection pooling, TLS verification and thread safety 
import _thread
import time 
import os
import platform
import subprocess
import random
import sys
import re
import argparse 
import ssl

#Linux command-line editors
EDITORS = ["vim", "vi", "nano", "pico", "emacs"]

#Decoding packets
ENCODING = "utf-8"

#URL Regex pattern
url_reg = "[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)"

CERT_PATH = os.path.join(os.getenv("HOME"))
HOST = "127.0.0.1"
PORT = 4443
EDITOR = "vim"
LOG = False
PRIVATE_KEY_FILE = "clpi_key.pem"
CERTIFICATE_FILE = "clpi_cert.pem"
LOCATE_CMD = "where" if platform.system() == "Windows" else "which"
END_OF_PACKET = b"\r\n\r\n"

parser = argparse.ArgumentParser(description="CLPI - Command-line packet inspector\n")
parser.add_argument("-l", "--log", action="store_true")
parser.add_argument("-p", "--port", metavar="port", type=int, help="Specify listening port")
parser.add_argument("-c", "--cert", metavar="cert", type=str, help="Folder of certificate and private key (.pem files)")
parser.add_argument("-e", "--editor", metavar="editor", type=str, help="Preferred text editor (e.g. vim)")
args = parser.parse_args()

if args.port:
    PORT = args.port
if args.cert:
    CERT_PATH = args.cert
if args.editor:
    EDITOR = args.editor 
if args.log:
    LOG = True

#Display settings
print("""\n
         CCCCCC LL PPPPPP IIIIII
        CC      LL PP  PP   II
        CC      LL PPPPPP   II
        CC      LL PP       II
        CC      LLLLLLLLL IIIIIII
         CCCCCCCCCCCCCCCCCCCCCCCC  By Edargorter\n
        """)
print("[CLPI] Cert folder: {}".format(CERT_PATH))
print("[CLPI] IP: {}".format(HOST))
print("[CLPI] Port: {}".format(PORT))

# open editor if exists (Linux systems)
def edit(filename):
    try:
        devnull = open(os.devnull, 'w')
    except Exception as e:
        devnull = "/tmp/devnull/"
    if subprocess.call([LOCATE_CMD, EDITOR], stdout=devnull, stderr=devnull):
        return False
    os.system("{} {}".format(EDITOR, filename))

def list_packets():
    pass

'''
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(os.path.join(CERT_PATH, CERTIFICATE_FILE), os.path.join(CERT_PATH, PRIVATE_KEY_FILE)) #Might need seperate files for public and private keys 

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
sock.bind((HOST, PORT))
sock.listen(5)
s = context.wrap_socket(sock, server_side=True)
'''
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
s.listen(1)

folder_dir = "/tmp/clpi_requests"
if not os.path.isdir(folder_dir):
    os.mkdir(folder_dir)
file_string = "request_"
packet_id = 0


while 1:
    print("\n[CLPI] Listening...\n")
    conn, addr = s.accept()

    with conn:
        print("============================================")
        print("[CLPI] Connection from: {}".format(addr))
        print("============================================")
        print()
        data = b''

        while 1:
            ddata = conn.recv(4096)
            if not ddata:
                break
            data += bytes(ddata)
            if data[-4:] == END_OF_PACKET:
                break
        #Decode into variable "encoding"
        request = data.decode(ENCODING, errors="ignore")
        print(request)

        #Write request to file 
        f = open(os.path.join(folder_dir, file_string + str(packet_id)), 'w+')
        f.write(request)
        f.close()

        while 1:
            if not LOG:
                cont = input("[CLPI] Forward [f] Edit [e]: ")
                if cont and cont[0] in ["E", "e"]:
                    print("[CLPI] Editing")
                    #Edit packet
                    edit(os.path.join(folder_dir, file_string + str(packet_id)))

                    #Get edited packet
                    f = open(os.path.join(folder_dir, file_string + str(packet_id)), 'r')
                    request = f.read()
                    f.close()
                elif cont and cont[0] in ["F", "f"]:
                    print("[CLPI] Forwarding request")

            try:
                host_index = request.find("Host: ") + 5
                print("HOST: {}".format(host_index))
                end_index = request[host_index:].find('\n') + host_index
                print("END: {}".format(end_index))
                dest = request[host_index:end_index].strip().split(":")
                print("DEST: {}".format(dest))
                dest_url = dest[0]
                print("DEST URL: {}".format(dest_url))
                dest_port = 80
                print("HOST: {}".format(dest_port))
                if len(dest) >= 2:
                    dest_port = int(dest[1])
                print("To: ", dest_url, dest_port)
                break
            except Exception as e:
                print("[CLPI] Incorrect request format.")
                continue

        try:
            #Create socket to communicate with destination server
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((dest_url, dest_port))
            print("\nSending request:")
            print(request)
            client.send(bytes(request, encoding=ENCODING, errors="ignore"))

            data = b'' #Receive from destination server
            print("Reception")
            ddata = client.recv(4096)
            data += ddata
            if ddata:
                while ddata:
                    time.sleep(1)
                    ddata = client.recv(4096)
                    print(data)
                    if data[-4:] == END_OF_PACKET:
                        break
                    data += ddata
            else:
                print("No response from server")
                

            response = data.decode(ENCODING, errors="ignore")
            print("============================================")
            print("[CLPI] Response")
            print("============================================")
            print(response)
            print("============================================")
            
            #Send response back to browser
            conn.send(bytes(response, encoding=ENCODING, errors="ignore"))
        except Exception as e:
            print("Could not connect to destination")
            continue 

        packet_id += 1

client.close()
s.close()
