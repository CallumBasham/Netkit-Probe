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

    dockTerminalsBtn = Button(base, text="Dock Terminals", state=NORMAL, command=lambda: btnDockTerms(nlab), anchor=N)
    dockTerminalsBtn.grid(row=1, column=5, columnspan=1)

    pinTerminalsBtn = Button(base, name="pinTerminalsBtn", text="Pin Terminals", state=NORMAL, command=lambda: btnPinTerms(nlab), anchor=N)
    pinTerminalsBtn.grid(row=1, column=6, columnspan=1)

    btnAnalysePackets = Button(base, text="Analyse Packets", state=NORMAL, command=lambda: btnAnalysePackets(nlab), anchor=N)
    btnAnalysePackets.grid(row=1, column=7, columnspan=1)

    machineList["text"] = "Machines: " + ' '.join(nlab.machineList)


def btnStartLab(nlab):
    nlab.startLab()
    updateStatus(nlab.labDirectory + " Lab ready!")


def btnStopLab(nlab):
    nlab.stopLab()
    updateStatus(nlab.labDirectory + " Lab cleared!")


def btnProbeLab(nlab):
    updateStatus(nlab.labDirectory + " Probing...")
    drawLab(nlab, nlab.probeLab())

def btnDockTerms(nlab):
    updateStatus(nlab.labDirectory + " Docking...")
    for mach in canvasMachines:
        nlab.moveLabTerminal(mach[1].machineName, labCanvas.coords(mach[0])[0], labCanvas.coords(mach[0])[1] + 50)

def btnPinTerms(nlab):
    updateStatus(nlab.labDirectory + " Pinning...")
    btn = base.children["pinTerminalsBtn"]
    if btn["text"] == "Pin Terminals":
        btn["text"] = "Unpin Terminals"
        # Thread to keep consoles locked
        pin = threading.Thread(target=keepNConsolesFixed, args=(nlab, btn))
        pin.start()
    else:
        btn["text"] = "Pin Terminals"

def btnAnalysePackets(nlab):
    updateStatus(nlab.labDirectory + " Analysing packets...")




