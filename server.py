import socket
import threading

IP = "192.168.221.164"
PORT=6002
ENCODING='utf-8'
HEADER=64
DISCONNECT_CODE="!(DISCONNECT)"
NEW_CLIENT_CODE= "!(NEW_CLIENT_CONNECTED)"
SEND_BY_CODE='!(SEND_BY)'
SEND_TO_CODE='!(SEND_TO)'
SEND_ALL_CODE='!(SEND_ALL)'

CLIENTS_STR=""
CLIENTS=[["NONE_(DO_NOT_REMOVE)"]]

def start_server():
    server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server.bind((IP,PORT))
    server.listen()
    print("[LISTINING] ........")
    while True:
        client_socket,client_addr=server.accept()
        print(f"[CONNECTED] {client_addr}")
        send_new_client_id(client_socket,client_addr)
        msg_reciever = threading.Thread(target=recieve_msg)
        msg_reciever.start()

def send_new_client_id(client_socket,client_addr):
    global CLIENTS
    global CLIENTS_STR
    client_id=len(CLIENTS)
    CLIENTS.append((client_socket,client_addr[0],client_addr[1],client_id))
    send_msg(client_id,"SERVER",CLIENTS_STR)
    if CLIENTS_STR:
        CLIENTS_STR = CLIENTS_STR+'/--/'
    CLIENTS_STR = CLIENTS_STR + str(client_addr[0])+'/'+str(client_addr[1])+"/"+str(client_id)
    
    for a_client in CLIENTS[1:-1]:
       send_msg(a_client[3],'SERVER',NEW_CLIENT_CODE)
       send_msg(a_client[3],"SERVER",''.join(str(k)+'/' for k in CLIENTS[-1][1:])[:-1])
    #Above line sends message to all clients except new client that (ip of new client/port of new client/id)

def recieve_msg():
    client_socket=CLIENTS[-1][0] #set current client to client that joined recently.
    client_id=CLIENTS[-1][-1] #(recently joined client must be on last of list)
    while True:
        msg_length=client_socket.recv(HEADER)
        if msg_length:
            msg_length = int(msg_length.decode(ENCODING))
            msg = client_socket.recv(msg_length).decode(ENCODING)
            msg,send_msg_to = msg.split(SEND_TO_CODE) #unpack msg and sender_id
            handling_msg=handel_recieved_msg(msg,send_msg_to,client_id)
            if handling_msg==DISCONNECT_CODE:
                return


def handel_recieved_msg(msg,send_msg_to,client_id):
    print(f"[{client_id}] : {msg}")
    print(f"[SEND_TO] : {send_msg_to}")
    if msg==DISCONNECT_CODE:
        send_msg([CLIENTS[client_id-1],],"SERVER" ,msg=DISCONNECT_CODE)#tells client to get disconnected
        print(f"[{client_id}] DISSCONNECTED FROM CLIENT !")
        return DISCONNECT_CODE
    elif send_msg_to==SEND_ALL_CODE:
        for send_to in CLIENTS[1:int(client_id)]+CLIENTS[int(client_id+1):] : send_msg(send_to[3],client_id,msg)
    else :
        for send_to in send_msg_to.split('/') : send_msg(int(send_to),client_id,msg) 

def send_msg(to_send,sender_id,msg):
    print(to_send)
    msg=msg+SEND_BY_CODE+str(sender_id) #prepare message by joinig senderid to it
    msg_length=((b' '*(HEADER-len(str(len(msg)))))+str(len(msg)).encode(ENCODING))
    to_send=int(to_send)
    print(f"[SENDING].......\n[TO] {CLIENTS[to_send]}\n[BY] {sender_id}\n[MSG] {msg}")
    CLIENTS[to_send][0].send(msg_length)
    CLIENTS[to_send][0].send((msg).encode(ENCODING))


start_server()

