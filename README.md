# SPECTACLE

SPECTACLE (Standardised Photographic Equipment Calibration Technique And CataLoguE) is a standardised methodology for the spectral and radiometric calibration of consumer camera data. The associated database, containing calibration data for a number of popular consumer cameras, can be found at http://spectacle.ddq.nl/. More information on the SPECTACLE methodology, including results from applying it to several cameras, can be found in our paper: https://doi.org/10.1364/OE.27.019075

This repository contains the associated `spectacle` Python module. This module can be used to calibrate data using previously obtained calibration data (measured by the user or retrieved from the SPECTACLE database). It also includes functions and pre-made scripts for processing calibration data, as described in the paper linked above.

# Installation

Currently, the easiest way to install the `spectacle` module is to clone this repository (`git clone git@github.com:monocle-h2020/camera_calibration.git`) and then install it using pip, by navigating into the repository folder and running `pip install .`. We will soon upload it to PyPI to simplify this process even further.

# Usage

There are three main use cases for the `spectacle` module, each of which will be explained further in the relevant subsection. They are as follows:

1. Application: applying camera calibrations to new data.
2. Analysis: analysing camera properties and performance based on calibration data.
3. Calibration: generating calibration data for use in the two other use cases.

## Application

To apply calibrations to new data, simply load the [`spectacle.calibrate`](spectacle/calibrate.py) submodule and apply the methods contained therein. For example, to correct for the camera bias, one would use the `correct_bias` method from this submodule. Each method comes with detailed documentation on its usage, which can be found [here](spectacle/calibrate.py) or from within Python (using Python's `help` function or iPython's `?` and `??` shortcuts).

## Analysis

A large number of pre-made scripts for the analysis of camera data, calibration data, and metadata are provided in the [analysis](analysis) subfolder. These are sorted by the parameter they probe, such as linearity or dark current. Please refer to the README in the [analysis](analysis) subfolder and documentation in the scripts themselves for further information. A number of common methods for analysing these data have also been bundled into the [`spectacle.analyse`](spectacle/analyse.py) submodule.

## Calibration

Finally, pre-made scripts for generating calibration data based on data gathered by the user are provided in the [calibration](calibration) subfolder. These are sorted by the parameter they probe, such as bias or flat-field response. Furthermore, a script is provided that combines calibration data generated this way into a format that can be uploaded to the [SPECTACLE database](http://spectacle.ddq.nl/). Please refer to the README in the [calibration](calibration) subfolder and documentation in the scripts themselves for further information.

# Further information

The SPECTACLE method itself has been fully developed and applied, as shown in [our paper](https://doi.org/10.1364/OE.27.019075). The [SPECTACLE database](http://spectacle.ddq.nl/) and `spectacle` Python module are still in active development. Contributions from the community are highly welcome and we invite everyone to contribute.

Further information will be added to this repository with time. If anything is missing, please [raise an issue](https://github.com/monocle-h2020/camera_calibration/issues) or [contact the authors directly](mailto:burggraaff@strw.leidenuniv.nl).
