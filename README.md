
# wingpod_proc

**wingpod_proc** is a small Python package to process raw data logged by the [**hgpstools**](https://bitbucket.org/haukex/hgpstools/src/master/) package within the WINGPOD turbulence measuring system. It was designed (at least attempted) to be as simple and compact as possible using [**pandas'**](https://pandas.pydata.org) [**DataFrame**](https://pandas.pydata.org/pandas-docs/stable/dsintro.html) objects.

Key features are:

* calculation of wind components in an earth-bounded cartesian coordinate system
* export of processed data as csv and kmz
* provision of coefficients calibration routines as [**Jupyter**](http://jupyter.org/) notebooks (needed to calculate wind components accurately)
* extensive documentation (e.g. master thesis in german relating to the physics background)

___

## Installation

### Requirements
#### Software

Make sure **Python 3.6** or greater is installed. Older versions may work, but have not been tested.

Before you proceed, make sure the following libraries are installed, too,:

* numpy (v1.15.2 or greater)
* pandas (v0.23.4 or greater)
* matplotlib (library not used yet, will be added soon)
* simplekml (v1.2.8 or greater)
* zipfile (version unknown, may be added)

by hitting `import [name of desired library without braces]` into a **Python console** to import them. If a `ModuleNotFoundError` is returned, the desired library is missing and has to be installed. In this case, proceed by running `pip install [library]` in a **terminal** of your choice (e.g. Bash Shell) and try to import the library in Python again.

After you have imported the libraries listed above, check their respective versions by prompting `[library].__version__` in the **Python console** (does not work with *zipfile*!).

#### Hardware

**LOTS of RAM** (16 GB or more recommended).

There's an issue of allocating huge amounts of RAM during the processing, which (hopefully) will be addressed as soon as possible.

### Actual Installation

The installation process is rather simple. Just clone the repository:

`git clone https://bitbucket.org/brieselanger/wingpod_proc/src/master/`

To guarantee consistent and reproducible results, it is **recommended** to run the `test.py` script by prompting `python test.py` in a console after installation. A couple of `passed!` or `failed!` messages will show up, indicating if the results of the testdata processing is consistent with reference values stored in the `/testdata/testvar.py` file.

___

## Usage

To calculate the wind components straight from a given set of input log files, go into the main directory of the package and open `conf.py` with a text editor of your choice. It is **mandatory** to set three paths according to your setup:

* `data_dir` - path in which the raw input files are stored.
* `mod_dir` - path into which wingpod_proc package was cloned to.
* `out_dir` - output path for csv, kmz and plot files.

All other variables are optional and explained in the `conf.py` in detail.

**To run the package, simply hit `python main.py` in a terminal.**

If you encounter **serious memory issues** (system freezing), try to decrease `upsmpl_rate` or chop down the input files into smaller units.
___

## Description of package directories and modules

### Main directory

There are four files included in the main directory, which are the most relevant from a user's point of view:

* `main.py` - contains main work flow, loads and calls subroutines.
* `conf.py` - configuration file, explained above.
* `const.py` - constant file, contains a bunch of correction parameters retrieved by calibration routines.
* `test.py` - test routine, explained above.

While the `conf.py` file has to be frequently edited by the user according to his needs, the `const.py` includes also some important features which have to be addressed from time to time:

1. calibration constants should be reviewed and evaluated regulary (at least once in a year) by performing the calibration maneuvers and calculate the respective parameters using the calibration routines.
2. Difference between TAI and UTC (leap seconds) have to be [checked](https://hpiers.obspm.fr/iers/bul/bulc/bulletinc.dat) and set in respect to the time frame of the data to be processed. For instance, TAI/UTC-difference is 37 s for all raw data recorded in 2017 and 2018. This is necessary to calculate the exact GNSS time (does not account for leap seconds) received by the SPAN-IGM as time reference into UTC based UNIX Epoch timestamps (does account for leap seconds) of the output data.

### Subdirectories

The following subdirectories are included:

* `calibration/` - calibration routines (Jupyter notebooks) and a bunch of config./const. files.
* `data/` - wind barb png's for kmz export and X-Plane test data (latter not in use).
* `doc/` - master thesis and presentation in german which cover the physical/technical background.
* `lib/` - several python functions. They are organized according their purpose (loading data, calculating wind, exporting etc.).
* `script_graveyard/` - old (faulty) scripts went in there, not in use.
* `testdata/` - test data for test.py routine.
* `tools/` - parser tool to split concatenated raw data files by looking for logger START/STOP statements (Bash shell only).
___

## Known issues and To-Do's

* Calibration routines are still missing.
* Way to much RAM gets allocated, if a high upsampling rate (upsmpl_rate >100) was selected or the raw data files are quite extensive (several hours of data). No investigation has been done so far in this regard.
* Comma seperated output file is HUGE, compression takes ages. At least a formatted output would be nice to save as much symbols as possible.
* Some sort of verbose output would be nice (processing time, mean values for wind components, plots, packages versions etc...).

___

### Author
*Alexander B., ka42001@gmx.net*
