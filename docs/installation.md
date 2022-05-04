# Install guide
This guide is provided to guide a user through the complete installation process of the Merge SVP tool. If you are a developer, please refer to the more concise documentation in the projects [readme](../README.md).

This guide is for Windows installations.

## Python

Merge SVP is written using the Python programming language and requires Python to be installed on your machine before use.

To check the currently installed version of Python open a 'Command Prompt' and type the following command.

    python --version

The output from the command should read "Python 3.8.13" or similar. If a command not found error is reported, or the version of Python is lower than 3.8 then Python must be installed/updated. A system administrator may be required to install or upgrade Python.

The latest version of Python can be downloaded from [https://www.python.org/downloads/](https://www.python.org/downloads/).


## Download Merge SVP

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
