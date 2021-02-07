import os
import subprocess
import io


class MachineData:
    def __init__(self, name):
        self.machineName = name
        self.machineConnections = []

    def addConnection(self, ethDev, wireName):
        self.machineConnections.append((ethDev, wireName))

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


    def probeLab(self):
        wid = 10
        for i in self.machineList:
            os.system('xdotool search --name "' + i + '"  windowactivate windowmove -- ' + str(
                wid) + '  300 windowsize 450 450 type " ping localhost "')
          #  for x in range(0, 500, 25):
            #    os.system('xdotool search --name "' + i + '"  windowactivate windowsize ' + str(x) + ' ' + str(x) + ' ')
            os.system('xdotool search --name "' + i + '" windowactivate key Return')
            wid = wid + 100

        proc = subprocess.Popen("cd " + self.labDirectory + " && vlist", stdout=subprocess.PIPE, shell=True)
        for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):
            if "@" in line and len(line) > 5:

                newMachine = self.getMachineInfo(line)





    # Constructor
    # Create a NetkitLab class based on a selected lab.conf File
    def __init__(self, labConfFilePath):
        self.labDirectory = os.path.dirname(labConfFilePath)
        self.labConf = labConfFilePath
        self.machineList = self.getMachineList()
