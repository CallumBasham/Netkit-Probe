import os
from tkinter import *
from tkinter.filedialog import askopenfilename
from lab import NetkitLab
import threading
import time

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
    labCanvas = Canvas(base2, bg="gray", height=2000)
    #ee.grid(row=2, columnspan=10, sticky="nsew")
    labCanvas.pack(fill=BOTH, expand=True, anchor=N, side=TOP)

    aerc = labCanvas.create_line(50, 50, 150, 150, fill="orange", width=4)

    #base.grid_rowconfigure(0, weight=1)
    #base.grid_columnconfigure(0, weight=1)

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
