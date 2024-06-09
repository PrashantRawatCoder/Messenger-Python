import socket
import threading

IP = "192.168.221.164"
PORT=6002
ENCODING='utf-8'
HEADER=64
DISCONNECT_CODE="!DISCONNECT"
NEW_CLINT_CODE= "!(NEW_CLIENT_CONNECTED)"
SEND_BY_CODE='!(SEND_BY)'
SEND_TO_CODE='!(SEND_TO)'
CLIENTS_STR=""
CLIENTS=[]

def start_server():
    server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server.bind((IP,PORT))
    server.listen()
    print("[LISTINING] ........")
    while True:
        client_socket,client_addr=server.accept()
        print(f"[CONNECTED] {client_addr}")
        send_new_client_id(client_socket,client_addr)
        msg_reciever = threading.Thread(target=recieve_msg,args=(server,))
        msg_reciever.start()

def send_new_client_id(client_socket,client_addr):
    global CLIENTS
    CLIENTS.append((client_socket,client_addr[0],client_addr[1],len(CLIENTS)+1))
    if not CLIENTS_STR :
        CLIENTS_STR.join('/--/') 
    CLIENTS_STR.join(str(client_addr[0])+'/'+str(client_addr[1])+"/"+str(len(CLIENTS)+1))
    
    send_msg(CLIENTS[:-1],'SERVER',NEW_CLINT_CODE)
    send_msg(CLIENTS[:-1],"SERVER",''.join(str(k)+'/' for k in CLIENTS[-1][1:])[:-1])
    #Above line sends message to all clients except new client that (ip of new client/port of new client/id)
    send_msg([CLIENTS[-1]],"SERVER",CLIENTS_STR)

def recieve_msg(server):
    client_socket=CLIENTS[-1][0]
    client_id=CLIENTS[-1][-1]
    while True:
        msg_length=client_socket.recv(HEADER)
        if msg_length:
            msg_length = int(msg_length.decode(ENCODING))
            msg = client_socket.recv(msg_length).decode(ENCODING)
            print(msg)
            msg,send_msg_to = msg.split(SEND_TO_CODE)
            if msg==DISCONNECT_CODE:
                send_msg([CLIENTS[client_id-1],],"SERVER" ,msg=DISCONNECT_CODE)
                print(f"[{client_id}] DISSCONNECTED FROM CLIENT !")
                server.close()
                return
            print(f"[{client_id}] : {msg}")
            print(f" send to {send_msg_to}")

def send_msg(CLIENTS_TO_SEND,SEND_BY,msg):
    global CLIENTS
    msg=msg+SEND_BY_CODE+SEND_BY
    for client in CLIENTS_TO_SEND:
        msg_length=((b' '*(HEADER-len(str(len(msg)))))+str(len(msg)).encode(ENCODING))
        print("sending to  ",client)
        client[0].send(msg_length)
        client[0].send((msg).encode(ENCODING))


start_server()

