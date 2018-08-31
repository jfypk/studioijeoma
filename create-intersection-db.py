import csv, sqlite3
import osmnx as ox, matplotlib.pyplot as plt, numpy as np, geopandas as gpd

ox.config(use_cache=True, log_console=True)

con = sqlite3.connect("geo.sq3")
cur = con.cursor()
cur.execute("CREATE TABLE intersections (id INTEGER PRIMARY KEY, zip_code INTEGER, coordinates_blob NONE, coordinates_str TEXT, street_name_blob NONE, street_name_str TEXT);")

try: 
    G = ox.graph_from_address(zipcode, network_type='walk', distance=1610)
    G_proj = ox.project_graph(G)
    # clean up the intersections and extract their xy coords
    intersections = ox.clean_intersections(G_proj, tolerance=15, dead_ends=False)
    points = np.array([point.xy for point in intersections])

    gdf = gpd.GeoDataFrame(geometry=intersections)
    gdf.crs = G_proj.graph['crs']
    latlon_csv = ox.project_gdf(gdf, to_latlong=True).to_csv()

    reader = csv.reader(latlon_csv, delimiter=',')

    for row in reader: 
        to_db = row[1]
        cur.execute("INSERT INTO intersections (coordinates_blob) VALUES (?);", to_db)
except: 
    pass


for row in cur.execute("SELECT * from intersections"):
    	print(row)

con.commit()
con.close()