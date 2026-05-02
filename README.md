## Intro

This small library is meant to provide some straightforward code that allows us to quickly model the sub-divisions of focus for the competition, and allowing us to visualize these regions relative to various features of the space (roads, transit, nearby amenities, etc.).

NOTE: for pathing in VSCODE, create a folder named `.vscode` at the same layer as this repo. It should have two files:

1. `launch.json`:

```
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Run Any File with src as Root",
      "type": "debugpy",
      "request": "launch",
      "program": "${file}",
      "console": "integratedTerminal",
      "env": {
        "PYTHONPATH": "${workspaceFolder}/GIS_work"
      }
    }
  ]
}
```

2. `settings.json`:

```
{
  "python.analysis.extraPaths": ["GIS_work"]
}
```

## Data

I'm using open-source GeoPackage data provided by the Canadian Government (.gpkg) - can be found [here](https://www12.statcan.gc.ca/census-recensement/2011/geo/bound-limit/bound-limit-s-eng.cfm?year=25).

Presumably the contest will provided similar data, at the very least we can expect something like a gpkg file, or that can be converted into one. Note that the tables below define this non-competition data that I've been playing around with, though this may not match the competition schema (likely won't), and is subject to change.

## Examples

NOTE: pathing may have to be changed for you Mac or Linux users (I didn't use `os.path.join`)

Some examples can be found in `examples.py` and at the bottom of the two python files.

## Table 1.1 — Record layout: 2024 Census Subdivision Boundary File

| Attribute | Data type | Description |
|-----------|-----------|-------------|
| `PRUID` | Character (2) | Uniquely identifies a province or territory. |
| `PRNAME` | Character (100) | Province or territory name. |
| `CDUID` | Character (4) | Uniquely identifies a census division (composed of the 2-digit province or territory unique identifier followed by the 2-digit census division code). |
| `CDNAME` | Character (100) | Census division name. |
| `CDTYPE` | Character (3) | Census division type. |
| `CSDUID` | Character (7) | Uniquely identifies a census subdivision (composed of the 2-digit province/territory unique identifier followed by the 2-digit census division code and the 3-digit census subdivision code). |
| `CSDNAME` | Character (100) | Census subdivision name. |
| `CSDTYPE` | Character (3) | Census subdivisions are classified according to designations adopted by provincial/territorial or federal authorities. |
| `Geometry` | — | Defines the shape of that subdivision. |

## PRUID lookup

Key-value pairs are how we query.

| PRUID | Description |
|-------|-------------|
| `10` | Newfoundland and Labrador / Terre-Neuve-et-Labrador |
| `11` | Prince Edward Island / Île-du-Prince-Édouard |
| `12` | Nova Scotia / Nouvelle-Écosse |
| `13` | New Brunswick / Nouveau-Brunswick |
| `24` | Quebec / Québec |
| `35` | Ontario |
| `46` | Manitoba |
| `47` | Saskatchewan |
| `48` | Alberta |
| `59` | British Columbia / Colombie-Britannique |
| `60` | Yukon |
| `61` | Northwest Territories / Territoires du Nord-Ouest |
| `62` | Nunavut |
| `< >` | Not applicable (outside of Canada) |

## Relevant libraries

Dependencies can be installed via:

```
python.exe -m pip install -r requirements.txt
```

We mainly focus around `geopandas` and `osmnx`. Both of them have solid docs that are worth checking out. 

We also use `shapely` for handling more complex geometries (merging polygons into multi-polygons), and this library may be more relevant for future work.

## Current Behavior

I've made only two files. Both of them have some small runnable examples at the bottom lines.

1. `fetch_csd.py` - this file queries the local GeoPackage file and allows quick filtering over each of the above table features (Table 1.1). Note that it expects our data to have a defined CRS (some standard for GIS data), and then remaps it to a CRS that our other libraries expect - ESPG:4326.

2. `fetch_features_in_csds.py` 

- 2.1. `fetch_features` 
this method is used to query the OverPass API, which is an open-source, publicly-managed and free compendium of GIS data. This is better than Google Maps if only because we don't need to spend money. 

In particular, we use `osmnx` to handle the API querying. We could do it manually, but this library handles some awkward parts. This library seems to have a lot of features, but its not the most popular and doesn't have the best error reporting, so I haven't used it much for anything beyond API querying. 

We query features using key-value pairs (passed in as `map_feature_dict` in the code). All possible key-value pairs can be found [here](https://wiki.openstreetmap.org/wiki/Map_features). 

Note that not all of them will populate for every sub-division. I have some simple reporting on which features are found and which are not, and I recommend removing those that are not found to speed up API calls.

On that note, API calls can timeout, or just generally take a long time. I'm going to make some simple logic to save the query results and then add a function to merge two different query results so that we can minimize how much we call the API.

- 2.2 `plot_features_over_geometry`

Plotting logic - takes in the feature geometry returned by `fetch_features`, and some separate geometry that you want to overlay these features over, and plots both. Has some optional bells and whistles for nicer plotting, which can be found as comments in the code.



