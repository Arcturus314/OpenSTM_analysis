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


scanfilename     = scandir+"/scan.txt"
approachfilename = scandir+"/approach.txt"
scanbuf     = open(scanfilename,"w")
approachbuf = open(approachfilename,"w")

# In reality, file parsing will be done with data received over serial. But we don't have that so will instead read from file

scan_stage_dict = {
        "Dumping approach data...": "approachstart",
        "scanning in 2D": "approachstop",
        "scanning in 1D": "approachstop",
        "step,x,y,z,current": "scanstart",
        "Returning":"scanstop"
        }

scanstage = "start"
scantype = ""
buf_approach = ""
buf_scan = ""

fname = "prevscans_fulllog/log3.csv"

for line in open(fname):
    # Next state logic: note that we also clear buffers here, as we only care about the last set of data included in the log file

    for key in scan_stage_dict:
        if key in line: # in a state transition
            scanstage = scan_stage_dict[key]
            if key == "approachstart":
                buf_approach = "" # cleaning out data buffers - only care about last scan
            if key == "scanstart":
                buf_scan = "" # cleaning out data buffers - only care about last scan
            continue # as no data, only state transition, on this line

    # Per-state logic
    if scanstage == "start":
        continue
    elif scanstage == "approachstart":
        approachbuf.write(line)
    elif scanstage == "approachstop":
        continue
    elif scanstage == "scanstart":
        scanbuf.write(line)
    elif scanstage == "scanstop":
        break

scanbuf.close()
approachbuf.close()

# now generating plots - we do this through calls to other python scripts which can be executed through the terminal

os.system("python3 plotapproach.py " +approachfilename+" "+scandir)
