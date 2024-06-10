import socket
import threading

SERVER_IP = "192.168.131.164"
SERVER_PORT=6016
ENCODING='utf-8'
HEADER=64
DISCONNECT_CODE="!(DISCONNECT)"
SEND_BY_CODE='!(SEND_BY)'
SEND_TO_CODE='!(SEND_TO)'
NEW_CLIENT_CODE= "!(NEW_CLIENT_CONNECTED)"
SEND_ALL_CODE='!(SEND_ALL)'
CLIENTS={}

def connect_to_server():
    global client
    client=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client.connect((SERVER_IP,SERVER_PORT))
    print("[CONNECTED] Connected to server !")
    recieveing_thread=threading.Thread(target=recieve_msg)
    sending_thread=threading.Thread(target=msg_sender_thread)
    recieveing_thread.start()
    sending_thread.start()

def recieve_msg():
    global CLIENTS
    while True: #gets fist msg as list of connected clients and stors that list
        #while loop : because sometime socket sends empty message while connecting(not sure about it)  
        msg_length = client.recv(HEADER).decode(ENCODING)
        if msg_length!='':
            msg_length = int(msg_length)
            msg = client.recv(msg_length).decode(ENCODING)
            msg=msg.split(SEND_BY_CODE)[0] 
            if msg:
                for add_client in msg.split('/--/'): #info of every client is seperated by "/--/"
                    add_client=add_client.split("/")
                    CLIENTS[add_client[2]]=[add_client[0],add_client[1]] #and ip,port,id are seperated by /
                print(f"List of Already connected clients : {CLIENTS}")
            break
    while True:
        msg_length = int(client.recv(HEADER).decode(ENCODING))
        msg = client.recv(msg_length).decode(ENCODING)
        msg,send_msg_by = msg.split(SEND_BY_CODE)

        # Handling recieved message
        if msg==DISCONNECT_CODE:
            if send_msg_by=="SERVER":
                print("DISSCONNECTED FROM THE SERVER !")
                client.close()
                exit()
            else :
                del CLIENTS[send_msg_by]
                print(f'[{send_msg_by}] Disconnected !')

        elif msg==NEW_CLIENT_CODE:
            msg_length = int(client.recv(HEADER).decode(ENCODING))
            msg = client.recv(msg_length).decode(ENCODING)
            msg,send_msg_by = msg.split(SEND_BY_CODE)
            CLIENTS[msg.split('/')[2]]=msg.split('/')[:-1]
        print(f"[{send_msg_by}] : {msg}")
        print("[SEND MSG] : ")


def msg_sender_thread():
    while True:
        msg=input("[SEND MSG ] : \n")
        print("Enter id of Client to which you want to send message:")
        for a_client in CLIENTS:
            print(f"ID : {a_client} , ADDRESS : {CLIENTS[a_client]}\n")
        print("ID : 0 , ADDRESS : TO ALL CLIENTS")
        send_msg_to=input("Send Message to : ")
        send_msg_to=SEND_ALL_CODE if (not send_msg_to) or (send_msg_to=='0') else send_msg_to
        send_msg(msg,send_msg_to)

def send_msg(msg,send_msg_to):
        msg=(msg+SEND_TO_CODE+str(send_msg_to)).encode(ENCODING)
        msg_length=((b' '*(HEADER-len(str(len(msg)))))+str(len(msg)).encode(ENCODING))
        client.send(msg_length)
        client.send(msg)

connect_to_server()