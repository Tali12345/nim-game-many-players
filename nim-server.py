#!/usr/bin/python3
import socket
import sys
import struct
import errno
import queue
from select import select


def step_1(conn_sock,init_conn_sock,dic):
    conn_sock.recv(struct.calcsize(">iii"))
    dic[conn_sock][3]=2
    
def step_2(conn_sock,init_conn_sock,dic):
    conn_sock.send(struct.pack(">iii", dic[conn_sock][0],dic[conn_sock][1],dic[conn_sock][2]))
    dic[conn_sock][3]=3
    
def step_3(conn_sock,init_conn_sock,dic):
    winner=dic[conn_sock][4]
    if ((dic[conn_sock][0]==0)and(dic[conn_sock][1]==0)and(dic[conn_sock][2]==0)):
        if (winner=="You"):
            conn_sock.send(struct.pack(">iii", 1,1,1)) #You win!
            if (init_conn_sock):
                conn_sock.close()
            dic[conn_sock][3]=6
        else:
            conn_sock.send(struct.pack(">iii", 2,2,2)) #Server win!
            if (init_conn_sock):
                conn_sock.close()
            dic[conn_sock][3]=6
    else:
        conn_sock.send(struct.pack(">iii", 0,0,0)) #game continue
        dic[conn_sock][3]=4

def step_4(conn_sock,init_conn_sock,dic):
    rec_bytes=conn_sock.recv(struct.calcsize(">iii"))
    if (rec_bytes==b''):
        if (init_conn_sock):
            conn_sock.close()
        dic[conn_sock][3]=6
    else:
        rec=struct.unpack(">iii", rec_bytes)
        dic[conn_sock][5]=rec[0]
        dic[conn_sock][6]=rec[1]
        dic[conn_sock][3]=5
        if (dic[conn_sock][5]==4):
            if init_conn_sock:
                conn_sock.close()
            dic[conn_sock][3]=6

def step_7(conn_sock,init_conn_sock,dic):
    rec_bytes=conn_sock.recv(struct.calcsize(">iii"))
    if (rec_bytes==b''):
        if (init_conn_sock):
            conn_sock.close()
        dic[conn_sock][3]=6
    else:
        rec=struct.unpack(">iii", rec_bytes)[0]
        if (rec==4):
            if init_conn_sock:
                conn_sock.close()
            dic[conn_sock][3]=8

def step_5(conn_sock,init_conn_sock,dic):
    msg1=dic[conn_sock][5]
    num=dic[conn_sock][6]
    if (msg1==0):
        if dic[conn_sock][0]>=int(num):
            conn_sock.send(struct.pack(">iii", 1,1,1)) #Move accepted
            dic[conn_sock][0]=dic[conn_sock][0]-int(num)
        else:
            conn_sock.send(struct.pack(">iii", 0,0,0)) #Illegal move
    if (msg1==1):
        if dic[conn_sock][1]>=int(num):
            conn_sock.send(struct.pack(">iii", 1,1,1)) #Move accepted
            dic[conn_sock][1]=dic[conn_sock][1]-int(num)
        else:
            conn_sock.send(struct.pack(">iii", 0,0,0)) #Illegal move
    if (msg1==2):
        if dic[conn_sock][2]>=int(num):
            conn_sock.send(struct.pack(">iii", 1,1,1)) #Move accepted
            dic[conn_sock][2]=dic[conn_sock][2]-int(num)
        else:
            conn_sock.send(struct.pack(">iii", 0,0,0)) #Illegal move
    if (msg1==3):
        conn_sock.send(struct.pack(">iii", 0,0,0)) #Illegal move
    dic[conn_sock][3]=2
    if ((dic[conn_sock][0]==0)and(dic[conn_sock][1]==0)and(dic[conn_sock][2]==0)):
        dic[conn_sock][4]="You"
    else:
        #server turn
        max_value=max(dic[conn_sock][0:3])
        for i in range (len(dic[conn_sock])):
            if (dic[conn_sock][i]==max_value):
                dic[conn_sock][i]=dic[conn_sock][i]-1
                break

