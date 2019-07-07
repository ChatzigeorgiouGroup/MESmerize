[![Snap Status](https://build.snapcraft.io/badge/kushalkolar/MESmerize.svg)](https://build.snapcraft.io/user/kushalkolar/MESmerize) [![Maintainability](https://api.codeclimate.com/v1/badges/950e956456b688c0886e/maintainability)](https://codeclimate.com/github/kushalkolar/MESmerize/maintainability)

[![Get it from the Snap Store](https://snapcraft.io/static/images/badges/en/snap-store-black.svg)](https://snapcraft.io/mesmerize)

# Mesmerize

Mesmerize is a platform for the annotation and analysis of neuronal calcium imaging data. Mesmerize attempts to encompasses the entire process of calcium imaging analysis from raw data to semi-final publication figures that are interactive, and keep track of the analysis so that it can be recapitulated. It is applicable for a broad range of experiments and is intended to be used by users with and without a programming background.

## Installation
Mesmerize is currently available only on Linux, it will soon be available for Mac OSX.

### Snap
The easiest way to get Mesmerize is through the Snap store [https://snapcraft.io/mesmerize](https://snapcraft.io/mesmerize) .

After installation simply run `mesmerize` in the terminal and the application will launch in ~10-30 seconds.

Command line snap installation:
```bash
sudo snap install mesmerize
```
Make sure you have `snapd` installed, which is required for running snap apps.
If you are on Ubuntu 16.04 or later snapd should be pre-installed.

You should be able to install `snapd` through apt for most Debian based distros
```bash
sudo apt update
sudo apt install snapd
```

Installing `snapd` on Fedora
```bash
sudo dnf install snapd
```

To install `snapd` on other distros please see: [https://docs.snapcraft.io/installing-snapd](https://docs.snapcraft.io/installing-snapd).

The snap has been tested to work on Ubuntu 18.04, Debian 9 (Stretch) and Fedora 29.

Mesmerize is experimental and we are working on increasing test coverage, however it has already been used extensively in our lab and is under active development.

### PyPI

### Virtual Environment
