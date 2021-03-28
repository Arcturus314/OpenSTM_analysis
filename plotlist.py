import matplotlib.pyplot as plt

f1 = open("l5.csv")
#f2 = open("log_60hzfilter.csv")

curr1 = []
#curr2 = []

for line in f1:
    curr1.append(float(line.split("\n")[0].split(",")[0]))

#for line in f2:
#    curr2.append(float(line.split(",")[1]))

plt.plot(curr1, marker='.')
#plt.plot(curr2)
#plt.xlim([0,100])
plt.grid()
plt.show()

# 25 samples @ 50us per current readout
# 3 periods in 40 readouts

# so 40/3 * 25 * 50e-6 = 1.7e-2 seconds / period -> exactly 60Hz noise dominates :(

