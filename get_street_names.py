import networkx as nx
import osmnx as ox
import geopandas as gpd
ox.config(log_console=True, use_cache=True)

location_point = (40.75431379999998, -73.8363186)

G = ox.graph_from_point(location_point, network_type='walk', distance=100)
G = ox.project_graph(G)
ints = ox.clean_intersections(G)

gdf = gpd.GeoDataFrame(ints, columns=['geometry'], crs=G.graph['crs'])
X = gdf['geometry'].map(lambda pt: pt.coords[0][0])
Y = gdf['geometry'].map(lambda pt: pt.coords[0][1])

nodes = ox.get_nearest_nodes(G, X, Y, method='kdtree')
connections = {}

for n in nodes:
    connections[n] = set([])
    for nbr in nx.neighbors(G, n):
        for d in G.get_edge_data(n, nbr).values():
            if 'name' in d:
                if type(d['name']) == str:
                    connections[n].add(d['name'])
                elif type(d['name']) == list:
                    for name in d['name']:
                        connections[n].add(name)
                else:
                    connections[n].add(None)
            else:
                connections[n].add(None)
                
print(connections)