labCanvas = Canvas(base2, bg="gray", height=2000)
canvasMachines = []
def drawLab(nlab, macineData):
    # Create the Canvas for Writing

    labCanvas.pack(fill=BOTH, expand=True, anchor=N, side=TOP)

    # Get Bounds
    boundW = base2.winfo_width()
    boundH = base2.winfo_height()

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
    canvasEths = []
    canvasLines = []
    canvasBoxes = []
    wAvaliable = boundW - (boundW / len(lanes))
    xIncriment = wAvaliable / len(lanes)
    lanesDrawn = 1
    for lane in lanes:
        lane.x = lanesDrawn * xIncriment
        lane.y = boundH / 2
        canvasBoxes.append(labCanvas.create_rectangle(
            lane.x - 30,
            lane.y - 20,
            lane.x + 30,
            lane.y + 20, fill="gray", outline=""))
        canvasLanes.append((labCanvas.create_text(lane.x, lane.y, fill="orange", text=lane.laneName), lane))
        lane.calcualteAllAvaliablePoints()
        lanesDrawn = lanesDrawn + 1

    # Sort by machine weight
    def sortFunc(e):
        return e.getNetworkWeight()

    macineData.sort(reverse=True, key=sortFunc)

    wAvaliable = boundW - (boundW / len(macineData))
    xIncriment =  wAvaliable / len(macineData)
    lanesDrawn = 1
    laneSwitch = 150
    lnswch = True
    for mach in macineData:
        canvasBoxes.append(labCanvas.create_rectangle(
            (lanesDrawn * xIncriment) - 30,
            (laneSwitch) - 20,
            (lanesDrawn * xIncriment) + 30,
            (laneSwitch) + 20, fill="gray", outline=""))
        canvasMachines.append(
            (labCanvas.create_text(lanesDrawn * xIncriment, laneSwitch, fill="#9ce036", text=mach.machineName), mach))
        lanesDrawn = lanesDrawn + 1
        if True == lnswch:
            laneSwitch = boundH - 150 + random.randrange(0, 100)
            lnswch = False
        else:
            laneSwitch = 150 - random.randrange(0, 100)
            lnswch = True

        for con in mach.machineConnections:

            currentLane = None
            laneCords = 0
            for clane in canvasLanes:
                if clane[1].laneName == con[1]:
                    laneCords = labCanvas.coords(clane[0])
                    currentLane = clane[1]
                    break

            machineCords = 0
            for cmach in canvasMachines:
                if cmach[1].machineName == mach.machineName:
                    machineCords = labCanvas.coords(cmach[0])
                    break

            #x = ((laneCords[0] + machineCords[0])/2) + random.randrange(-20, 20)
            #y = ((laneCords[1] + machineCords[1])/2) + random.randrange(-20, 20)
            #canvasEths.append(labCanvas.create_text(x, y, fill="yellow", text=con[0] + " - " + mach.machineName))
            #canvasLines.append(labCanvas.create_line(laneCords[0], laneCords[1] ,machineCords[0], machineCords[1], fill="yellow"))

            #ox, oy = laneCords[0], laneCords[1]
            #px, py = laneCords[0] + 100, laneCords[1] + 100

            #qx = ox + math.cos(math.radians((360 / currentLane.laneWeight) * currentLane.radiansUsed)) * (px - ox) - math.sin(math.radians((360 / currentLane.laneWeight) * currentLane.radiansUsed)) * (py - oy)
            #qy = oy + math.sin(math.radians((360 / currentLane.laneWeight) * currentLane.radiansUsed)) * (px - ox) + math.cos(math.radians((360 / currentLane.laneWeight) * currentLane.radiansUsed)) * (py - oy)

            #currentLane.radiansUsed = currentLane.radiansUsed + 1

            #ddd = canvEths.append(labCanvas.create_text(qx, qy, fill="yellow", text=con[0]))
            ####canvasEths.append(labCanvas.create_text(qx, qy, fill="yellow", text=con[0] + " - " + mach.machineName))


            dt = currentLane.getClosestAvaliablePoint(machineCords[0], machineCords[1])
            curX = dt[0]
            curY = dt[1]


            canvasLines.append(
                labCanvas.create_line(curX, curY, machineCords[0], machineCords[1], fill="yellow", stipple='gray50'))
            canvasLines.append(
                labCanvas.create_line(laneCords[0], laneCords[1], curX, curY, fill="orange", stipple='gray50'))
            canvasBoxes.append(labCanvas.create_rectangle(
                ((machineCords[0] + curX) / 2) - 20,
                ((machineCords[1] + curY) / 2) - 15,
                ((machineCords[0] + curX) / 2) + 20,
                ((machineCords[1] + curY) / 2) + 15, fill="gray", outline=""))
            canvasEths.append(labCanvas.create_text((machineCords[0] + curX)/2, (machineCords[1] + curY)/2, fill="yellow", text=con[0]))
            #labCanvas.create_line(linesDrawn * lineposXIncri, boundH / 2, qx, qy, fill="yellow")
            #####canvasLines.append(labCanvas.create_line(qx, qy, machineCords[0], machineCords[1], fill="yellow"))


    for b in canvasBoxes:
        labCanvas.tag_raise(b)

    for b in canvasLanes:
        labCanvas.tag_raise(b[0])

    for b in canvasEths:
        labCanvas.tag_raise(b)

    for b in canvasMachines:
        labCanvas.tag_raise(b[0])


def keepNConsolesFixed(nlab, btn):
    print("PIN STARTED >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    while btn["text"] == "Unpin Terminals":
        for mach in canvasMachines:
            nlab.moveLabTerminal(mach[1].machineName, labCanvas.coords(mach[0])[0], labCanvas.coords(mach[0])[1] + 50)
        time.sleep(.25)
    print("PIN STOPPED >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")


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
