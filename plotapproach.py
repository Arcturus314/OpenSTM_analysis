import matplotlib.pyplot as plt
import sys

print("plotting approach")

approachfilename = sys.argv[1]
outputdir        = sys.argv[2]

approachfile = open(approachfilename, "r")

zlist = []
currlist = []

for line in approachfile:
    if len(line.split(",")) != 2:
        print("ignoring line:",line)
        continue
    zlist.append(float(line.split("\n")[0].split(",")[1]))
    currlist.append(float(line.split(",")[0]))

approachfile.close()

fullscalefilename = outputdir+"/fullapp.png"
smallscalefilename = outputdir+"/endapp.png"
vtimefilename = outputdir+"/endappvtime.png"

plt.xlabel("Z position");
plt.ylabel("Current");

plt.plot(zlist, currlist)
plt.savefig(fullscalefilename)

plt.close()

plt.xlabel("Z position");
plt.ylabel("Current");

plt.plot(zlist[-50:], currlist[-50:])
plt.savefig(smallscalefilename)

plt.close()

plt.xlabel("Time");
plt.ylabel("Current");

plt.plot(currlist[-50:])
plt.savefig(vtimefilename)



