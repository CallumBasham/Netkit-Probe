import os
from tkinter import *
from tkinter.filedialog import askopenfilename
from lab import NetkitLab
from lab import LaneData
import threading
import time
import math
import random

# Program Variables -->-->-->-->-->-->-->-->-->-->

# Overall UI -->-->-->-->-->-->-->-->-->-->
root = Tk()
# root.attributes("-fullscreen", True)
root.attributes("-zoomed", True)
root.title("Netkit Probe")

# Base frame -->-->-->-->-->-->-->-->-->-->
base = Frame(root, height=50)
base.pack(fill=X, expand=True, anchor=N, side=TOP)
base2 = Frame(root, height=2000)
base2.pack(fill=BOTH, expand=True, anchor=N, side=TOP)


def addLabButtons(nlab):
    machineList = Label(base, anchor=N)
    machineList.grid(row=1, column=1, columnspan=1)

    startLabBtn = Button(base, text="Start Lab", state=NORMAL, command=lambda: btnStartLab(nlab), anchor=N)
    startLabBtn.grid(row=1, column=2, columnspan=1)

    stopLabBtn = Button(base, text="Stop Lab", state=NORMAL, command=lambda: btnStopLab(nlab), anchor=N)
    stopLabBtn.grid(row=1, column=3, columnspan=1)

    probeLabBtn = Button(base, text="Probe Lab", state=NORMAL, command=lambda: btnProbeLab(nlab), anchor=N)
    probeLabBtn.grid(row=1, column=4, columnspan=1)

    machineList["text"] = "Machines: " + ' '.join(nlab.machineList)


def btnStartLab(nlab):
    nlab.startLab()
    updateStatus(nlab.labDirectory + " Lab ready!")


def btnStopLab(nlab):
    nlab.stopLab()
    updateStatus(nlab.labDirectory + " Lab cleared!")


def btnProbeLab(nlab):
    updateStatus(nlab.labDirectory + " Probing...!")
    drawLab(nlab, nlab.probeLab())


