from lcapy import f, sqrt
I = 1e-12 * sqrt(250 / f + 1)
ax = (I * 1e12).plot((-1, 4), loglog=True)
ax.grid(True, 'both')
ax.set_ylabel('Noise current density pA$\sqrt{\mathrm{Hz}}$')
ax.set_ylim(0.1, 100)

from matplotlib.pyplot import savefig
savefig(__file__.replace('.py', '.png'), bbox_inches='tight')