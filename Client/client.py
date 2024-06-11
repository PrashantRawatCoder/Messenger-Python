import socket
import threading
from os import getcwd
import json

with open(getcwd().replace(getcwd().split('/')[-1],'Configuration/config.json'),'r') as config_file:
    config_data=json.load(config_file)
SERVER_IP =config_data["SERVER_IP"]
SERVER_PORT=config_data["SERVER_PORT"]
ENCODING=config_data["ENCODING"]
HEADER=config_data["HEADER"]
SAVE_FILE_PATH=config_data["SAVE_FILE_PATH"] if config_data["SAVE_FILE_PATH"] else getcwd().replace(getcwd().split('/')[-1],'Downloads/')

# CODES
DISCONNECT_CODE=config_data["DISCONNECT_CODE"]
SEND_BY_CODE=config_data["SEND_BY_CODE"]
SEND_TO_CODE=config_data["SEND_TO_CODE"]
NEW_CLIENT_CODE=config_data["NEW_CLIENT_CODE"]
SEND_ALL_CODE=config_data["SEND_ALL_CODE"]
SEND_FILE_CODE=config_data["SEND_FILE_CODE"]

#dict of connected clients , {id:(ip,port)}
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
        elif msg==SEND_FILE_CODE:
            print('[Reciving File]......')
            msg_length = int(client.recv(HEADER).decode(ENCODING))
            file_name = client.recv(msg_length).decode(ENCODING)
            file_name= file_name.split(SEND_BY_CODE)[0]
            msg_length = int(client.recv(HEADER).decode(ENCODING))
            file_data= client.recv(msg_length)
            with open(SAVE_FILE_PATH+file_name,'ab') as file:
                file_data=file.write(file_data)
        print(f"[{send_msg_by}] : {msg}")
        print("[SEND MSG] : ")

def msg_sender_thread():
    while True:
        print(f'Enter : \n {DISCONNECT_CODE} :for getting disconnecting,\n {SEND_FILE_CODE} :for sending file ,\n or just type message you want to send.')
        msg=input("[SEND MSG ] : \n")
        print("Enter id of Client to which you want to send message:")
        for a_client in CLIENTS :  print(f"ID : {a_client} , ADDRESS : {CLIENTS[a_client]}\n")
        print("[ID : 0 , ADDRESS : TO ALL CLIENTS]")
        send_msg_to=input("Send Message to : ")
        send_msg_to=SEND_ALL_CODE if (not send_msg_to) or (send_msg_to=='0') else send_msg_to
        if msg==SEND_FILE_CODE : 
            send_file(input("Enter file Path : "),send_msg_to)
        else :
            send_msg(msg,send_msg_to)

def send_msg(msg,send_msg_to):
        msg=(msg+SEND_TO_CODE+str(send_msg_to)).encode(ENCODING)
        msg_length=((b' '*(HEADER-len(str(len(msg)))))+str(len(msg)).encode(ENCODING))
        client.send(msg_length)
        client.send(msg)

def send_file(file_path,send_msg_to):
    with open(file_path,'rb') as file:
        file_data=file.read()
        file_name=file.name.split('/')[-1]
    send_msg(SEND_FILE_CODE,send_msg_to)
    send_msg(file_name,send_msg_to)
    msg_length=((b' '*(HEADER-len(str(len(file_data)))))+str(len(file_data)).encode(ENCODING))
    client.send(msg_length)
    client.send(file_data)
        
if __name__=='__main__':
    connect_to_server()