"""
Determine the spectral response curves of a camera based on data from iSPEX
measurements of sunlight reflected off a white paper.

Please note that this script is not up-to-date with the rest of the SPECTACLE
codebase since it is highly measurement-dependent. For example, the exact
location of the spectrum on the camera is device-dependent.

Consider this script a blueprint for writing your own script to process
spectrometer data.

In better news, a more generic iSPEX processing pipeline will be part of the
new iSPEX release being worked on within the MONOCLE project
(https://monocle-h2020.eu/Home).

This script requires the following additional data:
    * SMARTS2 reference spectrum
    (to be generated by the user based on the conditions when measuring)
    * iSPEX transmission spectrum
    (provided for the 2015 version of iSPEX)
    * iSPEX wavelength calibration coefficients
    (generated using ../to_fork/ispex_calibrate_wavelengths.py)

Command line arguments:
    * `file`: iSPEX spectrum (RAW image)
"""

import numpy as np
from matplotlib import pyplot as plt
from sys import argv
from spectacle import raw, plot, io, wavelength, calibrate
from spectacle.general import blackbody, RMS, gauss1d, curve_fit

# Load the SMARTS2 reference spectrum
wvl, smartsz, smartsy, smartsx = np.loadtxt("reference_spectra/ispex.ext.txt", skiprows=1, unpack=True)

# Normalise the SMARTS2 reference spectrum to its value at 500 nm
smartsx /= smartsx[wvl == 500] ; smartsy /= smartsy[wvl == 500] ; smartsz /= smartsz[wvl == 500]

# Use only the whole wavelengths (for compatibility with other data)
ind = np.where(wvl % 1 == 0)
wvl = wvl[ind]
smartsx = smartsx[ind] ; smartsy = smartsy[ind] ; smartsz = smartsz[ind]

# Smooth the SMARTS2 data
smartsx_smooth = gauss1d(smartsx, 5)

# Generate a normalised blackbody spectrum
BB = blackbody(wvl)
BB /= BB[wvl == 500]

# Plot the blackbody and SMARTS2 spectra for comparison
plt.plot(wvl, BB, c='k', label="Black-body")
plt.plot(wvl, smartsx, c='r', label="SMARTS2 (Diffuse)")
plt.plot(wvl, smartsx_smooth, c='b', label="SMARTS2 (smoothed)")
plt.xlim(390, 700)
plt.legend(loc="best")
plt.savefig(io.results_folder/"SMARTS_vs_BB.pdf")
plt.show()

# Get the data folder from the command line
file = io.path_from_input(argv)
root = io.find_root_folder(file)

# Load the iSPEX wavelength solution
coefficients = wavelength.load_coefficients(root/"intermediaries/spectral_response/ispex_wavelength_solution.npy")

# Load the data
img  = io.load_raw_file(file)
print("Loaded data")

# Bias correction
values = calibrate.correct_bias(root, img.raw_image.astype(np.float32))

# Flat-field correction - note that this clips the image
values = calibrate.correct_flatfield(root, values)

# Spectrum edges
xmin, xmax = 1900, 3500
ymin_thin , ymax_thin  = 450, 800
ymin_thick, ymax_thick = 900, 1220

thin_slit  = np.s_[ymin_thin :ymax_thin , xmin:xmax]
thick_slit = np.s_[ymin_thick:ymax_thick, xmin:xmax]

x = np.arange(xmin, xmax)
y_thin = np.arange(ymin_thin, ymax_thin)
y_thick = np.arange(ymin_thick, ymax_thick)

image_thin   = values        [thin_slit ]
colors_thin  = img.raw_colors[thin_slit ]
RGBG_thin, _ = raw.pull_apart(image_thin, colors_thin)
plot.show_RGBG(RGBG_thin)

image_thick  = values        [thick_slit]
colors_thick = img.raw_colors[thick_slit]
RGBG_thick, _ = raw.pull_apart(image_thick, colors_thick)
plot.show_RGBG(RGBG_thick)

# Extract areas slightly above and below the spectrum for noise removal
above_thin  = np.s_[350:360, xmin:xmax]
below_thick = np.s_[1400:1410, xmin:xmax]

values_above = values[above_thin]
colors_above = img.raw_colors[above_thin]
values_below = values[below_thick]
colors_below = img.raw_colors[below_thick]
RGBG_above,_ = raw.pull_apart(values_above, colors_above)
RGBG_below,_ = raw.pull_apart(values_below, colors_below)
above = RGBG_above.mean(axis=1)
below = RGBG_below.mean(axis=1)

# Subtract noise based on the areas around the spectrum
RGBG_thin -= above[:,np.newaxis,:]
RGBG_thick -= below[:,np.newaxis,:]

# Calculate the wavelength corresponding to each pixel
wavelengths_thin  = wavelength.calculate_wavelengths(coefficients, x, y_thin)
wavelengths_thick = wavelength.calculate_wavelengths(coefficients, x, y_thick)
wavelengths_thin_RGBG , _ = raw.pull_apart(wavelengths_thin , colors_thin )
wavelengths_thick_RGBG, _ = raw.pull_apart(wavelengths_thick, colors_thick)

# Combine the data into a single spectrum per slit
lambdarange, all_interpolated_thin  = wavelength.interpolate_multi(wavelengths_thin_RGBG , RGBG_thin )
lambdarange, all_interpolated_thick = wavelength.interpolate_multi(wavelengths_thick_RGBG, RGBG_thick)

