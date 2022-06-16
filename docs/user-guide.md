# Merge SVP User Guide
Merge SVP is a command line application that supports merging multiple Sound Velocity Profiles (SVP) taken at different locations, into a single file. This single file includes only the essential components of each SVP and some limited metadata (location and timestamp). The format output by Merge SVP has been designed to allow it to be read into the Teledyne CARIS application.

Merge SVP operates on two input types; the first is a collection of L0 and L2 formatted SVP files, the second is a collection of CARIS formatted SVP files. The processing performed during the merge process differs depending on which input type is used. *The input type used must be specified by the user on the command line.*


## Merge raw SVP (L0 and L2) files

### Input file format
There are three different input file formats that can be read by the merge raw SVP process; a SVP file list, L0 SVP, and L2 SVP. The SVP list file must always be provided, but users are free to use either the L0 or L2 formats for individual SVP files.


#### SVP file list format
The SVP file list includes a list of all the SVP files that will be included in the output with some additional metadata such as location and date. It is formatted as a comma separated values (csv) file, an example is provided below.

    Filename,Date,Latitude,Longitude
    V000003.TXT,28/05/2015 23:49:31,-12.24305556,130.92777780
    V000005.TXT,29/05/2015 23:18:02,-12.28333333,130.91972220
    V000008.TXT,31/05/2015 02:22:37,-12.26416667,130.88333330
    V000011.TXT,31/05/2015 03:39:05,-12.27125000,130.89747220
    V000013.TXT,31/05/2015 06:37:34,-12.24555556,130.90583330
    V000015.TXT,01/06/2015 01:11:13,-12.21666667,130.88350000
    V000017.TXT,01/06/2015 06:28:23,-12.28788050,130.76156950

This file must always include a single header line. The contents of this line are not important, but Merge SVP will skip data included in the first line.

