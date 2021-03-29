import matplotlib.pyplot as plt
from scipy.stats import linregress
import scipy.signal
import sys
import math
import copy

# SOS coeffs for band-stop @ 60hz + harmonics
bandstop_sos = [[0.8850438319844021, -1.490969611016647, 0.8850438319844018, 1.0, -1.6748977379966856, 0.9929837887904616], [1.0, -1.6921307027823607, 1.0000000000000002, 1.0, -1.6900200529318468, 0.9931366265425163], [0.8850229805001568, -0.7472044561511129, 0.8850229805001566, 1.0, -0.8349302912513681, 0.993014018007205], [1.0, -0.8569870307803186, 1.0, 1.0, -0.8603478268674766, 0.9930599316807296], [0.8850170846705809, 0.2170263672783544, 0.8850170846705807, 1.0, 0.237373781957078, 0.9930241850473202], [1.0, 0.2591675566376754, 1.0, 1.0, 0.26524021106130957, 0.9930366275384841]]

def filter_manual(ylist, coeffs):
    x0 = 0
    x1 = 0
    y0 = 0
    y1 = 0
    outlist = []
    for el in ylist:
        result = el*coeffs[0] + x0*coeffs[1] + x1*coeffs[2] - y0*coeffs[4] - y1*coeffs[5]
        x1 = x0
        x0 = el
        y1 = y0
        y0 = result

        outlist.append(result)

    return outlist

def filter_mult_sos(ylist, sosmatrix):
    ylist_out = ylist
    for l in sosmatrix:
        ylist_out = filter_manual(copy.deepcopy(ylist_out), l)

    return ylist_out


def gen_sos(freq, order, width, stopdb):

    gpass = 1
    gstop = stopdb

    samplerate = 833
    nyquist = samplerate/2

    wp = [(freq*order-width*2)/nyquist, (freq*order+width*2)/nyquist]
    ws = [(freq*order-width)/nyquist, (freq*order+width)/nyquist]

    print("passband",wp)
    print("stopband",ws)

    systemsos = scipy.signal.iirdesign(wp, ws, gpass, gstop, output='sos')

    print("system")
    print(systemsos)

    systemsos_list = []
    for el in systemsos:
        systemsos_list.append(list(el))


    return systemsos_list

def filter_sos(ylist):

    systemsos = []

    systemsos += gen_sos(66, 1, 0.5, 15)
    systemsos += gen_sos(66, 2, 0.5, 15)
    systemsos += gen_sos(66, 3, 0.5, 15)

    #systemsos.append(gen_sos(66, 1, 0.5, 15)[0])
    #systemsos.append(gen_sos(66, 2, 0.5, 15)[0])
    #systemsos.append(gen_sos(66, 3, 0.5, 15)[0])

    print("total system")
    print(systemsos)


    yvals_f = scipy.signal.sosfilt(systemsos,ylist)
    return yvals_f

filename = sys.argv[1]

scanfile = open(filename)

sampleindex = []
xpos = []
ypos = []
zpos = []
current = []

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

sizeingroup = 40

num_y = int(len(current)/sizeingroup)

for group in range(num_y):
    normfactor = 1/sum(zpos[group*sizeingroup:group*sizeingroup+sizeingroup])
    for i in range(group*sizeingroup, group*sizeingroup+sizeingroup):
        zpos_linenormalized.append(-1*zpos[i]*normfactor)
        print("GROUP",group,"ypos",ypos[i])

current_log = []

for c in current:
    if c > 0: current_log.append(math.log(c))
    else: current_log.append(0)

current_log_filtered = filter_mult_sos(current_log, bandstop_sos)
zpos_linenormalized_filtered = filter_sos(zpos_linenormalized)

# simple FFT and filter experiments
from scipy import fftpack
import numpy as np

fft = False

