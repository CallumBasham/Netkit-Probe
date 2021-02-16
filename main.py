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

    btnTracePackets = Button(base, name="btnTracePackets", text="Analyse Packets", state=NORMAL, command=lambda: btnAnalysePackets(nlab), anchor=N)
    btnTracePackets.grid(row=1, column=7, columnspan=1)

    btnShowAddressing = Button(base, name="btnShowAddressing", text="Show Addresses", state=NORMAL, command=lambda: btnShowAddress(nlab), anchor=N)
    btnShowAddressing.grid(row=1, column=8, columnspan=1)

    btnPingAll = Button(base, name="btnPingAll", text="Ping All", state=NORMAL,command=lambda: PingAll(nlab), anchor=N)
    btnPingAll.grid(row=1, column=9, columnspan=1)

    machineList["text"] = "Machines: " + str(len(nlab.machineList)) + " at: " + nlab.labDirectory #"#' '.join(nlab.machineList)

def onClose(nlab):
    nlab.stopLab()

def btnStartLab(nlab):
    nlab.startLab()
    updateStatus(nlab.labDirectory + " Lab ready!")
    root.protocol("WM_DELETE_WINDOW", lambda: onClose(nlab))


def btnShowAddress(nlab):
    pass

def PingAll(nlab):
    pin = threading.Thread(target=pingAllThread, args=(nlab, canvasMachines, labCanvas))
    pin.start()


def pingAllThread(nlab, canvasMachines, labCanvas):
    for mach in canvasMachines:
        nlab.moveLabTerminal(mach[1].machineName, -150, -75)
    prev = None
    for machSrc in canvasMachines:
        if prev is not None:
            nlab.moveLabTerminal(prev, -150, -75)
        nlab.moveLabTerminal(machSrc[1].machineName, labCanvas.coords(machSrc[0])[0] + 150, labCanvas.coords(machSrc[0])[1] + 50)
        for machDst in canvasMachines:
            if machDst[1].machineName != machSrc[1].machineName:
                for con in machDst[1].machineConnections:
                    if con[3].find("/") != -1:
                        nlab.pingCommand(machSrc[1].machineName, con[3][0: con[3].index("/"): 1])
                    time.sleep(.001)
                time.sleep(.35)
            time.sleep(1.25)
        prev = machSrc[1].machineName


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

listAnalysisThreads = []
def btnAnalysePackets(nlab):
    updateStatus(nlab.labDirectory + " Analysing packets...")
    btn = base.children["btnTracePackets"]

    if btn["text"] == "Analyse Packets":
        btn["text"] = "Analysing..." # Removed the ability to stop analysis for the time being...

        listAnalysisThreads = []
        for lane in canvasLanes:
            #if lane[1].laneName == "ispB": # TODO - Remove this, for testing only
            listAnalysisThreads.append(threading.Thread(target=spawnPacketAnalysis, args=(nlab, lane[1].laneName)))

        for thread in listAnalysisThreads:
            thread.start()

    else:
        btn["text"] = "Analyse Packets"


def spawnPacketAnalysis(nlab, lane):
    laneProc, stackReader = nlab.beginVdump(lane)

    for pck in stackReader:
        expPck = list(nlab.expandPacket(pck))
        if len(expPck) > 1:
            if expPck[1].name == "IP":
                print(lane + " -> PACKET READ: " + expPck[0].name + ": " + expPck[1].name + ": " + expPck[0].src + " -> " + expPck[0].dst + " ..=.." + expPck[1].src + " -> " + expPck[1].dst)

                for mach in canvasMachines:
                    for con in mach[1].machineConnections:
                        if con[3].find("/") != -1:
                            if con[3][0: con[3].index("/"): 1] == expPck[1].src:
                                pin = threading.Thread(target=chasePacket, args=(expPck, mach, con))
                                pin.start()
                        else:
                            if con[3] == expPck[1].src:
                                pin = threading.Thread(target=chasePacket, args=(expPck, mach, con))
                                pin.start()


            elif expPck[1].name == "ARP":
                print(lane + " -> PACKET READ: " + expPck[0].name + ": " + expPck[1].name + ": " + expPck[0].src + " -> " + expPck[0].dst)
        else:
            print("wtf bro")
        time.sleep(.1)

