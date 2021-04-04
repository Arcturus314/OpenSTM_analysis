import matplotlib.pyplot as plt
from scipy.stats import linregress
import scipy.signal
import sys
import math
import copy

print("plotting 2d scan")

filename  = sys.argv[1]
outputdir = sys.argv[2]

scanfile = open(filename)

sampleindex = []
xpos = []
ypos = []
zpos = []
current = []

scanfile.readline()

for line in scanfile:
    linesplit = line.split("\n")[0].split(",")
    sampleindex.append(int(linesplit[0]))
    xpos.append(int(linesplit[1]))
    ypos.append(int(linesplit[2]))
    zpos.append(int(linesplit[3]))
    current.append(int(linesplit[4]))

zpos_linearized = [] # expect ~linear thermal drift in zpos. Correcting for that here.

zpos_slope, zpos_int, r, p, s = linregress(sampleindex, zpos)

for index,z in zip(sampleindex, zpos): zpos_linearized.append(z - zpos_slope*index - zpos_int)

zpos_linenormalized = []

# determining group size. Assume x is the fast scan direction

sizeingroup = ypos.count(0)

num_y = int(len(current)/sizeingroup)

for group in range(num_y):
    normfactor = 1/sum(zpos[group*sizeingroup:group*sizeingroup+sizeingroup])
    for i in range(group*sizeingroup, group*sizeingroup+sizeingroup):
        zpos_linenormalized.append(-1*zpos[i]*normfactor)
        #print("GROUP",group,"ypos",ypos[i])

current_log = []

for c in current:
    if c > 0: current_log.append(math.log(c))
    else: current_log.append(0)

# simple FFT and filter experiments
from scipy import fftpack
import numpy as np

fft = True

if fft:

    currfft = fftpack.fft(current_log)
    currfreqs = fftpack.fftfreq(len(current_log)) * 833 # really want to make this independent of scan freq

    plt.plot(currfreqs, np.abs(currfft), label="unfiltered", alpha=0.5)
    plt.xlabel("frequency")
    plt.legend()
    plt.title("log(current) FFT")
    plt.yscale("log")
    plt.xlim([0,400])
    plt.savefig(outputdir+"/scan_currfft.png")
    plt.close()


    zfft = fftpack.fft(zpos_linenormalized)
    zfreqs = fftpack.fftfreq(len(zpos)) * 833

    plt.plot(zfreqs, np.abs(zfft), label = "unfiltered", alpha=0.5)
    plt.xlabel("frequency")
    plt.legend()
    plt.title("zpos FFT")
    plt.yscale("log")
    plt.xlim([0,400])
    plt.savefig(outputdir+"/scan_zfft.png")
    plt.close()


plotvstime = True

if plotvstime:


    # plotting current over time
    plt.plot(sampleindex, current)
    plt.title("Current over time in 2D scan")
    plt.savefig(outputdir+"/scan_currvtime.png")
    plt.close()

    # plotting zpos over time
    plt.plot(sampleindex, zpos)
    plt.title("Uncompensated zpos over time in 2D scan")
    plt.savefig(outputdir+"/scan_zvtime.png")
    plt.close()

    plt.plot(sampleindex, zpos_linearized)
    plt.title("Compensated zpos over time in 2D scan")
    plt.savefig(outputdir+"/scan_zlinvtime.png")
    plt.close()

    # plotting currents in 2D

    plt.scatter(xpos, ypos, c=current, s=2)
    plt.title("Current vs position in 2D scan")
    plt.savefig(outputdir+"/scan_currents_raw.png")
    plt.close()

plotscatter = True

