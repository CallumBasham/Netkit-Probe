import os


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

    # Constructor
    # Create a NetkitLab class based on a selected lab.conf File
    def __init__(self, labConfFilePath):
        self.labDirectory = os.path.dirname(labConfFilePath)
        self.labConf = labConfFilePath
        self.machineList = self.getMachineList()