if fft:

    currfft = fftpack.fft(current_log)
    currfft_filtered = fftpack.fft(current_log_filtered)
    currfreqs = fftpack.fftfreq(len(current_log)) * 833
    
    plt.plot(currfreqs, np.abs(currfft), label="unfiltered", alpha=0.5)
    plt.plot(currfreqs, np.abs(currfft_filtered), label="filtered", alpha=0.5)
    plt.xlabel("frequency")
    plt.legend()
    plt.title("log(current) FFT")
    plt.yscale("log")
    plt.xlim([0,400])
    plt.show()
    
    
    zfft = fftpack.fft(zpos_linenormalized)
    zfft_filtered = fftpack.fft(zpos_linenormalized_filtered)
    zfreqs = fftpack.fftfreq(len(zpos)) * 833
    
    plt.plot(zfreqs, np.abs(zfft), label = "unfiltered", alpha=0.5)
    plt.plot(zfreqs, np.abs(zfft_filtered), label = "filtered", alpha=0.5)
    plt.xlabel("frequency")
    plt.legend()
    plt.title("zpos FFT")
    plt.yscale("log")
    plt.xlim([0,400])
    plt.show()
    
    plt.plot(current_log)
    plt.plot(current_log_filtered)
    plt.xlim([000,1000])
    plt.show()

plotvstime = False

if plotvstime:


    # plotting current over time
    plt.plot(sampleindex, current)
    plt.title("Current over time in 2D scan")
    plt.show()

    # plotting zpos over time
    plt.plot(sampleindex, zpos)
    plt.title("Uncompensated zpos over time in 2D scan")
    plt.show()

    plt.plot(sampleindex, zpos_linearized)
    plt.title("Compensated zpos over time in 2D scan")
    plt.show()

    # plotting currents in 2D

    plt.scatter(xpos, ypos, c=current, s=2)
    plt.title("Current vs position in 2D scan")
    plt.show()

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
    plt.show()

    current_log_scatter = np.array([])

    count = 0

    xblocksize = sizeingroup

    num_blocks = int(len(zpos)/xblocksize)

    for blocki in range(num_blocks):
        print("appending blocki",blocki)
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
    plt.show()

    current_plot = plt.scatter(xpos, ypos, c=current_log, s=9, marker="s")
    plt.title("Log current vs position in 2D scan")
    plt.xlabel("x position (~0.5Å)")
    plt.ylabel("y position (~0.5Å)")
    plt.show()

    #plt.scatter(xpos, ypos, c=current_log_filtered, s=2)
    #plt.title("Log filtered current vs position in 2D scan")
    #plt.show()

    # plotting zpos in 2d

    plt.scatter(xpos, ypos, c=zpos, s=9, marker="s")
    plt.title("Uncompensated zpos vs position in 2D scan")
    plt.show()

    plt.scatter(xpos, ypos, c=zpos_linearized, s=9, marker="s")
    plt.title("Compensated zpos vs position in 2D scan")
    plt.show()

    scatter = plt.scatter(xpos, ypos, c=zpos_linenormalized, s=9, marker="s")
    plt.colorbar(scatter)
    plt.title("Line compensated zpos vs position in 2D scan")
    plt.xlabel("x position (~0.5Å)")
    plt.ylabel("y position (~0.5Å)")
    plt.show()

    #scatter = plt.scatter(xpos[100:], ypos[100:], c=zpos_linenormalized_filtered[100:], s=2)
    #plt.colorbar(scatter)
    #plt.title("Line filtered compensated zpos vs position in 2D scan")
    #plt.xlabel("x position (~0.5Å)")
    #plt.ylabel("y position (~0.5Å)")
    #plt.show()

plot3d = False

if plot3d:
    from mpl_toolkits.mplot3d import Axes3D
    from matplotlib import cm

    fig = plt.figure()
    ax = Axes3D(fig)
    surf = ax.plot_trisurf(xpos, ypos, zpos, cmap=cm.brg)
    plt.title("raw zpos")
    plt.show()

    fig = plt.figure()
    ax = Axes3D(fig)
    surf = ax.plot_trisurf(xpos, ypos, zpos_linearized, cmap=cm.brg)
    plt.title("linearized zpos")
    plt.show()

    fig = plt.figure()
    ax = Axes3D(fig)
    surf = ax.plot_trisurf(xpos, ypos, zpos_linenormalized, cmap=cm.brg)
    plt.title("line normalized zpos")
    plt.show()



plot3d_mayavi = True

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