def drawLab(nlab, macineData):
    # Create the Canvas for Writing
    labCanvas = Canvas(base2, bg="gray", height=2000)
    labCanvas.pack(fill=BOTH, expand=True, anchor=N, side=TOP)

    # Get Bounds
    boundW = base2.winfo_width()
    boundH = base2.winfo_height()

    # 1. Get Lanes
    # 2. Find Machines
    # 3. Find crossover between machines and lanes
    # 4. Sort machines into lanes
    # 5. Draw...

    # Filter distinct lanes into list
    # Machine name, weight (todo?)
    lanes = []
    for mach in macineData:
        for con in mach.machineConnections:
            if len(lanes) <= 0:
                lanes.append(LaneData(con[1]))
            else:
                exist = False

                for lane in lanes:
                    if con[1] == lane.laneName:
                        exist = True
                if exist == False:
                    lanes.append(LaneData(con[1]))


    # Give lanes weight and allocated machines (for later sorting)
    for mach in macineData:
        for con in mach.machineConnections:
            for lane in lanes:
                if con[1] == lane.laneName:
                    lane.laneWeight = lane.laneWeight + 1
                    lane.laneMachines.append(mach.machineName)

    # Try and place machines in a good order
    canvasLanes = []
    canvasMachines = []
    canvasEths = []
    canvasLines = []
    wAvaliable = boundW - (boundW / len(lanes))
    xIncriment = wAvaliable / len(lanes)
    lanesDrawn = 1
    for lane in lanes:
        canvasLanes.append((labCanvas.create_text(lanesDrawn * xIncriment, boundH / 2, fill="orange", text=lane.laneName), lane))
        lanesDrawn = lanesDrawn + 1

    # Sort by machine weight
    def sortFunc(e):
        return e.getNetworkWeight()

    macineData.sort(reverse=True, key=sortFunc)

    wAvaliable = boundW - (boundW / len(macineData))
    xIncriment =  wAvaliable / len(macineData)
    lanesDrawn = 1
    laneSwitch = 150
    for mach in macineData:
        canvasMachines.append(
            (labCanvas.create_text(lanesDrawn * xIncriment, laneSwitch, fill="orange", text=mach.machineName), mach))
        lanesDrawn = lanesDrawn + 1
        if laneSwitch == 150:
            laneSwitch = boundH - 150
        else:
            laneSwitch = 150

        for con in mach.machineConnections:

            laneCords = 0
            for clane in canvasLanes:
                if clane[1].laneName == con[1]:
                    laneCords = labCanvas.coords(clane[0])

            machineCords = 0
            for cmach in canvasMachines:
                if cmach[1].machineName == mach.machineName:
                    machineCords = labCanvas.coords(cmach[0])

            x = ((laneCords[0] + machineCords[0])/2) + random.randrange(-20, 20)
            y = ((laneCords[1] + machineCords[1])/2) + random.randrange(-20, 20)
            canvasEths.append(labCanvas.create_text(x, y, fill="yellow", text=con[0] + " - " + mach.machineName))

            # use the radious/orbit method instead as this has collisions
            # perhaps  make a two line system, one like the above code and the other using orbit
            # draw lines between the three points
            # find a way to group them to trace traffic
            # Get netkit sitting on its name perminantly (maybe allow them to move it, but the name remains, when they click it they can redock/see o




    # Draw lines onto canvas
    #canvLines = []
    #canvEths = []

    #boundW_open = boundW - (boundW / len(distinctLine))
    #lineposXIncri = boundW_open / len(distinctLine)
    #linesDrawn = 1
    #for line in distinctLine:
    #    canvLines.append(
    #        (labCanvas.create_text(linesDrawn * lineposXIncri, boundH / 2, fill="orange", text=line), line))

        #rotsComp = 0
        #maxrots = 0
        #for mach in macineData:
        #    for con in mach.machineConnections:
        #        if con[1] == line:
        #            maxrots = maxrots + 1

        #for mach in macineData:
        #    for con in mach.machineConnections:
        #        if con[1] == line:
        #            ox, oy = linesDrawn * lineposXIncri, boundH / 2
        #            px, py = linesDrawn * lineposXIncri + 100, (boundH / 2) + 100

            #        qx = ox + math.cos(math.radians((360 / maxrots) * rotsComp)) * (px - ox) - math.sin(
            #            math.radians((360 / maxrots) * rotsComp)) * (py - oy)
            #        qy = oy + math.sin(math.radians((360 / maxrots) * rotsComp)) * (px - ox) + math.cos(
            #            math.radians((360 / maxrots) * rotsComp)) * (py - oy)

            #        ddd = canvEths.append(labCanvas.create_text(qx, qy, fill="yellow", text=con[0]))
            #        labCanvas.create_line(linesDrawn * lineposXIncri, boundH / 2, qx, qy, fill="yellow")

     #               nlab.moveLabTerminal(mach.machineName, qx, qy + 50)

      #              rotsComp = rotsComp + 1

       # linesDrawn = linesDrawn + 1

    # Thread to keep consoles locked
    pin = threading.Thread(target=keepNConsolesFixed, args=(nlab, macineData))
    pin.start()


def keepNConsolesFixed(nlab, machineData):
    while True:
        nlab.pinConsoleAtPoint("x", 0, 0)
        print("Pinned...")
        time.sleep(1)


# Status bar -->-->-->-->-->-->-->-->-->-->
status = Label(root, text="Waiting...", bd=1, relief=SUNKEN, anchor=W)
status.pack(side=BOTTOM, fill=X)


def updateStatus(value):
    status["text"] = value


# Top Menu bar -->-->-->-->-->-->-->-->-->-->
mainMenu = Menu(root)
root.config(menu=mainMenu)


# File Menu -->-->-->-->-->-->-->-->-->-->
# File Menu events
def selectLab():
    updateStatus("Please select a lab.conf file")
    nlab = NetkitLab(askopenfilename(filetypes=[("*", "lab.conf")]))
    updateStatus(nlab.labDirectory + " loading...")
    addLabButtons(nlab)


# File Menu layout
fileMenu = Menu(mainMenu)
mainMenu.add_cascade(label="File", menu=fileMenu)
fileMenu.add_command(label="Load Lab", command=lambda: selectLab())
fileMenu.add_separator()
fileMenu.add_command(label="Quit", command=root.quit)

root.mainloop()
