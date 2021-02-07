import os
from tkinter import *
from tkinter.filedialog import askopenfilename
from lab import NetkitLab

# Program Variables -->-->-->-->-->-->-->-->-->-->

# Overall UI -->-->-->-->-->-->-->-->-->-->
root = Tk()
root.title("Netkit Probe")

# Base frame -->-->-->-->-->-->-->-->-->-->
base = Frame(root, width=1000, height=700)
base.pack()

def addLabButtons(nlab):
    machineList = Label(base, anchor=W)
    machineList.grid(row=1, column=1, columnspan=1)

    startLabBtn = Button(base, text="Start Lab", state=NORMAL, command=nlab.startLab)
    startLabBtn.grid(row=1, column=2, columnspan=1)

    stopLabBtn = Button(base, text="Stop Lab", state=NORMAL, command=nlab.stopLab)
    stopLabBtn.grid(row=1, column=3, columnspan=1)

    probeLabBtn = Button(base, text="Probe Lab", state=NORMAL, command=nlab.probeLab)
    probeLabBtn.grid(row=1, column=4, columnspan=1)

    machineList["text"] = "Machines: " + ' '.join(nlab.machineList)




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
