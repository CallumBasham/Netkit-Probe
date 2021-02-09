import os
import subprocess
import io

class LaneData:
    def __init__(self, name):
        self.laneName = name
        self.laneWeight = 0
        self.laneMachines = []
        self.radiansUsed = 1




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
        os.system('xdotool search --name "' + termName + '"  windowactivate windowmove -- ' + str(x) + '  ' + str(y) + ' windowsize 100 50')

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

    def pinConsoleAtPoint(self, machineName, pointX, pointY):
        pass

    # Constructor
    # Create a NetkitLab class based on a selected lab.conf File
    def __init__(self, labConfFilePath):
        self.labDirectory = os.path.dirname(labConfFilePath)
        self.labConf = labConfFilePath
        self.machineList = self.getMachineList()
        self.machineData = [] # Populated when user probes the Netkit Lab