# Create a stack including the wavelengths and RGBG2 data
stacked_thin  = wavelength.stack(lambdarange, all_interpolated_thin )
stacked_thick = wavelength.stack(lambdarange, all_interpolated_thick)

# Normalise the RGBG2 channels to the maximum value in any
stacked_thin [1:] /= stacked_thin [1:].max()
stacked_thick[1:] /= stacked_thick[1:].max()

# Use only the even wavelengths (for compatibility with other data)
ind = np.where(lambdarange % 2 == 0)[0]
stacked_thin  = stacked_thin [:, ind]
stacked_thick = stacked_thick[:, ind]

BB = BB[ind]
smartsx_smooth = smartsx_smooth[ind]
wvl = wvl[ind]

def plot_spectral_response(wavelength, thin_spec, thick_spec, monochromator, title="", saveto=None, label_thin = "narrow_slit", label_thick="broad slit"):
    print(title)
    plt.figure(figsize=(7,3), tight_layout=True)
    for j, c in enumerate("rgb"):
        plt.plot(monochromator[0], monochromator[1+j], c=c)
        plt.plot(wavelength, thin_spec [1+j], c=c, ls="--")
        plt.plot(wavelength, thick_spec[1+j], c=c, ls=":" )
        print(f"{c}: {label_thin}: {RMS(monochromator[1+j] - thin_spec[1+j]):.2f}  ;  {label_thick}: {RMS(monochromator[1+j] - thick_spec[1+j]):.2f}")
    plt.plot([-10], [-10], c='k', label="Monochromator")
    plt.plot([-10], [-10], c='k', ls="--", label=f"iSPEX ({label_thin})")
    plt.plot([-10], [-10], c='k', ls=":" , label=f"iSPEX ({label_thick})")
    if title:
        plt.title(title)
    plt.xlim(390, 700)
    plt.xlabel("Wavelength (nm)")
    plt.ylabel("Relative sensitivity")
    plt.ylim(0, 1.02)
    plt.grid()
    plt.legend(loc="best")
    if saveto is not None:
        plt.savefig(saveto)
    plt.show()
    plt.close()

# Load the monochromator curve for comparison
curves = np.load(root/"intermediaries/spectral_response/monochromator_curve.npy")

plot_spectral_response(wvl, stacked_thin, stacked_thick, curves, "Original", saveto=io.results_folder/"ispex_original.pdf")

BB_thin  = stacked_thin  / BB
BB_thin  /= BB_thin [1:].max()
BB_thick = stacked_thick / BB
BB_thick /= BB_thick[1:].max()

plot_spectral_response(wvl, BB_thin, BB_thick, curves, "Black-body", saveto=io.results_folder/"ispex_black_body.pdf")

SMARTS_thin  = stacked_thin / smartsx_smooth
SMARTS_thin  /= SMARTS_thin [1:].max()
SMARTS_thick = stacked_thick / smartsx_smooth
SMARTS_thick /= SMARTS_thick[1:].max()

plot_spectral_response(wvl, SMARTS_thin, SMARTS_thick, curves, "SMARTS2", saveto=io.results_folder/"ispex_smarts2.pdf")

BB_spec = np.stack([BB_thin, BB_thick]).mean(axis=0)
SMARTS_spec = np.stack([SMARTS_thin, SMARTS_thick]).mean(axis=0)

plot_spectral_response(wvl, SMARTS_spec, BB_spec, curves, title="BB and SMARTS2", label_thin="SMARTS2", label_thick="black-body", saveto=io.results_folder/"ispex_both.pdf")

transwvl, transmission = np.load("reference_spectra/transmission.npy")

BB_trans = BB_spec / transmission
BB_trans = BB_trans / BB_trans[1:].max()
SMARTS_trans = SMARTS_spec / transmission
SMARTS_trans = SMARTS_trans / SMARTS_trans[1:].max()

plot_spectral_response(wvl, SMARTS_trans, BB_trans, curves, title="Transmission corrected", label_thin="SMARTS2", label_thick="black-body", saveto=io.results_folder/"ispex_transmission.pdf")

def fix_trans(profile, factor):
    return profile * factor

SMARTS_factors = np.array([curve_fit(fix_trans, SMARTS_trans[j], curves[j], p0=1)[0] for j in range(1,4)])
SMARTS_factors[1] = 1.
SMARTS_fixed = SMARTS_trans.copy() ; SMARTS_fixed[1:] *= SMARTS_factors
print("SMARTS factors:", SMARTS_factors)
BB_factors = np.array([curve_fit(fix_trans, BB_trans[j], curves[j], p0=1)[0] for j in range(1,4)])
BB_factors[1] = 1.
BB_fixed = BB_trans.copy() ; BB_fixed[1:] *= BB_factors
print("BB factors:", BB_factors)

plot_spectral_response(wvl, SMARTS_fixed, BB_fixed, curves, title="Multiplied by constant", label_thin="SMARTS2", label_thick="black-body", saveto=io.results_folder/"ispex_fixed.pdf")

plot_spectral_response(wvl, SMARTS_trans, BB_trans, curves, label_thin="SMARTS2", label_thick="black-body", saveto=io.results_folder/"spectral_responses_ispex.pdf")
