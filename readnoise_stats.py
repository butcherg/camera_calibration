import numpy as np
import rawpy
from sys import argv
from matplotlib import pyplot as plt, patheffects as pe
from ispex.general import cut, gauss1d, gaussMd
from ispex.gamma import cos4f, find_I0
from ispex.plot import cmaps
from ispex import raw, plot, io, wavelength
from scipy.optimize import curve_fit
from glob import glob


x = glob("results/bias/bias_stds_iso*.npy")
color_pattern = io.load_dng_raw("test_files/bias/0806a/IMG_0390.dng").raw_colors

isos = np.zeros(len(x))
mean_std = np.zeros((len(x), 4))
std_std = mean_std.copy()
for i,file in enumerate(x):
    iso = file.split(".")[0].split("_")[-1][3:]
    print(iso, end=", ")
    std = np.load(file)
    mean = np.load(file.replace("stds", "mean"))
    isos[i] = iso
    handle = f"_iso{iso}"

    RGBG, _ = raw.pull_apart(std, color_pattern)
    reshaped = [RGBG[...,0], RGBG[...,1::2], RGBG[...,2], std]

    fig, axs = plt.subplots(2,2, sharex=True, sharey=True, figsize=(15,15), tight_layout=True)
    for j, colour, ax, resh in zip(range(4), "RGBk", axs.ravel(), reshaped):
        ax.hist(resh.ravel(), bins=np.arange(0,25,0.2), color=colour)
        ax.grid(ls="--")
    axs[1,0].set_xlabel("$\sigma$") ; axs[1,1].set_xlabel("$\sigma$")
    axs[0,0].set_ylabel("$f$") ; axs[1,0].set_ylabel("$f$")
    axs[0,0].set_yscale("log") ; axs[0,0].set_ylim(ymin=1)
    fig.savefig(f"results/bias/Bias_std_hist{handle}.png")
    plt.close()

    plt.figure(figsize=(mean.shape[1]/96,mean.shape[0]/96), dpi=96, tight_layout=True)
    plt.imshow(mean, interpolation="none")
    plt.axis("off")
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    plt.savefig(f"results/bias/Bias_mean{handle}.png", dpi=96, transparent=True)
    plt.close()

    plt.figure(figsize=(std.shape[1]/96,std.shape[0]/96), dpi=96, tight_layout=True)
    plt.imshow(std, interpolation="none", aspect="equal")
    plt.axis("off")
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    plt.savefig(f"results/bias/Bias_std_im{handle}.png", dpi=96, transparent=True)
    plt.close()

    G = gaussMd(std, sigma=10)
    plt.figure(figsize=(15,15), tight_layout=True)
    plt.imshow(G, interpolation="none", aspect="equal")
    plt.axis("off")
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    plt.savefig(f"results/bias/Bias_std_gauss{handle}.png", transparent=True)
    plt.close()

    for j, c in enumerate("RGBG"):
        G = gaussMd(RGBG[...,j], sigma=10)
        plt.figure(figsize=(15,15), tight_layout=True)
        plt.imshow(G, interpolation="none", aspect="equal", cmap=cmaps[c+"r"])
        plt.axis("off")
        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
        X = "2" if j == 3 else ""
        plt.savefig(f"results/bias/Bias_std_gauss{handle}_{c}{X}.png", transparent=True)
        plt.close()