if plotscatter:

    x_unique = np.unique(np.array(xpos))
    y_unique = np.unique(np.array(ypos))

    x_unique.sort()
    y_unique.sort()
    X, Y = np.meshgrid(x_unique, y_unique)

    z2d_scatter = np.array([])

    count = 0

    xblocksize = sizeingroup

    num_blocks = int(len(zpos)/xblocksize)

    for blocki in range(num_blocks):
        blocklist = zpos_linearized[blocki*xblocksize:(blocki+1)*xblocksize]
        blocklist_scaled = []
        for el in blocklist:
            blocklist_scaled.append(el/500)
        if blocki % 2 == 0:
            if blocki == 0: z2d_scatter = np.array([np.array(blocklist_scaled)])
            else: z2d_scatter = np.append(z2d_scatter, np.array([np.array(blocklist_scaled)]), axis=0)
        else:
            z2d_scatter = np.append(z2d_scatter, np.array([np.array(list(reversed(blocklist_scaled)))]), axis=0)

    z2d_scatter_norm = (z2d_scatter - z2d_scatter.min()) / (z2d_scatter.max() - z2d_scatter.min()) * 255

    z2d_uint8 = z2d_scatter_norm.astype(np.uint8)

    plt.figure()
    plt.imshow(z2d_uint8)
    plt.title("Linearized ZPOS")
    plt.savefig(outputdir+"/zpos_image_2d.png")
    plt.close()

    current_log_scatter = np.array([])

    count = 0

    xblocksize = sizeingroup

    num_blocks = int(len(zpos)/xblocksize)

    for blocki in range(num_blocks):
        #print("appending blocki",blocki)
        blocklist = current[blocki*xblocksize:(blocki+1)*xblocksize]
        blocklist_scaled = []
        for el in blocklist:
            blocklist_scaled.append(el/500)
        if blocki % 2 == 0:
            if blocki == 0: current_log_scatter = np.array([np.array(blocklist_scaled)])
            else: current_log_scatter = np.append(current_log_scatter, np.array([np.array(blocklist_scaled)]), axis=0)
        else:
            current_log_scatter = np.append(current_log_scatter, np.array([np.array(list(reversed(blocklist_scaled)))]), axis=0)

    current_log_scatter_norm = (current_log_scatter - current_log_scatter.min()) / (current_log_scatter.max() - current_log_scatter.min()) * 255

    current_log_uint8 = current_log_scatter_norm.astype(np.uint8)


    plt.figure()
    plt.imshow(current_log_uint8)
    plt.title("Current")
    plt.savefig(outputdir+"/current_image_2d.png")
    plt.close()

    current_plot = plt.scatter(xpos, ypos, c=current_log, s=9, marker="s")
    plt.title("Log current vs position in 2D scan")
    plt.xlabel("x position (~0.5Å)")
    plt.ylabel("y position (~0.5Å)")
    plt.savefig(outputdir+"/current_log_points.png")
    plt.close()

    # plotting zpos in 2d

    plt.scatter(xpos, ypos, c=zpos, s=9, marker="s")
    plt.title("Uncompensated zpos vs position in 2D scan")
    plt.savefig(outputdir+"/zpos_points.png")
    plt.close()

    plt.scatter(xpos, ypos, c=zpos_linearized, s=9, marker="s")
    plt.title("Compensated zpos vs position in 2D scan")
    plt.savefig(outputdir+"/zpos_lin_points.png")
    plt.close()

    scatter = plt.scatter(xpos, ypos, c=zpos_linenormalized, s=9, marker="s")
    plt.colorbar(scatter)
    plt.title("Line compensated zpos vs position in 2D scan")
    plt.xlabel("x position (~0.5Å)")
    plt.ylabel("y position (~0.5Å)")
    plt.savefig(outputdir+"/zpos_linenorm_points.png")
    plt.close()

plot3d = True

if plot3d:
    from mpl_toolkits.mplot3d import Axes3D
    from matplotlib import cm

    fig = plt.figure()
    ax = Axes3D(fig)
    surf = ax.plot_trisurf(xpos, ypos, zpos, cmap=cm.brg)
    plt.title("raw zpos")
    plt.savefig(outputdir+"/zpos_3d.png")
    plt.close()

    fig = plt.figure()
    ax = Axes3D(fig)
    surf = ax.plot_trisurf(xpos, ypos, zpos_linearized, cmap=cm.brg)
    plt.title("linearized zpos")
    plt.savefig(outputdir+"/zpos_lin_3d.png")
    plt.close()

    fig = plt.figure()
    ax = Axes3D(fig)
    surf = ax.plot_trisurf(xpos, ypos, zpos_linenormalized, cmap=cm.brg)
    plt.title("line normalized zpos")
    plt.savefig(outputdir+"/zpos_linenorm_3d.png")
    plt.close()



plot3d_mayavi = False

if plot3d_mayavi:
    from mayavi.mlab import *
    x_unique = np.sort(np.unique(np.array(xpos)))
    y_unique = np.sort(np.unique(np.array(ypos)))

    z2d = []

    count = 0

    xblocksize = sizeingroup

    num_blocks = int(len(zpos)/xblocksize)


    x_list = list(range(xblocksize))
    y_list = list(range(num_blocks))

    for blocki in range(num_blocks):
        blocklist = zpos_linearized[blocki*xblocksize:(blocki+1)*xblocksize]
        blocklist_scaled = []
        for el in blocklist:
            blocklist_scaled.append(el/500)
        if blocki % 2 == 0:
            z2d.append(blocklist_scaled)
        else:
            z2d.append(list(reversed(blocklist_scaled)))

    z2d_smooth = []
    x_smooth = range(1, len(z2d)-1)
    y_smooth = range(1, len(z2d[1])-1)

    for x in x_smooth:
        z2d_smooth.append([])
        for y in y_smooth:
            sumpt = z2d[x][y] + z2d[x+1][y] + z2d[x-1][y] + z2d[x][y+1] + z2d[x][y-1] + z2d[x+1][y+1] + z2d[x-1][y+1] + z2d[x+1][y-1] + z2d[x-1][y-1]
            z2d_smooth[-1].append(sumpt/9)


    #surf(x_list, y_list, z2d, representation='wireframe')
    surf(x_smooth, y_smooth, z2d_smooth, representation='wireframe')
    #points3d(xpos, ypos, zpos_scaled, scale_factor=2)
    show()
