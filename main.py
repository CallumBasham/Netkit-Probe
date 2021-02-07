import os
from tkinter import *
from tkinter.filedialog import askopenfilename
from lab import NetkitLab

# Program Variables -->-->-->-->-->-->-->-->-->-->
nlab = None

# Overall UI -->-->-->-->-->-->-->-->-->-->
root = Tk()
root.title("Netkit Probe")

# Base frame -->-->-->-->-->-->-->-->-->-->
base = Frame(root, width=1000, height=700)
base.pack()

machineList = Label(base, text="_ ...", anchor=W)
machineList.pack(side=LEFT, fill=X)

# Status bar -->-->-->-->-->-->-->-->-->-->
status = Label(root, text="Waiting...", bd=1, relief=SUNKEN, anchor=W)
status.pack(side=BOTTOM, fill=X)

# Top Menu bar -->-->-->-->-->-->-->-->-->-->
mainMenu = Menu(root)
root.config(menu=mainMenu)


# File Menu -->-->-->-->-->-->-->-->-->-->
# File Menu events
def selectLab(nlab, status):
    print(status)
    status["text"] = "Please select a lab.conf file..."
    nlab = NetkitLab(askopenfilename(filetypes=[("*", "lab.conf")]))
    status["text"] = nlab.labDirectory + " loading..."
    print(nlab.machineList)
    machineList["text"] = nlab.machineList


# File Menu layout
fileMenu = Menu(mainMenu)
mainMenu.add_cascade(label="File", menu=fileMenu)
fileMenu.add_command(label="Load Lab", command=lambda: selectLab(nlab, status))
fileMenu.add_separator()
fileMenu.add_command(label="Quit", command=root.quit)

root.mainloop()