The remainder of the file consists of 4 data columns, defined as follows;
- `filename`: the filename to extract SVP data from for this line entry, must be in either [L0](#svp-l0-format) or [L2](#svp-l2-format) format. This file must exist in the same folder as the SVP file list, or in a sub-folder named L0 or L2.
- `timestamp`: includes the date and time this SVP was recorded. Notation is Day/Month/Year Hour(24hr time):Minutes:Seconds
- `latitude`: location the SVP was taken at in decimal notation.
- `longitude`: location the SVP was taken at in decimal notation.

Note: data provided in the list file supersedes information included in the headers of the individual SVP files.

#### Auto-detection SVP formats (L0 or L2)
Merge SVP will attempt to automatically identify which format is being used in each reference SVP file. It performs this check against all files included in a SVP file list, it is therefore possible to mix and match formats within a single CSV list file.

The following checks are performed against an SVP file to determine which type it is.
- First lines beginning with "`Now:`" wil be treated as [L0 formatted files](#svp-l0-format)
- First lines beginning with "`( SoundVelocity`" wil be treated as [L3 formatted files](#svp-l2-format)


#### SVP L0 format
This format stores the sound velocity profile (sound speeds at various depths) for a single location. This section defines the format used by L0 data. An example is included below.

    Now: 28/05/2015 23:49:31
    Battery Level: 1.4V
    MiniSVP: S/N 34826
    Site info: DARWIN HARBOUR
    Calibrated: 10/01/2011
    Latitude: -12 14 35 S
    Longitude: 130 55 40 E
    Mode: P2.000000e-1
    Tare: 10.0854
    Pressure units: dBar
    00.040	24.047	0000.000
    00.202	26.599	1539.508
    00.400	26.911	1539.485
    00.600	26.139	1539.457
    00.559	26.890	1539.393
    00.841	27.064	1539.402
    00.871	27.160	1539.399

The file is defined in two sections; the header with an arbitrary number of lines, followed by the body which includes the depth vs speed data. *Merge SVP identifies the end of the header section (start of body) with the first line containing three number values*. In the example about this would be the line "`00.040	24.047	0000.000`".

Not all metadata is read from the L0 header, the following list gives the details on what is parsed based on the starting term of each line.
- `Now: ` - timestamp at which the SVP was recorded
- `Latitude: ` - location the SVP was taken at in degrees, minutes, seconds notation.
- `Longitude: ` - location the SVP was taken at in degrees, minutes, seconds notation.

Once all header lines have been parsed, Merge SVP will read the body data lines. *The first number in each data line is read as the depth, the last number the speed*. The middle number is ignored.


#### SVP L2 format
As per the previous SVP format, this data stores the SVP data for a single location, but in a different format. An example of the L2 SVP format is included below.

    ( SoundVelocity  1.0 0 201505282349 -12.24305556 130.92777780 -1 0 0 SSM_2021.1.7 P 0088 )
    0.00 1539.51
    0.20 1539.51
    0.40 1539.48
    0.60 1539.46
    0.84 1539.40
    0.87 1539.40
    1.01 1539.38
    1.20 1539.39

The L2 format includes a single header line, followed by the body data lines. Merge SVP always assumes there is single header line in L2 formatted SVP files.

The following pieces of information are read from the header line.
- 4th Token (eg; `201505282349`) - timestamp at which the SVP data was recorded.
- 5th Token (eg; `-12.24305556`) - latitude component of the location the SVP was taken at in decimal notation.
- 6th Token (eg; `130.92777780`) - longitude component of the location the SVP was taken at in decimal notation.

Merge SVP assumes all lines following the header line include body data that is provided in two space separated columns. First column is depth, second column speed.


### Input file structure
Merge SVP expects files to be located relatively according to the location of the [SVP list file](#svp-file-list-format). Each filename listed in the csv is expected to be in the same directory as the csv file, or in a folder named `L0` or `L2` in the same folder as the csv file. There is no requirement for L2 files to be included in the L2 folder; Merge SVP will identify the file type based on its contents.

Merge SVP will first look for SVP data files in the csv folder, followed by the L0 folder, then lastly the L2 folder.

An example file/folder structure is shown below using the L0 and L2 folders.

    |-- svp_file_list.csv
    |-- L0
    |   |-- V000003.TXT
    |   |-- V000005.TXT
    |   |-- V000008.TXT
    |-- L2
    |   |-- V000003.asvp
    |   |-- V000005.asvp
    |   |-- V000008.asvp
    |   |-- V000011.asvp

The following structure is also valid.

    |-- svp_file_list.csv
    |-- V000003.TXT
    |-- V000005.TXT
    |-- V000008.TXT
    |-- V000003.asvp
    |-- V000005.asvp
    |-- V000008.asvp
    |-- V000011.asvp


### Output file
Merge SVP output files include all SVPs referenced in the SVP file list csv, with meta data taken from the list csv file. An example of the output file format is shown below.

    [SVP_VERSION_2]
    output_template.svp
    Section 2015-148 23:49:31 -12:14:35.00 130:55:40.00
    0.201690 1539.508000
    0.399446 1539.485000
    0.599116 1539.457000
    0.839759 1539.402000
    Section 2015-149 23:18:02 -12:16:60.00 130:55:11.00
    0.405621 1539.718000
    0.441592 1539.671000
    0.462578 1539.675000
    0.599507 1539.661000
    0.842434 1539.669000
    0.887429 1539.668000
    1.023426 1539.666000
    1.206424 1539.670000
    Section 2015-172 05:20:13 -12:18:12.00 130:37:47.00
    1.042126 1538.484000
    1.050115 1538.494000
    1.060110 1538.415000
    1.215071 1538.399000

The output file starts with a header line `[SVP_VERSION_2]`, this is included at the start of the file.

The SVP data for each location is broken down into a number of sections, the start of these sections is indicated be a single header line starting with `Section`. This section header includes the timestamp (note: Julian days is used in date component), and the latitude/longitude of the SVP data in degrees, minutes, seconds notation.


#### Trimming of SVP data
Raw data read from the L0 and L2 SVP files is trimmed to include the longest dive section of the depth vs speed series. This is done to remove initial bobbing that sees depth fluctuate up and down in shallow depths, it also trims the measurements recorded during ascension.

Consider the following input data series.

    00.040	0000.000
    00.202	1539.508
    00.400	1539.485
    00.600	1539.457
    00.202	1539.508   <- start of longest dive
    00.559	1539.393
    00.841	1539.402
    00.871	1539.399
    00.742	1539.331
    00.592	1539.342
    00.397	1539.354
    00.647	1539.374
    00.672	1539.375
    00.816	1539.375
    01.014	1539.378
    01.205	1539.387
    01.414	1539.385
    01.610	1539.387
    01.800	1539.392   <- end of longest dive
    01.610	1539.387
    01.414	1539.385
    01.104	1539.385

Only the section from the start to end of the longest dive will be included in the merged svp output file.


### Running raw merge process
Merge SVP is a command line only application, there is no graphical user interface.
A complete list of available commands and arguments can be obtained from the application with the following command.

    mergesvp merge-raw-svp --help

Merge SVP raw process requires two input arguments; the location of the input SVP file list, and the output file to generate. These are specified by using the following arguments;
- `-i path/to/input/file.csv` location of the SVP input file list
- `-o path/to/output/file.txt` location of the merged SVP output file

An example command line is shown below.

    mergesvp merge-raw-svp -i /Users/lachlan/mergesvp/svp_time_location_data.csv -o /Users/lachlan/mergesvp/merged_output.txt


## Merge CARIS SVP files

The merge CARIS svp process combines multiple CARIS formatted SVP files into a single CARIS SVP file. During this process any duplicate SVP profiles are removed.

### Running CARIS merge process
A complete list of available commands and arguments for the CARIS merge process can be obtained from the application with the following command.

    mergesvp merge-caris-svp --help

Merge SVP CARIS process requires two input arguments; the root folder location all SVP files, and the output file to generate. These are specified by using the following arguments;
- `-i path/to/input/folder` location of the SVP files
- `-o path/to/output/file.txt` location of the merged SVP output file

An example command line is shown below.

    mergesvp merge-caris-svp -i /Users/lachlan/mergesvp/ -o /Users/lachlan/mergesvp/merged_output.txt

### Input file/folder structure
The merge CARIS SVP process will find all CARIS SVP files in or under the input folder. These files must be named `svp` (no extension).


### Duplicate SVP removal
Before duplicates are removed for the list of all SVPs, the list is sorted by the timestamp included in the header information of each SVP profile. The duplicate removal process is then run over this sorted list; this means that the first (based on timestamp) unique SVP from a group of duplicate SVPs will be included in the output.

This process identifies SVPs that have been duplicated by checking each value of the depth vs speed data contained within the SVP files. Timestamp and location (lat/lng) are not considered in this duplicate check.

Only one copy of each unique SVP will be included in the output file.


### Summary output data
When execution has completed summary information is written to standard output. An example is shown below;

    Reading SVP files  [####################################]  100%
    Finding duplicate SVPs  [####################################]  100%
    Writing merged SVP file  [####################################]  100%
    5523 SVP files were found in folder structure
    8961 SVPs were read from these files
    679 Unique profiles were found

The last three lines shown here tell us that a total of 5523 SVP files were found under the input folder. From these files a total of 8961 SVPs were read (CARIS SVP files can include multiple SVPs). Of these 8961 SVPs, only 679 were found to be unique (8282 will be removed as duplicates).

Two auxiliary output files are generated during execution of this process. One includes a complete list of all SVPs discovered files, and what duplicate group they were found to be in. The filename used is based on the specified output file with a `_group_summary.csv` suffix. The other auxiliary output file includes a listing of all unique SVPs, the timestamps included in their header information, and the time between subsequent SVPs.


## Warnings and errors
Warnings are generated when Merge SVP encounters an issue, but is able to continue processing without adverse effects on output data. An example is missing metadata within one of the SVP data files, if a latitude/longitude value is missing, Merge SVP is able to continue as the information from the list csv file is used instead. Multiple warning messages may be produced.

Errors are produced when Merge SVP encounters an issue it can not recover from; when this happens the application will output an error message and exit. A partial output file may have been generated, but this should be disregarded. Merge SVP will generate an error if it encounters a formatting issue related to information it requires, or if a SVP data file referenced within the csv list is not found.

An optional command line argument `-e` is available that will promote warnings to errors. By default Merge SVP will continue if possible after encountering a non-critical error and provide a warning message. But, by including this argument all warnings are treated as errors and the application will exit for any issues found in input files. An example command line including this argument is shown below.

    mergesvp -e merge-raw-svp -i ./test_in.csv -o ./test_out.txt