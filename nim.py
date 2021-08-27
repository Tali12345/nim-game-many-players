#!/usr/bin/python3
import socket
import sys
import struct
import errno
from select import select


def step_1(soc_client,init_soc_client,number_stepval):
    soc_client.send(struct.pack(">iii", 0,0,0))
    number_stepval[0]=2
    
def step_2(soc_client,init_soc_client,number_stepval):
    abc_bytes=soc_client.recv(struct.calcsize(">iii"))
    if (abc_bytes==b''):
        print("Disconnected from server")
        if init_soc_client:
            soc_client.close()
        number_stepval[0]=7
    else:
        abc = struct.unpack(">iii", abc_bytes)
        print ("Heap A:", abc[0])
        print ("Heap B:", abc[1])
        print ("Heap C:", abc[2])
        number_stepval[0]=3
    
def step_3(soc_client,init_soc_client,number_stepval):    
    data_rec_0_1_2_bytes=soc_client.recv(struct.calcsize(">iii"))
    if (data_rec_0_1_2_bytes==b''):
        print("Disconnected from server")
        if init_soc_client:
            soc_client.close()
        number_stepval[0]=7
    else:
        data_rec_0_1_2=struct.unpack(">iii", data_rec_0_1_2_bytes)[0]
        if data_rec_0_1_2==1 or data_rec_0_1_2==2:
            if data_rec_0_1_2==1:
                print("You win!")
                if init_soc_client:
                    soc_client.close()
                number_stepval[0]=7
            else:
                print("Server win!")
                if init_soc_client:
                    soc_client.close()
                number_stepval[0]=7
        else:
            print("Your turn:")
            number_stepval[0]=6
        
def step_6(number_stepval):
    val=sys.stdin.readline()
    number_stepval[1]=val
    number_stepval[0]=4
    
def step_9(soc_client,init_soc_client,number_stepval):
    val=sys.stdin.readline()
    number_stepval[1]=val
    number_stepval[0]=10
    
def step_10(soc_client,init_soc_client,number_stepval):
    val=number_stepval[1]
    if val=="Q":
        soc_client.send(struct.pack(">iii", 4,4,4)) # Q
        #if init_soc_client:
            #soc_client.close()
        number_stepval[0]=7 
    else:
        soc_client.send(struct.pack(">iii", 4,4,4)) # else
        #if init_soc_client:
            #soc_client.close()
        number_stepval[0]=7

def step_4(soc_client,init_soc_client,number_stepval):
    val=number_stepval[1].split()
    if (val[0]=="Q"):
        soc_client.send(struct.pack(">iii", 4,4,4)) # Q
        #if init_soc_client:
            #soc_client.close()
        number_stepval[0]=7
    else:
        if (len(val)!=2):
            soc_client.send(struct.pack(">iii", 3,3,3)) #Illegal move
        else:
            if ((val[0]!="A")and(val[0]!="B")and(val[0]!="C")and(val[0]!="Q")):
                soc_client.send(struct.pack(">iii", 3,3,3)) #Illegal move
            if val[0]=="A":
                if ((val[1].isdigit()) and (int(val[1])<=1000) and (int(val[1])>=1)):
                    soc_client.send(struct.pack(">iii", 0,int(val[1]),0))
                else:
                    soc_client.send(struct.pack(">iii", 3,3,3)) #Illegal move
            if val[0]=="B":
                if ((val[1].isdigit()) and (int(val[1])<=1000) and (int(val[1])>=1)):
                    soc_client.send(struct.pack(">iii", 1,int(val[1]),0))
                else:
                    soc_client.send(struct.pack(">iii", 3,3,3)) #Illegal move
            if val[0]=="C":
                if ((val[1].isdigit()) and (int(val[1])<=1000) and (int(val[1])>=1)):
                    soc_client.send(struct.pack(">iii", 2,int(val[1]),0))
                else:
                    soc_client.send(struct.pack(">iii", 3,3,3)) #Illegal move
        number_stepval[0]=5
                                    
