import requests
import pandas as pd
import numpy as np
import os
import osmnx as ox
import networkx as nx
import json
import matplotlib.pyplot as plt

VOORNE_BBOX = (51.79396282482595,4.015159606933595,51.93050388636866,4.435043334960938)


script_dir = os.path.abspath(os.path.dirname(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
NETWORK_DIR = os.path.join(ROOT_DIR, "data", "networks")
INFRA_DIR = os.path.join(ROOT_DIR, "data", "infra")
HELLE_INFRA_DIR = os.path.join(INFRA_DIR, 'hellevoetsluis_infra', 'hellevoetsluis_network_osm')
REGULAR_BUS_DATA_DIR = os.path.join(ROOT_DIR, 'data', 'regular_bus')


def query_busline_overpass_turbo(osm_larger_network_name, osm_busline_name):
    
    url = "https://overpass-api.de/api/interpreter"

    query = f"""[out:json][timeout:25];
    // gather results
    nwr["network"="{osm_larger_network_name}"]["name"="{osm_busline_name}"];
    // print results
    out geom;"""

    bus_query_json = requests.get(url, params={'data': query}).json()

    return [d for d in bus_query_json['elements'][0]['members'] if d['role'] == 'stop']


def query_bus_stop_name(node_ref):
    url = "https://overpass-api.de/api/interpreter"

    query = f"""[out:json][timeout:25];
    // gather results
        node({node_ref}){VOORNE_BBOX};
    // print results
    out geom;"""

    res = requests.get(url, params={'data': query}).json()

    return res['elements'][0]['tags']['name']


def osmids_to_node_ids_and_coords(osmid_list, network_name):

    with open(os.path.join(NETWORK_DIR, network_name, "base", "nodes_all_infos.geojson")) as f:
        network_nodes_info = json.load(f)

    node_ids = []
    lon = []
    lat = []

    for osmid in osmid_list:
        for d in network_nodes_info["features"]:
            if d["properties"]["source_edge_id"] == osmid:
                node_ids.append(d["properties"]["node_index"])
                lon.append(d["geometry"]["coordinates"][0])
                lat.append(d["geometry"]["coordinates"][1])

    return node_ids, lon, lat


def create_bus_stop_nodes_csv(osm_larger_network_name, osm_busline_name, gis_name, network_name, output_name, remove_indexes_from_osm_file=None):

    bus_stops_nodes_osm = query_busline_overpass_turbo(osm_larger_network_name, osm_busline_name)

    if remove_indexes_from_osm_file:
        for i in sorted(remove_indexes_from_osm_file, reverse=True):
            del bus_stops_nodes_osm[i]

    bus_stop_names = [query_bus_stop_name(stop['ref']) for stop in bus_stops_nodes_osm]

    networkx_graph = ox.io.load_graphml(os.path.join(NETWORK_DIR, network_name, "base", "network.graphml"))

    # TODO split the edge in two?
    bus_stops_network_edge_nodes_osmids = [ox.nearest_edges(networkx_graph, stop['lon'], stop['lat']) for stop in bus_stops_nodes_osm]
    bus_stops_network_edge_node_u = [u for (u, _, _) in bus_stops_network_edge_nodes_osmids]
    bus_stops_network_edge_node_v = [v for (_, v, _) in bus_stops_network_edge_nodes_osmids]

    bus_stops_network_osmids = bus_stops_network_edge_node_v

    bus_stops_network_node_ids, lon, lat = osmids_to_node_ids_and_coords(bus_stops_network_osmids, network_name)

    dist_diff = [0]
    for i in range(1, len(bus_stops_network_node_ids)):
        # print(f"{bus_stop_names[i-1]} to {bus_stop_names[i]}")
        dist_diff.append(nx.shortest_path_length(networkx_graph, bus_stops_network_osmids[i-1], bus_stops_network_osmids[i], weight='length'))

    stop_info_osm_df = pd.DataFrame({
        'name_osm': bus_stop_names,
        'node_index': bus_stops_network_node_ids,
        'node_osmid': bus_stops_network_osmids, 
        'edge_u_osmid': bus_stops_network_edge_node_u,
        'edge_v_osmid': bus_stops_network_edge_node_v,
        'lon': lon,
        'lat': lat,
        'dist_diff': dist_diff,
        'dist_cum_diff': np.cumsum(dist_diff)
    })
    
    stop_info_osm_df.to_csv(os.path.join(INFRA_DIR, gis_name, network_name, output_name + ".csv"), index=False)


def create_boarding_points(stop_file_list):
    stop_df_list = [pd.read_csv(os.path.join(HELLE_INFRA_DIR, stop_file_name)) for stop_file_name in stop_file_list]
    boarding_points_df = pd.concat([stop_df[['name_osm', 'node_index', 'lon', 'lat']] for stop_df in stop_df_list], axis=0)
    boarding_points_df = boarding_points_df.drop_duplicates()
    boarding_points_df.to_csv(os.path.join(HELLE_INFRA_DIR, 'boarding_points.csv'))


if __name__ == "__main__":

    # Query
    osm_larger_network_name = "Voorne-Putten en Rozenburg"
    bbox = (51.8012895484025,4.080562591552735,51.869600776213886,4.238662719726563)

    # Local files
    gis_name = "hellevoetsluis_infra"
    network_name = "hellevoetsluis_network_osm"

    # osm_busline91a_name = "Bus 91: Hellevoetsluis Winkelcentrum => Hellevoetsluis Kickersbloem"
    # osm_busline91b_name = "Bus 91: Oudenhoorn Oudenhoorn => Hellevoetsluis Winkelcentrum"
    # create_bus_stop_nodes_csv(osm_larger_network_name, osm_busline91a_name, gis_name, network_name, "line91a_stops")
    # create_bus_stop_nodes_csv(osm_larger_network_name, osm_busline91b_name, gis_name, network_name, "line91b_stops")

    # osm_busline102a_name = "Bus 102: Hellevoetsluis Amnesty Internationallaan => Spijkenisse Metro Centrum"
    # osm_busline102b_name = "Bus 102: Spijkenisse Metro Centrum => Hellevoetsluis Amnesty Internationallaan"
    # create_bus_stop_nodes_csv(osm_larger_network_name, osm_busline102a_name, gis_name, network_name, "line102a_stops", [10, 11])
    # create_bus_stop_nodes_csv(osm_larger_network_name, osm_busline102b_name, gis_name, network_name, "line102b_stops", [7, 8])

    # osm_busline105a_name = "Bus 105: Hellevoetsluis Kickersbloem => Spijkenisse Metro Centrum"
    # osm_busline105b_name = "Bus 105: Spijkenisse Metro Centrum => Hellevoetsluis Kickersbloem"
    # create_bus_stop_nodes_csv(osm_larger_network_name, osm_busline105a_name, gis_name, network_name, "line105a_stops", [13, 15, 16, 23, 24, 26, 27, 28])
    # create_bus_stop_nodes_csv(osm_larger_network_name, osm_busline105b_name, gis_name, network_name, "line105b_stops", [9, 10, 11, 13, 14, 21, 22, 24])

    # osm_busline106a_name = "Bus 106: Hellevoetsluis Kickersbloem => Spijkenisse Metro Centrum"
    # osm_busline106b_name = "Bus 106: Spijkenisse Metro Centrum => Hellevoetsluis Kickersbloem"
    # create_bus_stop_nodes_csv(osm_larger_network_name, osm_busline106a_name, gis_name, network_name, "line106a_stops", [2, 3, 4, 5, 7, 11, 13, 15])
    # create_bus_stop_nodes_csv(osm_larger_network_name, osm_busline106b_name, gis_name, network_name, "line106b_stops", [3, 5, 7, 11, 13, 14, 15, 16])

    stops_list = ["line91a_stops", "line91b_stops", "line102a_stops", "line102b_stops", "line105a_stops", "line105b_stops", "line106a_stops", "line106b_stops"]
    create_boarding_points([f"{stop_file_name}.csv" for stop_file_name in stops_list])