def game(conn_sock,init_conn_sock,dic):
    step_1(conn_sock,init_conn_sock,dic)           
    while (True):
        step_2(conn_sock,init_conn_sock,dic)
        step_3(conn_sock,init_conn_sock,dic)
        step_4(conn_sock,init_conn_sock,dic)
        step_5(conn_sock,init_conn_sock,dic)


def main(a,b,c,numplayers,waitlistsize,port):
    q = queue.Queue()
    init_soc_server=False
    init_conn_sock=False
    dic={}
    players=0
    rlist=[]
    wlist=[]
    try:
        soc_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        rlist.append(soc_server)
        init_soc_server=True
        soc_server.bind(('',port))
        soc_server.listen(10)
        while (True):
            init_conn_sock=False
            Readable, Writable, Exceptional=select(rlist, wlist,  [], 10)
            for conn_sock in Readable:
                if conn_sock==soc_server:
                    (conn_sock,address)=soc_server.accept() #accept won't block
                    init_conn_sock=True
                    rlist.append(conn_sock)
                    wlist.append(conn_sock)
                if (conn_sock!=soc_server):
                    if conn_sock not in dic:
                        dic[conn_sock]=[a,b,c,0,"Server","",0] # 0=number_step winner="Server", ""-msg1 0-num
                    if dic[conn_sock][3]==1:
                        step_1(conn_sock,init_conn_sock,dic)
                    elif dic[conn_sock][3]==4:
                        step_4(conn_sock,init_conn_sock,dic)
                    elif dic[conn_sock][3]==7:
                        step_7(conn_sock,init_conn_sock,dic)
            for conn_sock in Writable:
                if dic[conn_sock][3]==0:
                    if players<numplayers:
                        players=players+1
                        conn_sock.send(struct.pack(">iii", 0,0,0)) #Now you are playing against the server!
                        dic[conn_sock][3]=1
                    else:
                        if (q.qsize()<waitlistsize):
                            q.put(conn_sock)
                            conn_sock.send(struct.pack(">iii", 1,1,1)) #Waiting to play against the server.
                            dic[conn_sock][3]=7
                        else:
                            conn_sock.send(struct.pack(">iii", 2,2,2)) #You are rejected by the server.
                            rlist.remove(conn_sock)
                            wlist.remove(conn_sock)
                            del dic[conn_sock]
                elif dic[conn_sock][3]==2:
                    step_2(conn_sock,init_conn_sock,dic)
                elif dic[conn_sock][3]==3:
                    step_3(conn_sock,init_conn_sock,dic)
                elif dic[conn_sock][3]==5:
                    step_5(conn_sock,init_conn_sock,dic)
                elif dic[conn_sock][3]==6:
                    rlist.remove(conn_sock)
                    wlist.remove(conn_sock)
                    players=players-1
                    del dic[conn_sock]
                    if (q.qsize()!=0):
                        conn_sock=q.get()
                        players=players+1
                        conn_sock.send(struct.pack(">iii", 0,0,0)) #Now you are playing against the server!
                        dic[conn_sock][3]=1
                elif dic[conn_sock][3]==8:
                    rlist.remove(conn_sock)
                    wlist.remove(conn_sock)
                    del dic[conn_sock]
                    q.get(conn_sock)
    except OSError as error:
        if error.errno == errno.ECONNREFUSED:
            print("connection refused")
        else:
            print(error.strerror)
        if init_conn_sock:
            conn_sock.close()
        if init_soc_server:
            soc_server.close()
    except KeyboardInterrupt:
        if init_conn_sock:
            conn_sock.close()
        if init_soc_server:
            soc_server.close()
        exit(0)
            


if __name__ == "__main__":
    if len(sys.argv) < 6:
        print("The program should get 5 numbers")
    else:
        a=int(sys.argv[1])
        b=int(sys.argv[2])
        c=int(sys.argv[3])
        if (len(sys.argv)==6): #no port in the input
            main(a,b,c, int(sys.argv[4]),int(sys.argv[5]),6444)
        if (len(sys.argv)==7):
            if((int(sys.argv[6])<0) or (int(sys.argv[6])>65535)): # a port is a number between 0 to 65535
                print("The port number should be a number between 0 to 65535")
            else:
                main(a,b,c, int(sys.argv[4]),int(sys.argv[5]),int(sys.argv[6]))
        else:
            print("Too many parameters")