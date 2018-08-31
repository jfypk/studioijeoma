import osmnx as ox
ox.config(log_file=True, log_console=True, use_cache=True)

# get the network for all of LA - takes a couple minutes to do all the downloading and processing
place = 'Los Angeles, Los Angeles County, California, USA'
G = ox.graph_from_place(place, network_type='drive_service', simplify=False, retain_all=True)
fig, ax = ox.plot_graph(G, node_size=0, edge_linewidth=0.1, save=True, filename='la')