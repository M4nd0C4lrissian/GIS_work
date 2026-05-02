## Overview

The purpose of this folder is to associate low-level census data surveyed at the level of Dissemination Areas (DAs) to larger Census Sub-Divisions (CSDs).

The censuses that we pull from are very large (over 2000 values surveyed for each DA), and must be filtered down heavily.

The main file you need to run (after setting up the data and constants) is `full_pipeline.py`. If you've setup a `.vscode` file as specified in the outer `README`, then your pathing should work (assuming your workspace is one folder above this git repo).

The file `full_pipeline.py` takes in as arguments a list of provinces (the census data is separated by province, which we maintain), and a file pointing to the folder of the contest data file `Cleaned_Mtl_Data.csv`.

## Data

We need to manually download a few large files from online.

Specifically, for any province we care about, we need to go to this link: https://www12.statcan.gc.ca/census-recensement/2021/dp-pd/prof/details/download-telecharger.cfm?Lang=E

Click 'Comprehensive download files', and download the CSV file dubbed 'Canada, provinces, territories, census divisions (CDs), census subdivisions (CSDs) and dissemination areas (DAs) - {PROVINCE OF CHOICE} only'.

It will be a zip file that *needs to be unpacked* into `data/DA Data/{PROVINCE NAME}`. For a note on how province names are expected to be spelled, check `util/constants.py`.

*IMPORTANT* - you need to download one more file, [found here](https://www12.statcan.gc.ca/census-recensement/alternative_alternatif.cfm?l=eng&dispext=zip&teng=2021_92-151_X.zip&k=%20%20%20%20%209602&loc=/census-recensement/2021/geo/aip-pia/attribute-attribs/files-fichiers/2021_92-151_X.zip) 

Please rename it to: `GIS_work\data\2021_geographic_attribute_file.csv`

## Usage

After doing the above, all you need to specify is which census data you actually care about.

For this, look at `util/constants.py` which includes a value called Characteristics of Interest (COI). 

Everything is pre-configured to use these characteristic IDs to filter the census data. I made it a constant so that we don't hawe to re-check every time what the IDs should be (its a bit tedious).

Feel free to modify this value, but note that I've added constants.py to the `.gitignore`, so your IDs will only be locally saved.

*IMPORTANT*: to find the census data you want, and their associated IDs, check [here](https://www12.statcan.gc.ca/census-recensement/2021/dp-pd/prof/details/page.cfm?Lang=E&SearchText=24662285&DGUIDlist=2021S051224662285&GENDERlist=1,2,3&STATISTIClist=1,4&HEADERlist=0)

It's an example search result for a specific DA, and you can see all of the info available (you can filter it with the 'Add or remove data' section.)

To find the associated IDs of the features you want to work with, look at the file `GIS_work\data\DA Data\queryable_characteristics.csv`. You can CTRL + F the names as you see them on the website, and find the ID.