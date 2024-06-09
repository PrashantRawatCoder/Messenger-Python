import socket
import threading

SERVER_IP = "192.168.221.164"
SERVER_PORT=6002
ENCODING='utf-8'
HEADER=64
DISCONNECT_CODE="!(DISCONNECT)"
SEND_BY_CODE='!(SEND_BY)'
SEND_TO_CODE='!(SEND_TO)'
NEW_CLIENT_CODE= "!(NEW_CLIENT_CONNECTED)"
SEND_ALL_CODE='!(SEND_ALL)'
CLIENTS=[]

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
                    CLIENTS.append(add_client.split("/")) #and ip,port,id are seperated by /
                print(f"List of Already connected clients : {CLIENTS}")
            break
    while True:
        msg_length = int(client.recv(HEADER).decode(ENCODING))
        msg = client.recv(msg_length).decode(ENCODING)
        msg,send_msg_by = msg.split(SEND_BY_CODE)
        if msg==DISCONNECT_CODE:
            print("DISSCONNECTED FROM THE SERVER !")
            client.close()
            exit()
        elif msg==NEW_CLIENT_CODE:
            msg_length = int(client.recv(HEADER).decode(ENCODING))
            msg = client.recv(msg_length).decode(ENCODING)
            msg,send_msg_by = msg.split(SEND_BY_CODE)
            CLIENTS.append(msg.split("/"))
        print(f"[{send_msg_by}] : {msg}")


def msg_sender_thread():
    while True:
        msg=input("Send Msg : ")
        print("Enter id of Client to which you want to send message:")
        print(''.join(f"ID : {a_client[2]} , ADDRESS : {a_client[0]}:{a_client[1]}\n") for a_client in CLIENTS)
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