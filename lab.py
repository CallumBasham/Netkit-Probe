import os
import subprocess
import io
import math
import random
import fcntl as fcntl
import select as select
from scapy.all import *
import pyshark
from scapy.layers.inet import IP, TCP, ICMP, UDP
from scapy.layers.l2 import ARP


class LaneData:
    def __init__(self, name):
        self.laneName = name
        self.laneWeight = 0
        self.laneMachines = []
        self.radiansUsed = 1

        # Set in main.py
        self.x = 0
        self.y = 0
        # Set by calcualteAllAvaliablePoints
        self.avaliablePoints = []

    def calcualteAllAvaliablePoints(self):
        ox, oy = self.x, self.y
        px, py = ox + 50, oy + 50
        radianQuantity = 12
        if self.laneWeight > 12:
            radianQuantity = self.laneWeight
        for i in range(0, radianQuantity, 1):
            self.avaliablePoints.append((
                    ox + math.cos(math.radians((360 / radianQuantity) * i)) * (px - ox) - math.sin(math.radians((360 / radianQuantity) * i)) * (py - oy),
                    oy + math.sin(math.radians((360 / radianQuantity) * i)) * (px - ox) + math.cos(math.radians((360 / radianQuantity) * i)) * (py - oy),
                    0
            ))
        # Below proves it does not care for anything but the smallest gird number
        #self.avaliablePoints.append((25, 25))

    def getClosestAvaliablePoint(self, _x, _y):

        closest = 50000
        point = None

        for p in self.avaliablePoints:
            pthag = math.sqrt(((_x - p[0]) ** 2) + ((_y - p[1]) ** 2))
            if pthag < closest:
                #if p[2] == 0:
                point = list(p)
                closest = pthag

        #point[0] = point[0] + random.randrange(-40, 40)
        #point[1] = point[1] + random.randrange(-40, 40)
        return point

    def getAllPoints(self):
        return self.avaliablePoints



class MachineData:
    # Setup a new Machine Object
    def __init__(self, name):
        self.machineName = name
        self.machineConnections = []

    # Append a new connection
    def addConnection(self, ethDev, wireName):
        self.machineConnections.append((ethDev, wireName))

    # Info dump to stdout
    def printMachineData(self):
        print("[ " + self.machineName + " ]")
        for con in self.machineConnections:
            print("-> connection -> " + con[0] + " - on line - " + con[1])

    # How many different lanes this machine connets to
    def getNetworkWeight(self):
        dist = []
        for con in self.machineConnections:
            if con[1] not in dist:
                dist.append(con[1])
        return len(dist)

