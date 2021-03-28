import os

allscandir = "scans"

# setting up file system

if not os.path.exists(allscandir):
    print("creating cumulative scan directory...")
    os.mkdir(allscandir)

scanbasedir = "scans/scan"
scandirindex = 0

scandir = scanbasedir+str(scandirindex)

while os.path.exists(scandir):
    scandirindex += 1
    scandir = scanbasedir+str(scandirindex)

print("creating scan directory",scandir)

os.mkdir(scandir)

# In reality, file parsing will be done with data received over serial. But we don't have that so will instead read from file

scan_stage_dict = {
        "Dumping approach data...": "approachstart",
        "scanning in 2D": "approachstop",
        "scanning in 1D": "approachstop",
        "step,x,y,z,current": "scanstart",
        "Returning","scanstop"
        }

scanstage = "start"
scantype = ""
buf_approach = ""
buf_scan = ""

fname = "log1.csv"

for line in open(fname):



