# Install Dependencies
## From OSMNX

Install OSMnx with conda:
```
conda install -c conda-forge osmnx
```

Or with pip:
```
pip install geopandas
pip install rtree
pip install osmnx
```

If you are pip installing from Windows, please follow instructions for [geopandas](http://geoffboeing.com/2014/09/using-geopandas-windows/). 

It's easiest to use conda-forge to get these dependencies installed. If you have any trouble with the installation, read the [docs](https://osmnx.readthedocs.io/en/stable/).

# Instructions

Script is located in the script.py file. To run, navigate to the folder and enter the following command in your terminal:

```
python script.py
```

# Notes

The script pulls lat/lon coordinates of intersections by zipcode.

Pulling intersections by cities can get really slow since a city like "Los Angeles" has a myriad of intersections. It is also slow to pull streetnames into the database, especially if a zipcode has a lot of intersections. 

To get street names, pull the nearest lat/lon from phone and call the get_nearest_streets function

Map network types are set to DRIVE

The database size for a zip code is around 1.5MB
Database names follow the template: intersections_ZIPCODE where ZIPCODE is the zipcode of interest