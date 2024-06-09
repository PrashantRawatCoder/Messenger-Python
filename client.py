import socket
import threading

SERVER_IP = "192.168.221.164"
SERVER_PORT=6002
ENCODING='utf-8'
HEADER=64
DISCONNECT_CODE="!DISCONNECT"
SEND_BY_CODE='!(SEND_BY)'
SEND_TO_CODE='!(SEND_TO)'
CLIENTS=[]

def connect_to_server():
    client=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client.connect((SERVER_IP,SERVER_PORT))
    print("[CONNECTED] Connected to server !")
    recieveing_thread=threading.Thread(target=recieve_msg,args=(client,))
    sending_thread=threading.Thread(target=send_msg,args=(client,))
    recieveing_thread.start()
    sending_thread.start()


def recieve_msg(client):
    global CLIENTS
    while True:
        msg_length = client.recv(HEADER).decode(ENCODING)
        print(f"[RECIEVED] : {msg_length}")
        if msg_length!='':
            msg_length = int(msg_length)
            msg = client.recv(msg_length).decode(ENCODING)
            print(f"[RECIEVED] : {msg}")
            for add_client in msg.split('/--/'):
                CLIENTS.append((add_client.split("/")))
            print(CLIENTS)
            break
    while True:
        msg_length = int(client.recv(HEADER).decode(ENCODING))
        msg = client.recv(msg_length).decode(ENCODING)
        print("[RECIEVED] : ",msg)
        msg,send_msg_by = msg.split(SEND_BY_CODE)
        if msg==DISCONNECT_CODE:
            print("DISSCONNECTED FROM THE SERVER !")
            client.close()
            return
        print(f"[SERVER] : {msg}")


def send_msg(client):
    while True:
        msg=input("Send Msg : ")
        send_msg_to=input("Send Message to : ")
        msg=(msg+SEND_TO_CODE+send_msg_to).encode(ENCODING)
        msg_length=((b' '*(HEADER-len(str(len(msg)))))+str(len(msg)).encode(ENCODING))
        client.send(msg_length)
        client.send(msg)
 
connect_to_server()

