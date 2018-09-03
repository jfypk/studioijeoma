import csv, sqlite3
import osmnx as ox
import matplotlib.pyplot as plt
import numpy as np
import geopandas as gpd
import networkx as nx
import ast

"""----------------Define helper functions----------------"""

def create_geo_db(csv_path):
    """This function creates a geo database of all zipcodes, cities, states, and counties in the United States"""
    try:
        cur.execute("CREATE TABLE geo (id INTEGER PRIMARY KEY, zip_code TEXT, city TEXT, state TEXT, county TEXT);")

        reader = csv.reader(open(csv_path, 'r'), delimiter=',')

        for row in reader:
            to_db = [row[0], row[3], row[4], row[5]]
            cur.execute("INSERT INTO geo (zip_code, city, state, county) VALUES (?, ?, ?, ?);", to_db)
        print("db created")
    except:
        print("db already exists")
        pass

def get_geo_data_by_zip(zipcode):
    """This function returns state, city, and county data based on zipcode input """
    results = {}
    query = "SELECT * from geo where zip_code = " + "\'"+str(zipcode)+"\'"
    print(query)
    index = 1
    for row in cur.execute(query):
        results[index] = row
        index += 1
    return results

def get_nearest_streetnames(location_tuple, distFromPoint = 50):
    """This function retrieves the nearest streets of a coordinate tuple (lat, lon). Currently set to drive network. Edit the parameters in line 40 to fit your preferences."""
    try: 
        G = ox.graph_from_point(location_tuple, network_type='drive', distance=distFromPoint)
        G = ox.project_graph(G)
        ints = ox.clean_intersections(G)

        gdf = gpd.GeoDataFrame(ints, columns=['geometry'], crs=G.graph['crs'])
        X = gdf['geometry'].map(lambda pt: pt.coords[0][0])
        Y = gdf['geometry'].map(lambda pt: pt.coords[0][1])

        nodes = ox.get_nearest_nodes(G, X, Y, method='kdtree')
        streetnames = []

        for n in nodes:
            for nbr in nx.neighbors(G, n):
                for d in G.get_edge_data(n, nbr).values():
                    if 'name' in d:
                        if type(d['name']) == str:
                            streetnames.append(d['name'])
                        elif type(d['name']) == list:
                            for name in d['name']:
                                streetnames.append(name)
        streetnames = list(set(streetnames))
    except:
        streetnames = []
    return streetnames

def create_intersections_db_by_zip(data):
    """This function creates a database of the coordinates and streets of all intersections in a mile radius of a given zipcode. Currently set to drive network and a radius of 1610m (1 mile). Edit the parameters in line 81 to fit your preferences"""
    d = data[1]
    zipcode = d[1]
    city = d[2]
    state = d[3]
    county = d[4]
    
    tablename = "intersections_" + str(zipcode)
    
    try: 
        cur.execute("CREATE TABLE " + tablename + " (zip_code TEXT, city TEXT, state TEXT, county TEXT, latlon_str TEXT);")

        latlon_array = []
        streetname_array = []
        latlon_array_str = ""
        streetname_array_str = ""

        try:
            G = ox.graph_from_address(zipcode, network_type='drive', distance=1610)
            G_proj = ox.project_graph(G)
            # clean up the intersections and extract their xy coords
            intersections = ox.clean_intersections(G_proj, tolerance=15, dead_ends=False)
            points = np.array([point.xy for point in intersections])

            gdf = gpd.GeoDataFrame(geometry=intersections)
            gdf.crs = G_proj.graph['crs']
            lonlat = ox.project_gdf(gdf, to_latlong=True)
            a = lonlat['geometry'].tolist()
            for coord in a:
                lon = coord.x
                lat = coord.y
                latlon_tuple = (lat, lon)

                # nearest_streets = get_nearest_streetnames(latlon_tuple)
                
                # streetname_array.append(nearest_streets)
                latlon_array.append(latlon_tuple)
        except:
            #THROW A WARNING THAT THERE IS NO LAT/LON DATA FOR THIS ZIPCODE
            pass
        
        latlon_array_str = str(latlon_array).strip('[]')
        # streetname_array_str = str(streetname_array).strip('[]')

        to_db = [zipcode, city, state, county, latlon_array_str]
        cmd = "INSERT INTO " + tablename + " (zip_code, city, state, county,latlon_str) VALUES (?, ?, ?, ?, ?);"
        cur.execute(cmd, to_db)
        
        for row in cur.execute("SELECT * from " + tablename):
            print(row)
    except:
        print(tablename + " already exists")

