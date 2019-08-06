"""
This script uses the results obtained using the SPECTACLE method and combines
them into a format that can be uploaded to the database.
"""

from sys import argv
import numpy as np
from phonecal import io
from os import makedirs

# Load data
folder = io.path_from_input(argv)
root, images, stacks, products, results = io.folders(folder)
phone = io.read_json(root/"info.json")

# Create results folder
identifier = "-".join([phone["device"]["manufacturer"], phone["device"]["name"], phone["device"]["code"]])
identifier = identifier.replace(" ", "_")
save_folder = root/"spectacle"/identifier

makedirs(save_folder, exist_ok=True)  # create folder if it does not yet exist

# General properties

# Linearity

# Bias

# Read-out noise

# Dark current

# ISO speed normalization

# Gain variations

# Flat-field correction

# Spectral response
fetch_folder = results/"spectral_response"
try:
    spectral_response = np.load(fetch_folder/"monochromator_curve.npy")
except FileNotFoundError:
    print("No spectral response curve found")
    spectral_response = np.tile(np.nan, (9, 156))

spectral_response = spectral_response.T  # transpose to have columns for wavelength, R, G, ...
header = "wavelength (nm),R,G,B,G2,R_error,G_error,B_error,G2_error"

np.savetxt(save_folder/f"spectral_response_{identifier}.csv", spectral_response, delimiter=",", fmt="%.8f", header=header)