import socket
import threading

IP = "192.168.131.164"
PORT=6022
ENCODING='utf-8'
HEADER=128
DISCONNECT_CODE="!(DISCONNECT)"
NEW_CLIENT_CODE= "!(NEW_CLIENT_CONNECTED)"
SEND_BY_CODE='!(SEND_BY)'
SEND_TO_CODE='!(SEND_TO)'
SEND_ALL_CODE='!(SEND_ALL)'
SEND_FILE_CODE="!(SEND_FILE)"

CLIENTS_STR=""
CLIENTS=[["NONE_(DO_NOT_REMOVE)"]]

def start_server():
    global server
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
    
    send_msg(list(range(1,client_id)),'SERVER',NEW_CLIENT_CODE)
    send_msg(list(range(1,client_id)),"SERVER",''.join(str(k)+'/' for k in CLIENTS[-1][1:])[:-1])
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
    global CLIENTS 
    global CLIENTS_STR
    print(f"[{client_id}] : {msg}")
    print(f"[SEND_TO] : {send_msg_to}")
    if msg==DISCONNECT_CODE:
        send_msg(client_id,"SERVER" ,msg=DISCONNECT_CODE)#tells client to get disconnected
        print(f"[{client_id}] DISSCONNECTED FROM CLIENT !")
        disconnecting_client_str=str(CLIENTS[client_id][1])+'/'+str(CLIENTS[client_id][2])+"/"+str(client_id)
        CLIENTS_STR=CLIENTS_STR.replace('/--/'+disconnecting_client_str,'') if client_id!=1 else CLIENTS_STR.replace(disconnecting_client_str+'/--/','')
        CLIENTS[client_id]=DISCONNECT_CODE
        send_msg(SEND_ALL_CODE,client_id,msg)
        return DISCONNECT_CODE
    elif msg==SEND_FILE_CODE:
        send_file(client_id)
    else :
        send_msg(send_msg_to,client_id,msg) 

def send_file(client_id):
    client_socket=CLIENTS[int(client_id)][0]
    msg_length=client_socket.recv(HEADER)
    msg_length = int(msg_length.decode(ENCODING))
    file_name = client_socket.recv(msg_length).decode(ENCODING)
    file_name,send_msg_to = file_name.split(SEND_TO_CODE)
    msg_length=client_socket.recv(HEADER)
    msg_length = int(msg_length.decode(ENCODING))
    file_data = client_socket.recv(msg_length) #file_data
    print("file data recieved............\n\n\n\n\n\n\n")
    send_msg(send_msg_to,client_id,SEND_FILE_CODE)
    send_msg(send_msg_to,client_id,file_name)
    #sending file data :
    #this is copy of send_msg function ,with modification to not encrypt file data 
    to_send_lst=send_msg_to
    msg=file_data
    if isinstance(to_send_lst,str):
        if to_send_lst == SEND_ALL_CODE:
            for a_client in CLIENTS[1:]:
                if a_client!=DISCONNECT_CODE : 
                    msg_length=((b' '*(HEADER-len(str(len(msg)))))+str(len(msg)).encode(ENCODING))
                    to_send=int(a_client[3])
                    CLIENTS[to_send][0].send(msg_length)
                    CLIENTS[to_send][0].send(msg)
        else :
            for a_client in to_send_lst.split('/'): 
                if CLIENTS[int(a_client)]!=DISCONNECT_CODE : 
                    msg_length=((b' '*(HEADER-len(str(len(msg)))))+str(len(msg)).encode(ENCODING))
                    to_send=int(a_client)
                    CLIENTS[to_send][0].send(msg_length)
                    CLIENTS[to_send][0].send(msg)

    elif isinstance(to_send_lst,list):
        for a_client in to_send_lst: 
            if CLIENTS[int(a_client)]!=DISCONNECT_CODE : 
                msg_length=((b' '*(HEADER-len(str(len(msg)))))+str(len(msg)).encode(ENCODING))
                to_send=int(a_client)
                CLIENTS[to_send][0].send(msg_length)
                CLIENTS[to_send][0].send(msg)
    elif isinstance(to_send_lst,int):
        if CLIENTS[to_send_lst]!=DISCONNECT_CODE : 
            msg_length=((b' '*(HEADER-len(str(len(msg)))))+str(len(msg)).encode(ENCODING))
            to_send=to_send_lst
            CLIENTS[to_send][0].send(msg_length)
            CLIENTS[to_send][0].send(msg)



def send_msg(to_send_lst,sender_id,msg):
    if isinstance(to_send_lst,str):
        if to_send_lst == SEND_ALL_CODE:
            for a_client in CLIENTS[1:]:
                if a_client!=DISCONNECT_CODE : msg_sender(a_client[3],sender_id,msg)
        else :
            for a_client in to_send_lst.split('/'): 
                if CLIENTS[int(a_client)]!=DISCONNECT_CODE : msg_sender(a_client,sender_id,msg)
    elif isinstance(to_send_lst,list):
        for a_client in to_send_lst: 
            if CLIENTS[int(a_client)]!=DISCONNECT_CODE : msg_sender(a_client,sender_id,msg)
    elif isinstance(to_send_lst,int):
        if CLIENTS[to_send_lst]!=DISCONNECT_CODE : msg_sender(to_send_lst,sender_id,msg)

def msg_sender(to_send,sender_id,msg):
    msg=msg+SEND_BY_CODE+str(sender_id) #prepare message by joining senderid to it
    msg_length=((b' '*(HEADER-len(str(len(msg)))))+str(len(msg)).encode(ENCODING))
    to_send=int(to_send)
    #print(f"[SENDING].......\n[TO] {CLIENTS[to_send]}\n[BY] {sender_id}\n[MSG] {msg}")
    CLIENTS[to_send][0].send(msg_length)
    CLIENTS[to_send][0].send((msg).encode(ENCODING))


try :
    start_server()
except Exception as e:
    print(e)
finally :
    server.close()

