import os
from tkinter import *
from tkinter.filedialog import askopenfilename
from lab import NetkitLab
import threading
import time
import math

# Program Variables -->-->-->-->-->-->-->-->-->-->

# Overall UI -->-->-->-->-->-->-->-->-->-->
root = Tk()
#root.attributes("-fullscreen", True)
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

    # Get distinct lines
    distinctLine = []
    for mach in macineData:
        for con in mach.machineConnections:
            if con[1] not in distinctLine:
                distinctLine.append(con[1])

    # Draw lines onto canvas
    canvLines = []
    canvEths = []

    boundW_open = boundW - (boundW / len(distinctLine))
    lineposXIncri = boundW_open / len(distinctLine)
    linesDrawn = 1
    for line in distinctLine:
        canvLines.append((labCanvas.create_text(linesDrawn * lineposXIncri, boundH / 2, fill="orange", text=line), line))


        rotsComp = 0
        maxrots = 0
        for mach in macineData:
            for con in mach.machineConnections:
                if con[1] == line:
                    maxrots = maxrots + 1

        for mach in macineData:
            for con in mach.machineConnections:
                if con[1] == line:

                    ox, oy = linesDrawn * lineposXIncri, boundH / 2
                    px, py = linesDrawn * lineposXIncri + 100, (boundH / 2) + 100

                    qx = ox + math.cos( math.radians((360 / maxrots) * rotsComp) ) * (px - ox) - math.sin( math.radians((360 / maxrots) * rotsComp)  ) * (py - oy)
                    qy = oy + math.sin( math.radians((360 / maxrots) * rotsComp) ) * (px - ox) + math.cos(  math.radians((360 / maxrots) * rotsComp)  ) * (py - oy)

                    ddd = canvEths.append(labCanvas.create_text(qx, qy, fill="yellow", text=con[0]))
                    labCanvas.create_line(linesDrawn * lineposXIncri, boundH / 2, qx, qy, fill="yellow")

                    nlab.moveLabTerminal(mach.machineName, qx, qy + 50)

                    rotsComp = rotsComp + 1

        linesDrawn = linesDrawn + 1

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
