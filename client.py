import socket
import threading

SERVER_IP = "192.168.221.164"
SERVER_PORT=6000
ENCODING='utf-8'
HEADER=64
disconnect_msg="!DISCONNECT"

def connect_to_server():
    client=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client.connect((SERVER_IP,SERVER_PORT))
    print("[CONNECTED] Connected to server !")
    recieveing_thread=threading.Thread(target=recieve_msg,args=(client,))
    sending_thread=threading.Thread(target=send_msg,args=(client,))
    recieveing_thread.start()
    sending_thread.start()


def recieve_msg(client):
    while True:
        msg_length = int(client.recv(HEADER).decode(ENCODING))
        msg = client.recv(msg_length).decode(ENCODING)
        if msg==disconnect_msg:
            print("DISSCONNECTED FROM THE SERVER !")
            client.close()
            return
        print(f"[SERVER] : {msg}")


def send_msg(client):
    while True:
        msg=input("Send Msg : ").encode(ENCODING)
        send_msg_to=input("Send Message to : ").encode(ENCODING)
        send_msg_to=((b' '*(HEADER-len(send_msg_to))))+send_msg_to
        msg_length=((b' '*(HEADER-len(str(len(msg)))))+str(len(msg)).encode(ENCODING))
        client.send(msg_length)
        client.send(msg)
 
connect_to_server()
