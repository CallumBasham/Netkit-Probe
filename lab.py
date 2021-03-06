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

    def getLaneWeight(self):
        return self.laneWeight



class MachineData:
    # Setup a new Machine Object
    def __init__(self, name):
        self.machineName = name
        self.machineConnections = []

    # Append a new connection
    def addConnection(self, ethDev, wireName, macAddr, ipAddr):
        self.machineConnections.append((ethDev, wireName, macAddr, ipAddr))

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

                with open(self.labDirectory + "/" + nk.machineName + ".startup") as f:
                    content = f.readlines()
                content = [x.strip() for x in content]

                mac, ip = "?", "?"

                for line in content:
                    # If this is an ifconfig command
                    if line.find("ifconfig", 0) != -1:
                        # If the line is not commented out
                        if line.find("#", 0, line.find("ifconfig", 0) + 1) == -1:
                            # If the line contains the current ethernet port
                            if line.find(lineSplit[i - 1]) != -1:
                                # This contains the MAC address
                                if line.find(":", line.find("ifconfig", 0)) != -1:
                                    mac = line[
                                          line.index("ether ") + len("ether "):
                                          line.index("ether ") + len("ether ") + 17:
                                          1
                                          ]
                                # This contains the IP address
                                elif line.find(".", line.find("ifconfig", 0)) != -1:
                                    ip = line[
                                         line.index(lineSplit[i - 1] + " ") + len(lineSplit[i - 1] + " "):
                                         line.index(lineSplit[i - 1] + " ") + len(lineSplit[i - 1] + " ") + len(line) - line.index(lineSplit[i - 1] + " ") + len(lineSplit[i - 1] + " "):
                                         1
                                         ].replace(" ", "")




                nk.addConnection(lineSplit[i - 1], lineSplit[i + 1], mac, ip)


        # Return the Machine object
        return nk

    def beginVdumpLab(self):
        pass

    def moveLabTerminal(self, termName, x, y):
        os.system('xdotool search --name "' + termName + '"  windowactivate windowmove -- ' + str(x) + '  ' + str(y) + ' windowsize 250 150')

    def pingCommand(self, termName, pingMachine):
        os.system('xdotool search --name "' + termName + '"  windowactivate key Return')
        os.system('xdotool search --name "' + termName + '"  windowactivate type   "ping -c1 ' + pingMachine + ' "')
        os.system('xdotool search --name "' + termName + '"  windowactivate key Return')


    def probeLab(self):
        # Cleanup any old data
        self.machineData = []
        proc = subprocess.Popen("cd " + self.labDirectory + " && vlist", stdout=subprocess.PIPE, shell=True)
        for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):
            if "@" in line and len(line) > 5:
                self.machineData.append(self.getMachineInfo(line))
        return self.machineData


    def expandPacket(self, x):
        yield x
        while x.payload:
            x = x.payload
            yield x

    def beginVdump(self, lane):

        try:
            os.remove(self.labDirectory + "/" + lane + "-out-dump-NK-Probe.pcap")
        except:
            pass

        proc = subprocess.Popen("cd " + self.labDirectory + " && vdump " + lane + " >> " + lane + "-out-dump-NK-Probe.pcap", shell=True)

        time.sleep(1)

        while os.stat(self.labDirectory + "/" + lane + "-out-dump-NK-Probe.pcap").st_size == 0:
            time.sleep(.05)

        bufferReadPcap = PcapReader(self.labDirectory + "/" + lane + "-out-dump-NK-Probe.pcap")

        def follow(fl):
            while True:
                try:
                    pack = fl.next()
                except:
                    pack = None
                if not pack or pack == None:
                    time.sleep(.005)
                    continue
                yield pack

        capData = follow(bufferReadPcap)

        # region Outdated_Old_Useful_Code
        #    # if IP in test:
        #    # iptest = test[IP]
        #    #    if TCP in test:
        #    #        tcptest = test[TCP]


        # mememe = set((p[IP]) for p in PcapReader("/home/hex/NetkitLabs/CDP/ipsec/ee2.cap") if IP in p)

        # Old Code which reads the VDUMP directly from stdout pipe of the terminal - retired as its too difficult to separate/detect packets
        # proc = subprocess.Popen("cd " + self.labDirectory + " && vdump " + lane, stdout=subprocess.PIPE, shell=True, stderr=subprocess.PIPE, universal_newlines=False)

        # Make the read a non-block
        # fd = proc.stdout.fileno()
        # fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        # fcntl.fcntl(fd, fcntl.F_SETFL, fl |        ree = pck os.O_NONBLOCK)

        # Select means wait until data arrives
        # streams = [proc.stdout]
        # temp0 = []
        # readable, writable, exceptional = select.select(streams, temp0, temp0, 120)
        # if len(readable) == 0:
        #    raise Exception("Timeout of 2 minutes reached!")

        # Read the data into temp [bytearray]
        # temp = bytearray(4096)#bytearray(4096)
        # numberOfBytesRecieved = proc.stdout.readinto(temp)
        # if numberOfBytesRecieved <= 0:
        #    raise Exception("No data recieved!")
        # endregion

        return proc, capData




    # Constructor
    # Create a NetkitLab class based on a selected lab.conf File
    def __init__(self, labConfFilePath):
        self.labDirectory = os.path.dirname(labConfFilePath)
        self.labConf = labConfFilePath
        self.machineList = self.getMachineList()
        self.machineData = [] # Populated when user probes the Netkit Lab