def step_5(soc_client,init_soc_client,number_stepval):
    data_rec_bytes=soc_client.recv(struct.calcsize(">iii"))
    if (data_rec_bytes==b''):
        print("Disconnected from server")
        if init_soc_client:
            soc_client.close()
        number_stepval[0]=7
    else:
        data_rec=struct.unpack(">iii", data_rec_bytes)[0]
        if (data_rec==0):
            print("Illegal move")
        else:
            print("Move accepted")
        number_stepval[0]=2

def game(soc_client,init_soc_client,number_stepval):
    step_1(soc_client,init_soc_client,number_stepval)
    game_over=False
    while (not game_over):
        step_2(soc_client,init_soc_client,number_stepval)
        step_3(soc_client,init_soc_client,number_stepval)
        step_6(number_stepval)
        step_4(soc_client,init_soc_client,number_stepval)
        step_5(soc_client,init_soc_client,number_stepval)


def main(ip,port):
    number_step=0
    val=""
    number_stepval=[number_step,val]
    init_soc_client=False
    rlist=[]
    wlist=[]
    try:
        soc_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        rlist.append(soc_client)
        wlist.append(soc_client)
        rlist.append(sys.stdin)
        init_soc_client=True
        soc_client.connect((ip, port))
        while (True):
            Readable, Writable, Exceptional=select(rlist, wlist,  [], 10)
            for soc in Readable:
                if soc==sys.stdin:
                    if number_stepval[0]==6:
                        step_6(number_stepval)
                    else:
                        step_9(soc_client,init_soc_client,number_stepval)
                else:
                    if number_stepval[0]==0:
                        msgbytes=soc_client.recv(struct.calcsize(">iii"))
                        if (msgbytes==b''):
                            print("Disconnected from server")
                            if init_soc_client:
                                soc_client.close()
                            number_stepval[0]=7
                        else:
                            msg = struct.unpack(">iii", msgbytes)[0]
                            if (msg==0):
                                print("Now you are playing against the server!")
                                number_stepval[0]=1
                            else:
                                if (msg==1):
                                    print("Waiting to play against the server.")
                                    number_stepval[0]=8
                                else:
                                    print("You are rejected by the server.")
                                    if init_soc_client:
                                        soc_client.close()
                                    exit(0)
                    elif number_stepval[0]==2:
                        step_2(soc,init_soc_client,number_stepval)
                    elif number_stepval[0]==3:
                        step_3(soc,init_soc_client,number_stepval)
                    elif number_stepval[0]==5:
                        step_5(soc,init_soc_client,number_stepval)
                    elif number_stepval[0]==8:
                        is_still_waiting_bytes=soc_client.recv(struct.calcsize(">iii"))
                        if (msgbytes==b''):
                            print("Disconnected from server")
                            if init_soc_client:
                                soc_client.close()
                            number_stepval[0]=7
                        else:
                            is_still_waiting = struct.unpack(">iii", is_still_waiting_bytes)[0]
                            if (is_still_waiting==0):
                                print("Now you are playing against the server!")
                                number_stepval[0]=1
            for soc in Writable:
                if number_stepval[0]==1:
                    step_1(soc,init_soc_client,number_stepval)
                elif number_stepval[0]==4:
                    step_4(soc,init_soc_client,number_stepval)
                elif number_stepval[0]==7:
                    exit(0)
                elif number_stepval[0]==10:
                    step_10(soc_client,init_soc_client,number_stepval)
                    
    except OSError as error:
        if error.errno == errno.ECONNREFUSED:
            print("Disconnected from server")
        else:
            print(error.strerror)
        if init_soc_client:
            soc_client.close()  
    except KeyboardInterrupt:
        if init_soc_client:
            soc_client.close()
        exit(0)


if __name__ == "__main__":
    if (len(sys.argv) == 1): # no parameters
        main("localhost",6444)
    else:
        if (len(sys.argv) ==2): # 1 parameters
            main(sys.argv[1],6444)
        else:
            if (len(sys.argv) ==3): # 2 parameters
                if((int(sys.argv[2])<0) or (int(sys.argv[2])>65535)): # a port is a number between 0 to 65535
                    print("The port number should be a number between 0 to 65535")
                else:
                    main(sys.argv[1],int(sys.argv[2]))
            else:
                print("Too many parameters")