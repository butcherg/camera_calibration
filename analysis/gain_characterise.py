"""
Analyse gain maps (in ADU/electron) generated using the calibration functions.

Note: this script currently only looks at raw gain maps (ADU/electron at a
specific ISO speed), not normalised gain maps (normalised ADU/electron).

Command line arguments:
    * `file`: the location of the gain map to be analysed. This should be an
    NPY file generated using ../calibration/gain.py.
"""

import numpy as np
from sys import argv
from matplotlib import pyplot as plt
from spectacle import io, analyse

# Get the data folder from the command line
file = io.path_from_input(argv)
root = io.find_root_folder(file)
savefolder = root/"analysis/gain/"
ISO = io.split_iso(file)

# Get metadata
camera = io.load_metadata(root)
print("Loaded metadata")

# Load the data
gains = np.load(file)
print("Loaded data")

# Plot an RGB histogram of the data
xmin, xmax = 0, analyse.symmetric_percentiles(gains, percent=0.001)[1]
camera.plot_histogram_RGB(gains, xmin=xmin, xmax=xmax, xlabel="Gain (ADU/e$^-$)", saveto=savefolder/f"gain_histogram_iso{ISO}.pdf")
print("Made histogram")

# Plot Gauss-convolved maps of the data
camera.plot_gauss_maps(gains, colorbar_label="Gain (ADU/e$^-$)", saveto=savefolder/f"gain_map_iso{ISO}.pdf")
print("Made maps")

# Demosaick data by splitting the RGBG2 channels into separate arrays
gains_RGBG = camera.demosaick(gains)

# Plot a miniature RGB histogram
fig, axs = plt.subplots(nrows=3, sharex=True, sharey=True, figsize=(3.3,2.4), squeeze=True, tight_layout=True, gridspec_kw={"wspace":0, "hspace":0})
shared_kwargs = {"bins": np.linspace(0, 3.5, 250), "density": True}
axs[0].hist(gains_RGBG[0]   .ravel(), color="r", edgecolor="r", **shared_kwargs)
axs[1].hist(gains_RGBG[1::2].ravel(), color="g", edgecolor="g", **shared_kwargs)
axs[2].hist(gains_RGBG[2]   .ravel(), color="b", edgecolor="b", **shared_kwargs)
for ax in axs[:2]:
    ax.xaxis.set_ticks_position("none")
for ax in axs:
    ax.grid(True)
    ax.set_yticks([0,1,2])
axs[0].set_xlim(0, 3.5)
axs[0].set_ylim(0, 2.5)
axs[2].set_xlabel("Gain (ADU/e-)")
axs[1].set_ylabel("Frequency")
plt.savefig(savefolder/f"gain_histogram_iso{ISO}_rgb_only.pdf")
plt.close()
print("Made RGB histogram")
