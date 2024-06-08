import socket
import threading

IP = "192.168.221.164"
PORT=6000
ENCODING='utf-8'
HEADER=64
disconnect_msg="!DISCONNECT"
CLIENTS=[]

def start_server():
    server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server.bind((IP,PORT))
    server.listen()
    print("[LISTINING] ........")
    global CLIENTS
    while True:
        client_socket,client_ip=server.accept()
        CLIENTS.append((client_socket,client_ip))
        print(f"[CONNECTED] {client_ip}")
        client_handler=threading.Thread(target=recieve_msg,args=(client_ip,client_socket,server))
        client_handler.start()

def recieve_msg(client_ip,client_socket,server):
    while True:
        msg_length=client_socket.recv(HEADER)
        if msg_length:
            msg_length = int(msg_length.decode(ENCODING))
            msg = client_socket.recv(msg_length).decode(ENCODING)
            send_msg_to = client_socket.recv(HEADER).decode(ENCODING)
            if msg==disconnect_msg:
                send_msg(client_socket,client_ip,msg=disconnect_msg)
                print(f"[{client_ip}] DISSCONNECTED FROM CLIENT !")
                server.close()
                return
            print(f"[{client_ip}] : {msg}")
            print(f" send to {send_msg_to}")

def send_msg(client_socket ,client_ip,msg):
    global CLIENTS
    for client in CLIENTS:
        msg_length=((b' '*(HEADER-len(str(len(msg)))))+str(len(msg)).encode(ENCODING))
        client[0].send(msg_length)
        client[0].send(msg.encode(ENCODING))

try:
    start_server()
except Exception as e:
    print(e)

