GeoPackage
    └─► geopandas (analysis, filtering, spatial joins)
            ├─► shapely (geometry math — contains, intersects, buffer)
            ├─► GeoJSON (Google Maps, web APIs, Leaflet/Folium)
            ├─► PostGIS (if you scale up to a database)
            └─► matplotlib / contextily (visualization)


Table 4.1
Record layout - 2024 Census Subdivision Boundary File
Table summary
This table displays the results of Record layout - 2024 Census Subdivision Boundary File. The information is grouped by Attribute name (appearing as row headers), Data type and Description (appearing as column headers).

Attribute name	Data type	Description
PRUID	Character (2)	Uniquely identifies a province or territory.
PRNAME	Character (100)	Province or territory name.
CDUID	Character (4)	Uniquely identifies a census division (composed of the 2-digit province or territory unique identifier followed by the 2-digit census division code).
CDNAME	Character (100)	Census division name.
CDTYPE	Character (3)	Census division type.
CSDUID	Character (7)	Uniquely identifies a census subdivision (composed of the 2-digit province/territory unique identifier followed by the 2-digit census division code and the 3-digit census subdivision code).
CSDNAME	Character (100)	Census subdivision name.
CSDTYPE	Character (3)	Census subdivisions are classified according to designations adopted by provincial/territorial or federal authorities.

Also includes: Geometry (which defines the shape of that sub-division)


Need to turn the following into some static data:

PRUID	DESCRIPTION
10	Newfoundland and Labrador / Terre-Neuve-et-Labrador
11	Prince Edward Island / Île-du-Prince-Édouard
12	Nova Scotia / Nouvelle-Écosse
13	New Brunswick / Nouveau-Brunswick
24	Quebec / Québec
35	Ontario
46	Manitoba
47	Saskatchewan
48	Alberta
59	British Columbia / Colombie-Britannique
60	Yukon
61	Northwest Territories / Territoires du Nord-Ouest
62	Nunavut
< >	not applicable (outside of Canada)

Key-Value pairs are how we query