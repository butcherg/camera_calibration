"""
Create a dark current map using dark data (zero light, varying exposure times).
An intermediary map in ADU/s (at this ISO speed) is generated as well as a
calibration map in normalised ADU/s.

An ISO speed normalisation is applied to the data. This means this script
requires an ISO speed look-up table to exist.

Command line arguments:
    * `folder`: folder containing NPY stacks of dark-current data taken at
    different exposure times.

To do:
    * Save maps for all ISOs and use these in the calibration process.
    * Generic filenames, if data are not labelled by ISO.
"""

import numpy as np
from sys import argv
from spectacle import io, calibrate, dark

# Get the data folder from the command line
folder = io.path_from_input(argv)
root = io.find_root_folder(folder)
save_to_normalised = root/"calibration/dark_current_normalised.npy"

# Get the ISO speed at which the data were taken from the folder name
ISO = io.split_iso(folder)
save_to_ADU = root/f"intermediaries/dark_current/dark_current_iso{ISO}.npy"

# Load the data
times, means = io.load_means(folder, retrieve_value=io.split_exposure_time)
print(f"Loaded data at {len(times)} exposure times")

# Fit a linear trend to each pixel
dark_current, bias_fit = dark.fit_dark_current_linear(times, means)
print("Fitted dark current to each pixel")

# Save the dark current map at this ISO
np.save(save_to_ADU, dark_current)
print(f"Saved dark current map at ISO {ISO} to '{save_to_ADU}'")

# ISO normalisation
dark_current_normalised = calibrate.normalise_iso(root, ISO, dark_current)

# Save the normalised dark current map
np.save(save_to_normalised, dark_current_normalised)
print(f"Saved normalised dark current map to '{save_to_normalised}'")
