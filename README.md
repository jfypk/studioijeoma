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

If you want to change from walk network to drive network: 

Enter zip code and go


# Notes

Pull coordinates of intersections by zipcodes

Gets really slow if we try to pull streetnames as well, especially if zip code has lots of intersections. 
Best way to do this is to get lat, lon data of phone and call the get_nearest_streets function