class NetkitLab:

    # Searches the Lab.Conf file for references to the Machines List
    def searchLabConf(self):
        with open(self.labConf, "r") as f:
            searchlines = f.readlines()
        j = len(searchlines) - 1
        for i, line in enumerate(searchlines):
            if "machines=\"" in line.lower() and line.find("#") == -1:
                return line
        return False

    # If the Lab.Conf search fails, the directory will be searched instead
    def searchLabDir(self):
        machineList = []
        for file in os.listdir(self.labDirectory):
            if file.endswith(".startup"):
                machineList.append(file.replace(".startup", ""))
        return machineList

    # Search for the machines list
    # Calls searchLabConf, searchLabDir
    def getMachineList(self):
        machines = self.searchLabConf()
        if machines == False:
            return self.searchLabDir()
        else:
            str = machines.replace("machines=", "").replace("\"", "")
            return str.split(" ")

    def startLab(self):
        os.system('cd ' + self.labDirectory + ' && ~/netkit-jh/bin/lstart')

    def stopLab(self):
        os.system('cd ' + self.labDirectory + ' && lcrash')

    def getMachineInfo(self, line):
        # Dump list into array and clear spaces
        line = line.replace("\n", "").replace(",", "")
        lineSplit = line.split(' ')
        lineSplit = list(filter(None, lineSplit))

        # Create new Machine Object with its Name
        nk = MachineData(lineSplit[1])

        # Browse the string for the Machines networking data
        for i in range(0, len(lineSplit), 1):
            if lineSplit[i] == "@":
                nk.addConnection(lineSplit[i - 1], lineSplit[i + 1])

        # Return the Machine object
        return nk

    def beginVdumpLab(self):
        pass

    def moveLabTerminal(self, termName, x, y):
        os.system('xdotool search --name "' + termName + '"  windowactivate windowmove -- ' + str(x) + '  ' + str(y) + ' windowsize 200 100')


    def probeLab(self):
        # Cleanup any old data
        self.machineData = []

        #wid = 10
        #for i in self.machineList:
         #   os.system('xdotool search --name "' + i + '"  windowactivate windowmove -- ' + str(
         #       wid) + '  300 windowsize 450 450 type " ping localhost "')
         #   os.system('xdotool search --name "' + i + '" windowactivate key Return')
         #   wid = wid + 100

        proc = subprocess.Popen("cd " + self.labDirectory + " && vlist", stdout=subprocess.PIPE, shell=True)
        for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):
            if "@" in line and len(line) > 5:
                self.machineData.append(self.getMachineInfo(line))

        return self.machineData

    def beginVdump(self, lane):


        ee = pyshark.FileCapture("/home/hex/NetkitLabs/CDP/ipsec/ee.cap")

        packets = rdpcap("/home/hex/NetkitLabs/CDP/ipsec/ee.cap")

        eeve = set((p[IP].src, p[IP].dst) for p in PcapReader("/home/hex/NetkitLabs/CDP/ipsec/ee2.cap") if IP in p)


        #mememe = set((p[IP]) for p in PcapReader("/home/hex/NetkitLabs/CDP/ipsec/ee2.cap") if IP in p)

        def expand(x):
            yield x
            while x.payload:
                x = x.payload
                yield x

        for test in PcapReader("/home/hex/NetkitLabs/CDP/ipsec/ee2.cap"):
            original = test
            if IP in test:
                iptest = test[IP]
            if TCP in test:
                tcptest = test[TCP]
            if UDP in test:
                udptest = test[UDP]
            if ICMP in test:
                icmptest = test[ICMP]
            if ARP in test:
                arptest = test[ARP]
            final = list(expand(test))
            print("end")


        print("BEGINNING VDUMP [" + lane + "]>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        proc = subprocess.Popen("cd " + self.labDirectory + " && vdump " + lane, stdout=subprocess.PIPE, shell=True, stderr=subprocess.PIPE, universal_newlines=False)

        #PcapReader()

        fd = proc.stdout.fileno()
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

        streams = [proc.stdout]
        temp0 = []
        readable, writable, exceptional = select.select(streams, temp0, temp0, 120)
        if len(readable) == 0:
            raise Exception("Timeout of 2 minutes reached!")

        temp = bytearray(4096)#bytearray(4096)
        numberOfBytesRecieved = proc.stdout.readinto(temp)
        if numberOfBytesRecieved <= 0:
            raise Exception("No data recieved!")

        for byte in temp:
            print(byte & 1)

        for byte in temp:
            print(byte)

        tst = []
        for b in temp:
            if len(tst) > 5:
                if tst[len(tst) - 1] == 0 and tst[len(tst) - 2] == 0 and tst[len(tst) - 3] == 0 and tst[len(tst) - 4] == 0 and tst[len(tst) - 5] == 0:
                    tst.append(b)
            else:
                tst.append(b)

        bitlist = [byte & 1 for byte in temp]

        f = open("/home/hex/NetkitLabs/CDP/ipsec/ee2-420.cap", "wb")
        f.write(temp)
        f.close()

        #packets = rdpcap(temp)
        packet = Packet(temp)
        packet.show()
        v = packet.name

        final = list(expand(packet))


        #packet.show_summary()



        cap = pyshark.InMemCapture()
        #cap.parse_packets([byte for byte in temp])
        cap.parse_packets([byte & 1 for byte in temp])

        #cap.parse_packets(bitlist)
        #cap.parse_packets()

        var = ""


    # Constructor
    # Create a NetkitLab class based on a selected lab.conf File
    def __init__(self, labConfFilePath):
        self.labDirectory = os.path.dirname(labConfFilePath)
        self.labConf = labConfFilePath
        self.machineList = self.getMachineList()
        self.machineData = [] # Populated when user probes the Netkit Lab
