import csv, sqlite3
import osmnx as ox
import matplotlib.pyplot as plt
import numpy as np
import geopandas as gpd
import networkx as nx

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

def get_nearest_streetnames(location_tuple):
    """This function retrieves the nearest streets of a coordinate tuple (lat, lon). Currently set to drive network and a distance of 100m. Edit the parameters in line 37 to fit your preferences."""
    try: 
        G = ox.graph_from_point(location_tuple, network_type='drive', distance=100)
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
        cur.execute("CREATE TABLE " + tablename + " (zip_code TEXT, city TEXT, state TEXT, county TEXT, latlon_array TEXT, latlon_str TEXT, streetnames_array TEXT, streetnames_str TEXT);")

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
        streetname_array_str = ""

        to_db = [zipcode, city, state, county, latlon_array_str, streetname_array_str]
        cmd = "INSERT INTO " + tablename + " (zip_code, city, state, county,latlon_str, streetnames_str) VALUES (?, ?, ?, ?, ?, ?);"
        cur.execute(cmd, to_db)

        # latlon_data = myListToStr(latlon_array)
        # # latlon_data = pickle.dumps(latlon_array, pickle(type,).HIGHEST_PROTOCOL)
        # cur.execute("INSERT INTO " + tablename + "(latlon_array) values (:data)", sqlite3.Binary(latlon_data))

        # streetname_data = pickle.dumps(streetname_array, pickle(type,).HIGHEST_PROTOCOL)
        # cur.execute("INSERT INTO " + tablename + "(streetnames_array) values (:data)", sqlite3.Binary(streetname_data))
        
        for row in cur.execute("SELECT * from " + tablename):
            print(row)
    except:
        print(tablename + " already exists")

def myListToStr(myList):
    """This method takes a list of (lat, lon) tuples and converts them to a string"""

    strList = ""
    for item in myList:
        lat, lon = item #split the tuple

        strList += "{}:{} ".format(lat, lon) #append the tuple in "lat:lon" format with a " " delimiter

    return strList[:-1] #remove the final space (unneeded)

def strToMyList(myStr):
    """This method takes a string in the format "int:str int:str int:str..."
    and converts it to a list of (lat, lon) tuples"""

    myList = []
    for tup in myStr.split(" "): #for each converted tuple
        lat, lon = tup.split(":") #split the tuple

        latlon_tuple = (lat, lon)
        myList.append(latlon_tuple)

    return myList

def create_intersections_db_by_city(data): 
    """This function creates a database of the coordinates and streets of all intersections in a given city. Currently set to drive network and a radius of 1610m (1 mile). I do NOT recommend this method as a city like Los Angeles has many intersections and this process will take a long long time."""
    return


ox.config(use_cache=True, log_console=True)

con = sqlite3.connect("geo.sq3")
cur = con.cursor()

create_geo_db("resources/zip_codes_states.csv")
z = '11354'
data = get_geo_data_by_zip(z)
create_intersections_db_by_zip(data)

print(get_nearest_streetnames((40.78171239999999, -73.824605)))

con.commit()
con.close()