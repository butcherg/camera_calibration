"""
Analyse dark current maps (in normalised ADU/s) generated using the calibration
functions. The dark current is converted from normalised ADU/s to electrons/s
using a gain map.

Command line arguments:
    * `file`: the location of the dark current map to be analysed. This map
    should be an NPY file generated using ../calibration/dark_current.py.
"""


import numpy as np
from sys import argv
from spectacle import io, analyse, calibrate

# Get the data file from the command line
file = io.path_from_input(argv)
root = io.find_root_folder(file)
save_folder = root/f"analysis/dark_current/"

# Get metadata
camera = io.load_metadata(root)

# Load the data
dark_current_normADU = np.load(file)
print("Loaded data")

# Convert the data to photoelectrons per second
dark_current_electrons = calibrate.convert_to_photoelectrons(root, dark_current_normADU)

# Convolve the map with a Gaussian kernel and plot an image of the result
save_to_maps = save_folder/"dark_current_map_electrons.pdf"
camera.plot_gauss_maps(dark_current_electrons, colorbar_label="Dark current (e-/s)", saveto=save_to_maps)
print(f"Saved Gauss map to '{save_to_maps}'")

# Split the data into the RGBG2 filters and make histograms (aggregate and per
# filter)
save_to_histogram = save_folder/"dark_current_histogram_electrons.pdf"
camera.plot_histogram_RGB(dark_current_electrons, xlabel="Dark current (e-/s)", saveto=save_to_histogram)
print(f"Saved RGB histogram to '{save_to_histogram}'")
