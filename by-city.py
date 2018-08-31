import osmnx as ox, matplotlib.pyplot as plt, numpy as np, geopandas as gpd
ox.config(use_cache=True, log_console=True)

G = ox.graph_from_place('Costa Mesa, CA, USA', network_type='walk', memory=25000000, retain_all=True)
G = ox.project_graph(G)
gdf = ox.gdf_from_place('Costa Mesa, CA, USA')
poly = gdf['geometry'].iloc[0]
poly, crs = ox.project_geometry(poly)
poly = poly.buffer(-500)
G_truncated = ox.truncate_graph_polygon(G, poly, retain_all=False, truncate_by_edge=False, quadrat_width=1000, buffer_amount=0.01)

# clean up the intersections and extract their xy coords
intersections = ox.clean_intersections(G, tolerance=15, dead_ends=False)
points = np.array([point.xy for point in intersections])

fig, ax = ox.plot_graph(G_truncated)
ax.scatter(x=points[:,0], y=points[:,1], zorder=2, color='#66ccff', edgecolors='k')
plt.show()

gdf = gpd.GeoDataFrame(geometry=intersections)
gdf.crs = G.graph['crs']
ox.project_gdf(gdf, to_latlong=True)