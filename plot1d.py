import matplotlib.pyplot as plt
from scipy.stats import linregress
import scipy.signal
import sys
import math
import copy
from scipy import fftpack
import numpy as np
import statistics

f1 = open("s48b.csv")
f2 = open("s48f.csv")

pos1  = []
curr1 = []
zpos1 = []
pos2  = []
curr2 = []
zpos2 = []

for line in f1:
    pos1.append(float(line.split(",")[0]))
    curr1.append(float(line.split(",")[1]))
    zpos1.append(float(line.split("\n")[0].split(",")[2]))

for line in f2:
    pos2.append(float(line.split(",")[0]))
    curr2.append(float(line.split(",")[1]))
    zpos2.append(float(line.split("\n")[0].split(",")[2]))

# removing linear component to resolve thermal expansion

zpos1_linearized = []
zpos2_linearized = []

zpos1_slope, zpos1_int, r, p, s = linregress(pos1, zpos1)
zpos2_slope, zpos2_int, r, p, s = linregress(pos2, zpos2)

for pos,z in zip(pos1, zpos1): zpos1_linearized.append(z - zpos1_slope*pos - zpos1_int)
for pos,z in zip(pos2, zpos2): zpos2_linearized.append(z - zpos2_slope*pos - zpos2_int)

plt.plot(pos1, curr1, alpha = 0.5, c='b')
plt.plot(pos2, curr2, alpha = 0.5, linestyle = '--', c='r')
plt.title("current")
plt.grid()
plt.show()

plt.plot(pos1, zpos1, alpha = 0.5, c='g')
plt.plot(pos2, zpos2, alpha = 0.5, linestyle = '--', c='orange')
plt.title("Z not corrected for temperature drift")
#plt.xlim([0,400])
plt.grid()
plt.show()

plt.plot(pos1, zpos1_linearized, alpha = 0.5, c='g')
plt.plot(pos2, zpos2_linearized, alpha = 0.5, linestyle = '--', c='orange')
plt.scatter(pos1, zpos1_linearized, alpha = 0.5, c='g')
plt.scatter(pos2, zpos2_linearized, alpha = 0.5, linestyle = '--', c='orange')
plt.title("Z corrected for temperature drift")
#plt.xlim([0,400])
plt.grid()
plt.show()

# 25 samples @ 50us per current readout
# 3 periods in 40 readouts

# so 40/3 * 25 * 50e-6 = 1.7e-2 seconds / period -> exactly 60Hz noise dominates :(


# with new scan...
# 1200us -> 1.2ms / point -> 833Hz scan rate
# 0.01666 sec / 60hz period
# so expect 13.87 points / period if we're seeing 60hz
# this provides ~7 oscillations / 100 points plotted here

# new 12 stage biquad scan
# 600007us / scan (500pts)
# so 1.2ms / point, so same 833Hz scan rate, same conclusion
# see oscillation every 8 points ... so 150nm/volt displacement. I'm stepping x/y/z in increments of ~20/2^16 volts, which gives me a step size of about half an angstrom
#   therefore 4 angstroms per oscillation. About right for gold!

enable_further_analysis = True

if enable_further_analysis:
    scantimeperpoint = 1.2e-3 #1.2ms/point
    scanfreq = 1/scantimeperpoint # in hz
    scandistperpoint = 0.5e-10
    scanspatfreq = 1/scandistperpoint # in 1/m

    print("calculated scanfreq=",scanfreq)
    print("calculated scanspatfreq=",scanspatfreq) # in 1/m

    plt.plot(zpos1_linearized)
    plt.show()

    zpos1fft = fftpack.fft(zpos1_linearized)
    zpos1freqs = fftpack.fftfreq(len(zpos1_linearized))*scanfreq
    zpos1spatfreqs = fftpack.fftfreq(len(zpos1_linearized))*scanspatfreq

    zpos1dists = [1/el for el in zpos1spatfreqs]

    plt.plot(zpos1freqs, np.abs(zpos1fft))
    plt.ylim([1e1,1e5])
    plt.xlim([1,400])
    plt.xlabel("freq (Hz)")
    plt.ylabel("mag (log)")
    plt.yscale('log')
    plt.show()

    plt.plot(zpos1dists, np.abs(zpos1fft))
    plt.title("FFT-inferred spatial periodicity")
    plt.ylim([1e1,1e5])
    plt.xlim([1e-11, 1e-8])
    plt.xlabel("dist (m)")
    plt.ylabel("mag (log)")
    plt.yscale('log')
    plt.xscale('log')
    plt.show()
