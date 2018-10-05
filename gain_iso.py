import numpy as np
from sys import argv
from matplotlib import pyplot as plt
from phonecal import raw, plot, io
from phonecal.general import bin_centers, weighted_mean, Rsquare
from glob import glob
from scipy.optimize import curve_fit

folder_main = argv[1]
folders = glob(folder_main+"/*iso*")
isos = np.tile(np.nan, len(folders))
gains = isos.copy()
gainerrs = gains.copy()
RONs = gains.copy()
RONerrs = RONs.copy()

for i,folder in enumerate(folders):
    isos[i] = int(folder.split("iso")[-1])
    try:
        gains[i], gainerrs[i], RONs[i], RONerrs[i] = np.load(folder+"/gain_ron.npy")
    except FileNotFoundError:
        continue

invgains = 1/gains
invgainerrs = invgains**2 * gainerrs

def model(iso, slope, offset, knee):
    iso2 = np.copy(iso)
    results = np.tile(knee * slope + offset, len(iso2))
    results[iso2 < knee] = iso2[iso2 < knee] * slope + offset
    return results

def model_err(iso, popt, pcov):
    iso2 = np.copy(iso)
    results = np.tile(popt[2]**2 * pcov[0,0] + popt[0]**2 * pcov[2,2] + pcov[1,1], len(iso2))
    results[iso2 < popt[2]] = iso2[iso2 < popt[2]]**2 * pcov[0,0] + pcov[1,1]
    results = np.sqrt(results)
    return results

ind = np.where(~np.isnan(gains))
popt, pcov = curve_fit(model, isos[ind], invgains[ind], p0=[0.1, 0.1, 200], sigma=invgainerrs[ind])

irange = np.arange(0, 1850, 3)
invgain_fit = model(irange, *popt)
err_fit = model_err(irange, popt, pcov)
gain_fit = 1/invgain_fit
gain_err_fit = err_fit / invgain_fit**2

fit_measured = model(isos, *popt)
R2 = Rsquare(invgains[ind], fit_measured[ind])

invRONs = invgains * RONs
invRONerrs = np.sqrt(invgains**2 * RONerrs**2 + RONs**2 * invgainerrs**2)

LUT_iso = np.arange(0, 2000, 1)
LUT_invgain = model(LUT_iso, *popt)
LUT_invgain_err = model_err(LUT_iso, popt, pcov)
LUT_gain = 1/LUT_invgain
LUT_gain_err = LUT_invgain_err
LUT = np.stack([LUT_iso, LUT_gain, LUT_gain_err])
np.save("results/gain_new/LUT.npy", LUT)

for xmax in (1850, 250):
    plt.figure(figsize=(7,5), tight_layout=True)
    plt.errorbar(isos, invgains, yerr=invgainerrs, fmt="o", c="k")
    plt.plot(irange, invgain_fit, c="k", label=f"slope: {popt[0]:.4f}\noffset: {popt[1]:.4f}\nknee: {popt[2]:.1f}")
    plt.fill_between(irange, invgain_fit-err_fit, invgain_fit+err_fit, color="0.5",
                     label=f"$\sigma$ slope: {np.sqrt(pcov[0,0]):.4f}\n$\sigma$ offset: {np.sqrt(pcov[1,1]):.4f}\n$\sigma$ knee: {np.sqrt(pcov[2,2]):.1f}")
    plt.xlabel("ISO")
    plt.ylabel("$1/G$ (ADU/e$^-$)")
    plt.xlim(0, xmax)
    plt.ylim(0, 5)
    plt.title(f"$R^2 = {R2:.4f}$")
    plt.legend(loc="lower right")
    plt.savefig(f"results/gain_new/iso_invgain_{xmax}.png")
    plt.show()
    plt.close()

    plt.figure(figsize=(7,5), tight_layout=True)
    plt.errorbar(isos, gains, yerr=gainerrs, fmt="o", c="k")
    plt.plot(irange, gain_fit, c="k", label=f"slope: {popt[0]:.4f}\noffset: {popt[1]:.4f}\nknee: {popt[2]:.1f}")
    plt.fill_between(irange, gain_fit-gain_err_fit, gain_fit+gain_err_fit, color="0.5",
                     label=f"$\sigma$ slope: {np.sqrt(pcov[0,0]):.4f}\n$\sigma$ offset: {np.sqrt(pcov[1,1]):.4f}\n$\sigma$ knee: {np.sqrt(pcov[2,2]):.1f}")
    plt.xlabel("ISO")
    plt.ylabel("$G$ (e$^-$/ADU)")
    plt.xlim(0, xmax)
    plt.ylim(0, 5)
    plt.title(f"$R^2 = {R2:.4f}$")
    plt.legend(loc="upper right")
    plt.savefig(f"results/gain_new/iso_gain_{xmax}.png")
    plt.show()
    plt.close()

    plt.figure(figsize=(7,5), tight_layout=True)
    plt.errorbar(isos, RONs, yerr=RONerrs, fmt="o", c="k")
    plt.xlabel("ISO")
    plt.ylabel("RON (e$^-$)")
    plt.xlim(0, xmax)
    plt.savefig(f"results/gain_new/iso_RON_{xmax}.png")
    plt.show()
    plt.close()

    plt.figure(figsize=(7,5), tight_layout=True)
    plt.errorbar(isos, invRONs, yerr=invRONerrs, fmt="o", c="k")
    plt.xlabel("ISO")
    plt.ylabel("RON/G (ADU)")
    plt.xlim(0, xmax)
    plt.savefig(f"results/gain_new/iso_invRON_{xmax}.png")
    plt.show()
    plt.close()