def create_intersections_bigdb_by_city(data):
    """This function creates a database of the coordinates and streets of all intersections in a mile radius of a given zipcode. Currently set to drive network and a radius of 1610m (1 mile). Edit the parameters in line 81 to fit your preferences"""
    d = data[1]
    zipcode = d[1]
    city = d[2]
    state = d[3]
    county = d[4]
    
    tablename = "intersections_" + str(city)
    
    try: 
        cur.execute("CREATE TABLE " + tablename + " (zip_code TEXT, city TEXT, state TEXT, county TEXT, latlon_str TEXT, streetnames_str TEXT);")

        latlon_array = []
        streetname_array = []
        latlon_array_str = ""
        streetname_array_str = ""

        try:
            place = city + ', ' + county + ', ' + state + ", USA "
            G = ox.graph_from_place(place, network_type='drive', distance=1610, retain_all = True, simplify = True)
            G_proj = ox.project_graph(G)
            # clean up the intersections and extract their xy coords
            intersections = ox.clean_intersections(G_proj, tolerance=15, dead_ends=False)
            # points = np.array([point.xy for point in intersections])

            gdf = gpd.GeoDataFrame(geometry=intersections)
            gdf.crs = G_proj.graph['crs']
            lonlat = ox.project_gdf(gdf, to_latlong=True)
            a = lonlat['geometry'].tolist()
            for coord in a:
                lon = coord.x
                lat = coord.y
                latlon_tuple = (lat, lon)

                nearest_streets = get_nearest_streetnames(latlon_tuple)
                
                streetname_array.append(nearest_streets)
                latlon_array.append(latlon_tuple)
        except:
            #THROW A WARNING THAT THERE IS NO LAT/LON DATA FOR THIS ZIPCODE
            pass
        
        latlon_array_str = str(latlon_array).strip('[]')
        streetname_array_str = str(streetname_array).strip('[]')

        to_db = [zipcode, city, state, county, latlon_array_str]
        cmd = "INSERT INTO " + tablename + " (zip_code, city, state, county,latlon_str, streetname_array_str) VALUES (?, ?, ?, ?, ?, ?);"
        cur.execute(cmd, to_db)
        
        for row in cur.execute("SELECT * from " + tablename):
            print(row)
    except:
        print(tablename + " already exists")

def get_intersections_data_from_db(db):
    """
        This function returns all the data from db table in an array. 
    """
    data = []
    for row in cur.execute("SELECT * from " + db):
        data.append(row)
    return data

def strListToList(strList):
    x = ast.literal_eval(strList)
    return x

"""----------------Begin Script----------------"""

#configure osmnx 
ox.config(use_cache=True, log_console=True)

#connect to sqlite3 database
con = sqlite3.connect("geo.sq3")
cur = con.cursor()

#create database with geo data
create_geo_db("resources/zip_codes_states.csv")

#handle zipcode input (Connect to Mobile App here)
z = '94608'

#create db of lat/lon intersections 
geodata = get_geo_data_by_zip(z)
create_intersections_db_by_zip(geodata)

#intersections data
db = "intersections_" + z
data = get_intersections_data_from_db(db)
data = data[0]
zipcode = data[0]
city = data[1]
state = data[2]
county = data[3]
str_latlon = data[4]
arr_latlon = strListToList(str_latlon)
num_intersections = len(arr_latlon)

print("\n")
print("\n")
print("\n")
print("Intersection data for " + city + " " + state + " " + county + " " + zipcode)
print(str(num_intersections) + " intersections found")
print("------------------")
print(str_latlon)
print("------------------")
print("\n")
print("\n")
print("\n")

#get closest street names for specific intersection
#Note: better to call this function than to list in database as database will be too big for zip codes with large number of intersections
latlon_tuple = arr_latlon[int(num_intersections/2)]
closest_streets = get_nearest_streetnames(latlon_tuple)

print("\n")
print("\n")
print("\n")
print("CLOSEST STREETS TO " + str(latlon_tuple))
print("------------------")
print(closest_streets)
print("------------------")
print("\n")
print("\n")
print("\n")

#commit and close database
con.commit()
con.close()