def chasePacket(packet, srcMachine, connection):

    dstMachine = None
    for mach in canvasMachines:
        for con in mach[1].machineConnections:
            if con[3].find("/") != -1:
                if con[3][0: con[3].index("/"): 1] == packet[1].dst:
                    dstMachine = mach
            else:
                if con[3] == packet[1].src:
                    dstMachine = mach


    textDis = "N/A"

    if packet[2].name:
        textDis = packet[2].name
    elif packet[1].name:
        textDis = packet[1].name
    elif packet[0].name:
        textDis = packet[0].name


    scords = labCanvas.coords(srcMachine[0])
    s = labCanvas.create_text(scords[0] + 35, scords[1] + random.randrange(-30, 30), fill="blue", text=textDis)
    sdeb = threading.Thread(target=debris, args=(s, 4))
    sdeb.start()

    dcords = labCanvas.coords(dstMachine[0])
    d = labCanvas.create_text(dcords[0] - 35, dcords[1] + random.randrange(-30, 30), fill="red", text=textDis)
    ddeb = threading.Thread(target=debris, args=(d, 4))
    ddeb.start()


    for con in srcMachine[1].machineConnections:
        if con[3].find("/") != -1:
            if con[3][0: con[3].index("/"): 1] == packet[1].src:
              for line in canvasLines:
                  if line[2].machineName == srcMachine[1].machineName and line[1][3][0: line[1][3].index("/"): 1] == packet[1].src and line[1][1] == con[1] and line[1][0] == con[0]:
                      orig = labCanvas.itemcget(line[0], "fill")
                      labCanvas.itemconfig(line[0], fill="blue")
                      pin = threading.Thread(target=returnState, args=(line[0], orig, .1))
                      pin.start()


        else:
            if con[3] == packet[1].src:
                print("not now...")

    time.sleep(.05)

    for con in dstMachine[1].machineConnections:
        if con[3].find("/") != -1:
            if con[3][0: con[3].index("/"): 1] == packet[1].dst:
                for line in canvasLines:
                    if line[2].machineName == dstMachine[1].machineName and line[1][3][0: line[1][3].index("/"): 1] == packet[1].dst and line[1][1] == con[1] and line[1][0] == con[0]:
                        orig = labCanvas.itemcget(line[0], "fill")
                        labCanvas.itemconfig(line[0], fill="red")
                        pin = threading.Thread(target=returnState, args=(line[0], orig, .1))
                        pin.start()


        else:
            if con[3] == packet[1].src:
                print("not now...")


    #for i in range(1, 20):
    #    time.sleep(0.1)
    #    scords = labCanvas.coords(s)
    #    labCanvas.coords(s, scords[0] - 1, scords[1] - 1, scords[2] + 1, scords[3] + 1)#

    #    dcords = labCanvas.coords(d)
    #    labCanvas.coords(d, dcords[0] - 1, dcords[1] - 1, dcords[2] + 1, dcords[3] + 1)

def returnState(obj, orig, times):
    time.sleep(times)
    labCanvas.itemconfig(obj, fill=orig)

def debris(obj, times):
    time.sleep(times)
    labCanvas.delete(obj)



labCanvas = Canvas(base2, bg="gray", height=2000)
canvasMachines = []
canvasLanes = []
canvasEths = []
canvasAddrs = []
addressesShown = False
canvasLines = []
canvasBoxes = []
mcData = None
def drawLab(nlab, macineData):
    # Create the Canvas for Writing

    mcData = macineData
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

    wAvaliable = boundW - (boundW / len(lanes))
    xIncriment = wAvaliable / len(lanes)
    lanesDrawn = 1

    #lanes = lanes[len(lanes)%2::2] + lanes[::-2]

    #def sortByWeight(e):
    #    return e.getLaneWeight()

    # Inspired by ...
    #newList = []
    #lanes.sort(key=sortByWeight)
    #newList = lanes[:len(lanes) // 2]

    #newnewlist = lanes[:len(lanes)/2] + list(reversed(lanes[len(lanes)/2:]))

    #lanes.sort(key=sortByWeight, reverse=True)
    #newList = newList + lanes[:len(lanes) // 2]



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

        machConDone = 0
        for con in mach.machineConnections:

            machConDone = machConDone + 1
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
                (labCanvas.create_line(curX, curY, machineCords[0], machineCords[1], fill="yellow", stipple='gray50'), con, mach))
            canvasLines.append(
                (labCanvas.create_line(laneCords[0], laneCords[1], curX, curY, fill="orange"), con, mach))
            canvasBoxes.append(labCanvas.create_rectangle(
                ((machineCords[0] + curX) / 2) - 20,
                ((machineCords[1] + curY) / 2) - 15,
                ((machineCords[0] + curX) / 2) + 20,
                ((machineCords[1] + curY) / 2) + 15, fill="gray", outline=""))
            canvasEths.append((labCanvas.create_text((machineCords[0] + curX)/2, (machineCords[1] + curY)/2, fill="yellow", text=con[0]), con))

            if len(mach.machineConnections) == 1:
                canvasAddrs.append((labCanvas.create_text((machineCords[0] + (machineCords[0] + (machineCords[0] + curX)/2) /2) / 2, (machineCords[1] + (machineCords[1] + (machineCords[1] + curY)/2) / 2) / 2, fill="lightgray", font="Times 10 italic bold", text=con[2] + "\n" + con[3]), con ))
            elif len(mach.machineConnections) >= 2:
                if lnswch == False:
                    canvasAddrs.append((labCanvas.create_text(((machineCords[0] + (machineCords[0] + (machineCords[0] + curX) / 2) / 2) / 2),((machineCords[1] + (machineCords[1] + (machineCords[1] + curY) / 2) / 2) / 2) + (machConDone * 15), fill="lightgray", font="Times 10 italic bold", text=con[2] + "\n" + con[3]), con))
                else:
                    canvasAddrs.append((labCanvas.create_text(((machineCords[0] + (machineCords[0] + (machineCords[0] + curX) / 2) / 2) / 2),((machineCords[1] + (machineCords[1] + (machineCords[1] + curY) / 2) / 2) / 2) - (machConDone * 15), fill="lightgray", font="Times 10 italic bold",text=con[2] + "\n" + con[3]), con))

                machConDone = machConDone + 1
            #labCanvas.create_line(linesDrawn * lineposXIncri, boundH / 2, qx, qy, fill="yellow")
            #####canvasLines.append(labCanvas.create_line(qx, qy, machineCords[0], machineCords[1], fill="yellow"))


    for b in canvasBoxes:
        labCanvas.tag_raise(b)

    for b in canvasLanes:
        labCanvas.tag_raise(b[0])

    for b in canvasEths:
        labCanvas.tag_raise(b[0])

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
