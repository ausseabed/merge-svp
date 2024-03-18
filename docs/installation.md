# Install guide
This guide is provided to guide a user through the complete installation process of the Merge SVP tool. If you are a developer, please refer to the more concise documentation in the projects [readme](../README.md).

This guide is for Windows installations.

## Python

Merge SVP is written using the Python programming language and requires Python to be installed on your machine before use.

To check the currently installed version of Python open a 'Command Prompt' and type the following command.

    python --version

The output from the command should read "Python 3.8.13" or similar. If a command not found error is reported, or the version of Python is lower than 3.8 then Python must be installed/updated. A system administrator may be required to install or upgrade Python.

The latest version of Python can be downloaded from [https://www.python.org/downloads/](https://www.python.org/downloads/).


## Anaconda

Anaconda (Conda for short) is a package and environment manager for Python. While its use is not necessary for Merge SVP, the installation of several dependencies is easier through Conda. The following installation process assumes Conda is being used.

The latest version of Conda can be downloaded from the following link:
[https://docs.conda.io/en/latest/miniconda.html](https://docs.conda.io/en/latest/miniconda.html)


## Installation steps

Open a Anaconda Prompt. If Conda was installed on Windows a "Anaconda Prompt (Minicondaa3)" item should be available from the start menu.

In the Conda command prompt type the following command to create a new Conda environment

    conda create -y -n mergesvp python=3.11

Then activate the Conda environment that has just been created.

    conda activate mergesvp

Now install dependencies needed by Sound Speed Manager into the mergesvp conda environment.

Note: during the installation of the following dependencies several warning messages may be presented stating that some dependencies are missing. These can be ignored as they related to components of Sound Speed Manager that are not used by Merge SVP.

    pip install https://github.com/hydroffice/hyo2_abc2/archive/refs/heads/master.zip --no-dependencies
    pip install netCDF4
    pip install requests
    pip install pyproj
    pip install psutil
    pip install appdirs
    pip install scipy

    conda install -y -c conda-forge gdal
    conda install -y -c conda-forge gsw

Install Sound Speed Manager

    pip install https://github.com/hydroffice/hyo2_soundspeed/archive/refs/heads/master.zip --no-dependencies


### Download and Install Merge SVP

Download the latest Merge SVP release package from the GitHub repository. A *.zip file can be found under the Assets section of each release.
https://github.com/ausseabed/merge-svp/releases

Copy this zip file to a suitable folder (eg: `C:\Users\lachlan\merge-svp\`) and unzip its contents. Open a command prompt via "Run as administrator" and change to this folder. The contents of this folder should include a list of files similar to that below.

    C:\Users\lachlan\merge-svp\merge-svp-0.0.1>dir

    Directory of C:\Users\lachlan\merge-svp\merge-svp-0.0.1

    05/04/2022  09:59 PM    <DIR>          .
    05/04/2022  09:59 PM    <DIR>          ..
    05/04/2022  09:59 PM    <DIR>          .github
    04/28/2022  11:40 PM             2,213 .gitignore
    04/28/2022  11:40 PM            11,357 LICENSE
    05/04/2022  09:59 PM    <DIR>          mergesvp
    04/28/2022  11:40 PM               925 README.md
    04/28/2022  11:40 PM                26 requirements.txt
    04/28/2022  11:40 PM               774 setup.py
    05/04/2022  09:59 PM    <DIR>          tests

Install the Python dependencies using the following command. Note: this command will only work if the command prompt was opened via "Run as administrator".

    pip install -r requirements.txt

Now install Merge SVP with the following command.

    pip install .

Successful installation can be confirmed by printing the command line usage with;

    mergesvp --help

Note: after the initial installation mergesvp can be run from any command prompt (no longer requires "Run as administrator")

## Upgrading or reinstallation

Merge SVP has no mechanism to automatically upgrade itself, users must undertake the following steps to upgrade to more recent versions.

1. Uninstall existing version of Merge SVP by running `pip uninstall merge-svp` from the command prompt (may require admin permissions)
2. Download and install as per [guide](#download-and-install-merge-svp)

> **Warning**
> Please ensure older versions previously downloaded are not within the same folder as the new install process is being run.
