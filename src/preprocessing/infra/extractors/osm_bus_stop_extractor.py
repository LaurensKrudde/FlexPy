import requests
import pandas as pd
import os
import osmnx as ox
import json

script_dir = os.path.abspath(os.path.dirname(__file__))
FLEETPY_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(script_dir))))
NETWORK_DIR = os.path.join(FLEETPY_DIR, "data", "networks")
INFRA_DIR = os.path.join(FLEETPY_DIR, "data", "infra")

def query_busline_overpass_turbo(osm_larger_network_name, osm_busline_name):
    
    url = "https://overpass-api.de/api/interpreter"

    query = f"""[out:json][timeout:25];
    // gather results
    nwr["network"="{osm_larger_network_name}"]["name"="{osm_busline_name}"];
    // print results
    out geom;"""

    return requests.get(url, params={'data': query}).json()


def osmid_to_node_id(osmid_list):

    with open(os.path.join(NETWORK_DIR, network_name, "base", "nodes_all_infos.geojson")) as f:
        network_nodes_info = json.load(f)

    return [d["properties"]["node_index"] for d in network_nodes_info["features"] if d["properties"]["source_edge_id"] in osmid_list]


def osmid_to_coord(osmid_list):

    with open(os.path.join(NETWORK_DIR, network_name, "base", "nodes_all_infos.geojson")) as f:
        network_nodes_info = json.load(f)

    lon = [d["geometry"]["coordinates"][0] for d in network_nodes_info["features"] if d["properties"]["source_edge_id"] in osmid_list]
    lat = [d["geometry"]["coordinates"][1] for d in network_nodes_info["features"] if d["properties"]["source_edge_id"] in osmid_list]

    return lon, lat


def create_bus_stop_nodes_csv(osm_larger_network_name, osm_busline_name, gis_name, network_name):

    bus_query_json = query_busline_overpass_turbo(osm_larger_network_name, osm_busline_name)
    stops_nodes_osm = [d for d in bus_query_json['elements'][0]['members'] if d['role'] == 'stop']

    networkx_graph = ox.io.load_graphml(os.path.join(NETWORK_DIR, network_name, "base", "network.graphml"))
    stop_nodes_network_osmids = [ox.nearest_nodes(networkx_graph, stop['lon'], stop['lat']) for stop in stops_nodes_osm]

    stop_nodes_network_node_ids = osmid_to_node_id(stop_nodes_network_osmids)

    lon, lat = osmid_to_coord(stop_nodes_network_osmids)

    boarding_points_df = pd.DataFrame({'node_index': stop_nodes_network_node_ids,
                                       'osmid': stop_nodes_network_osmids, 
                                       'lon': lon,
                                       'lat': lat})
    boarding_points_df.to_csv(os.path.join(INFRA_DIR, gis_name, network_name, "boarding_points.csv"), index=False)


if __name__ == "__main__":

    osm_larger_network_name = "Voorne-Putten en Rozenburg"
    osm_busline_name = "Bus 91: Oudenhoorn Oudenhoorn => Hellevoetsluis Winkelcentrum"
    gis_name = "hellevoetsluis_infra"
    network_name = "hellevoetsluis_network_osm"

    create_bus_stop_nodes_csv(osm_larger_network_name, osm_busline_name, gis_name, network_name)
