import socket
import sys
import time
import math
import random

commandList = []
#HOST = "codebb.cloudapp.net"
HOST = "localhost"
PORT = 17429

USER = "a"
PASS = "a"

#USER = "GenericTeamName"
#PASS = "f28jiang"

pos = []
vec = []
mines = []
captured = []



class Coord:
    def __init__(self, x, y):
        self.x = x
        self.y = y


def split(str):
    start = 0;
    end = 0;
    newArr = [];
    for c in str:
        if c == " " or not c:
            newArr.append(str[start:end])
            start = end + 1
            end = end + 1
        else:
            end += 1

    return newArr

def dist(x,y, a,b):
    return Coord(float(x) - float(a), float(y) - float(b))

def normalize(dir):
    root = math.sqrt(dir.x * dir.x + dir.y * dir.y)
    return Coord(dir.x/root, dir.y/root)


def run(user, password, * commands):

    data = user + " " + password + "\n" + "\n".join(commands) + "\nCLOSE_CONNECTION\n"
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

        sock.connect((HOST, PORT))
        sock.sendall(bytes(data, "utf-8"))
        sfile = sock.makefile()
        rline = sfile.readline()
        while rline:
            print(rline.strip())
            commandList.append(rline.strip())
            rline = sfile.readline()

def subscribe(user, password):
    HOST, PORT = "codebb.cloudapp.net", 17429
    data = user + " " + password + "\nSUBSCRIBE\n"
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))
        sock.sendall(bytes(data, "utf-8"))
        sfile = sock.makefile()
        rline = sfile.readline()
        while rline:
            print(rline.strip())
            rline = sfile.readline()

def main():
    mineCount = 0

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))
        sock.send(bytes(USER + " " + PASS + "\n", "utf-8"))
        sock.send(bytes("\nCONFIGURATIONS \n", "utf-8"))
        #response = str(sock.recv(4096).decode("utf-8"))
       # print(response)
        response1 = split(sock.recv(4096).decode("utf-8"))
        mapw = response1[2]
        maph = response1[4]
        friction = response1[11]
        breakfriction = response1[13]
        scanradius = response1[23]
        visionradius = response1[8]
        sock.send(bytes("\nACCELERATE 4 1 \n", "utf-8"))
        print(sock.recv(4096).decode("utf-8"))

        tempCount = 0
        while True:
            if tempCount >= 500:
                sock.send(bytes("\nACCELERATE " + str(random.randint(0, 6)) + " 1 \n", "utf-8"))
                print(sock.recv(4096).decode("utf-8"))
                tempCount = 0
            tempCount += 1
            sock.send(bytes("\n STATUS \n", "utf-8"))
            response = str(sock.recv(4096).decode("utf-8"))
            #print(response)
            response = split(response)
            myCoord = Coord(response[1], response[2])
            print("My current location: " + myCoord.x + "," + myCoord.y)
            print (response)
            if int(response[7]) > 0 and response[8] != "a":
                mineCoord = Coord(response[9], response[10])
                mines.append(mineCoord)
                print("Mine Found")

                captured = False;
                #response = str(sock.recv(4096).decode("utf-8"))
                tempCounter = 0
                while not captured:
                    if tempCounter == 3:
                        sock.send(bytes("\nACCELERATE " + str(random.randint(0, 6)) + " 1 \n", "utf-8"))
                        print(sock.recv(4096).decode("utf-8"))
                        mineCount += 1
                        break
                    tempCounter += 1
                    sock.send(bytes("\n BRAKE \n", "utf-8"))
                    time.sleep(7)
                    response = str(sock.recv(4096).decode("utf-8"))
                    print("Looking for mine " + str(mineCount))
                    print(mines[mineCount].x + "," + mines[mineCount].y)
                    sock.send(bytes("\n STATUS \n", "utf-8"))
                    response = split(str(sock.recv(4096).decode("utf-8")))
                    print(response)
                    myCoord.x = float(response[1])
                    myCoord.y = float(response[2])

                    newDir = Coord(float(mines[mineCount].x) - myCoord.x, float(mines[mineCount].y) - myCoord.y)
                    normalized = normalize(newDir)
                    print(str(normalized.x) + "," + str(normalized.y))
                    #newAcc = math.sqrt(normalized.x * normalized.x + normalized.y * normalized.y)
                    newAcc = math.sqrt(newDir.x * newDir.x + newDir.y * newDir.y)
                    print (math.degrees(math.acos(newDir.x / newAcc)))
                    print (str(myCoord.x) + " " + str(myCoord.y) + ", " + str(newDir.x) + " " + str(newDir.y))
                    print(mines[mineCount].x + " " + mines[mineCount].y)
                    if newDir.x >= 0 and newDir.y <= 0:
                        temp = 2 * math.pi - math.acos(newDir.x / newAcc)
                        print("AAAA")
                    elif newDir.x >= 0:
                        temp = math.acos(newDir.x / newAcc)
                        print("CCCC")
                    elif newDir.y <= 0:
                        temp = math.pi/2 + math.acos(newDir.x / newAcc)
                        print("SSSSS")
                    else:
                        temp = math.acos(newDir.x / newAcc)
                        print("TTTTT")
                     
                    if temp > 2 * math.pi:
                        temp -= math.pi
                    elif temp < 0:
                        temp += math.pi
                    print("temp: " + str(temp))

                    sock.send(bytes("\nACCELERATE " + str(temp) + " 0.25 \n", "utf-8"))
                    time.sleep(5)
                    print(sock.recv(4096).decode("utf-8"))
                    time.sleep(4)
                    sock.send(bytes("\n SCAN " + str(mines[mineCount].x) + " " + mines[mineCount].y + " \n", "utf-8"))
                    response = split(str(sock.recv(4096).decode("utf-8")))
                    print (response)
                    if response[4] == "a":
                        captured = True
                        mineCount += 1
                        sock.send(bytes("\nACCELERATE " + str(temp) + " 1 \n", "utf-8"))
                        print(sock.recv(4096).decode("utf-8"))
                        break
main();