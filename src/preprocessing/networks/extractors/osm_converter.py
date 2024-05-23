import os
from shapely.geometry import Point, LineString, Polygon
import numpy as np
import pandas as pd
import geopandas as gpd

import osmnx as ox
import networkx as nx

script_dir = os.path.abspath(os.path.dirname(__file__))
FLEETPY_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(script_dir))))
NETWORK_DIR = os.path.join(FLEETPY_DIR, "data", "networks")
INFRA_DIR = os.path.join(FLEETPY_DIR, 'data', 'infra', 'hellevoetsluis_infra', 'hellevoetsluis_network_osm')

DEFAULT_MAX_V = 30  # if no value is provided for maximum velocity on the street, this is the default value (kmh)
MIN_MAX_V = 20  # minimal value for the maximum velocity on the street (kmh) | overwrites data from osm if below
MAX_MAX_V = 130 # maximal value for the maximum velocity on the street (kmh) | overwrites data from osm if above

#NETWORK CLASSES FOR EXPORT


def convertCoordListToString(coord_list):
    l = []
    for coord in coord_list:
        l.append("{};{}".format(coord[0], coord[1]))
    return "|".join(l)


def convertStringToCoordList(string):
    coord_list = []
    for e in string.split("|"):
        x,y = e.split(";")
        coord_list.append( (float(x), float(y)) )
    return coord_list


def convert_str_to_float(in_str):
    print(in_str)
    if type(in_str) == list:
        return_float = max([convert_str_to_float(x) for x in in_str])
    elif type(in_str) == str:
        s0 = ""
        for char in in_str:
            try:
                int(char)
                s0 += char
            except ValueError:
                if char == ".":
                    s0 += char
        return_float = float(s0)
    else:
        return_float = float(in_str)
    return return_float


def createDir(dirname):
    if os.path.isdir(dirname):
        print("{} allready here! Overwriting basic network files!".format(dirname))
    else:
        os.makedirs(dirname)


class NetworkOSMCreator():
    def __init__(self):
        self.nodes = []
        self.edge_id_to_edge = {}
        self.source_edge_id_to_edge = {}
        self.super_nodes = {}

        self.networkXGraph = None

    def addNode(self, node):
        self.nodes.append(node)
        if node.index != len(self.nodes) - 1:
            print("wrong node order!")
            exit()

    def addSuperNode(self, super_node):
        self.super_nodes[super_node.id] = super_node

    def getCurrentNodeNumber(self):
        return len(self.nodes)

    def addEdge(self, edge):
        start_index = edge.start_node_index
        end_index = edge.end_node_index
        print("edge {} -> {} nodes {}".format(start_index, end_index, len(self.nodes)))
        self.nodes[start_index].addOutgoingEdge(edge)
        self.nodes[end_index].addIncomingEdge(edge)
        self.edge_id_to_edge[edge.id] = edge
        if edge.source_edge_id is not None:
            self.source_edge_id_to_edge[edge.source_edge_id] = edge

    def exportNetworkFull(self, destination_folder, name):
        node_list = []
        for node in self.nodes:
            node_list.append(str(node))
        f = open(os.path.join(destination_folder, "{}_nodes.csv".format(name)), "w")
        f.write("\n".join(node_list))
        f.close()

        edge_list = []
        for edge in self.edge_id_to_edge.values():
            edge_list.append(str(edge))
        f = open(os.path.join(destination_folder, "{}_edges.csv".format(name)), "w")
        f.write("\n".join(edge_list))
        f.close()

        super_node_list = []
        for super_node in self.super_nodes.values():
            super_node_list.append(str(super_node))

        f = open(os.path.join(destination_folder, "{}_supernodes.csv".format(name)), "w")
        f.write("\n".join(super_node_list))
        f.close()

    def loadNetworkFromOSM(self, polygon = None, bounding_box = None, by_name=None, network_type = "drive"):
        """ loads network from osmnx
        network_type specified from osmnx (e.g. drive or all)
        either bounding_box (x_max, x_min, y_max, y_min)  or polygon (shapely) has to be given
        """
        if polygon is None and bounding_box is None and by_name is None:
            print("loadNetworkFromOSM: no area specification given!")
            exit()
        if polygon is not None:
            G = ox.graph_from_polygon(polygon, network_type = network_type)
        
        # Hardcoded for now TODO
        elif by_name == "Hellevoetsluis_Oudenhoorn":
            G1 = ox.graph_from_place("Hellevoetsluis", network_type=network_type, truncate_by_edge=True)
            G2 = ox.graph_from_place("Oudenhoorn", network_type=network_type, truncate_by_edge=True)
            G = nx.compose(G1, G2)
        elif by_name == "Voorne_Putten_Rozenburg":
            G1 = ox.graph_from_place("Voorne-Putten", network_type=network_type, truncate_by_edge=True)
            G2 = ox.graph_from_place("Rozenburg eiland", network_type=network_type, truncate_by_edge=True)
            G_hartelbrug = ox.graph_from_point((51.8648, 4.2993), dist=1000, network_type=network_type, truncate_by_edge=True) 
            G_dammenweg = ox.graph_from_point((51.8989, 4.2089), dist=1000, network_type=network_type, truncate_by_edge=True) 
            G = nx.compose_all([G1, G2, G_hartelbrug, G_dammenweg])

        elif by_name is not None:
            G = ox.graph_from_place(by_name, network_type=network_type)
        else:
            G = ox.graph_from_bbox(bounding_box[0], bounding_box[1], bounding_box[2], bounding_box[3], network_type = network_type)
        self.networkXGraph = G

    def createNetworkFromNetwokXGraph(self, speed_unit="kmh"):
        osm_G = self.networkXGraph

        # Create nodes
        node_id_to_index = {}
        node_index_to_id = {}
        node_index_to_infos = {}
        c = 0
        
        for e_id, data in osm_G.nodes(data=True):
            if node_id_to_index.get(e_id, None) is not None:
                print("error for {}".format(e_id))
            node_id_to_index[e_id] = c
            node_index_to_id[c] = e_id
            coor = (data['x'], data['y'])
            node_index_to_infos[c] = (coor, e_id)
            node = NetworkNode(c, float(coor[0]), float(coor[1]), source_edge_id=e_id)
            self.addNode(node)
            c+=1

        print("Number nodes: {}".format(c))

        # Create edges
        arcs = {}
        for u, v, key, data in osm_G.edges(keys=True, data=True):
            start_node = node_id_to_index[u]
            end_node = node_id_to_index[v]
            if arcs.get(start_node, {}).get(end_node,None) is not None:
                print("multiple arcs? This arc is ignored currently!")
                print(u, v, data)
                print(arcs.get(start_node, {}).get(end_node,None))
                continue
            # Try to add end_node to start_node dict, except the dict does not yet exist, then create it
            try:
                arcs[start_node][end_node] = data
            except:
                arcs[start_node] = {end_node : data}

        for start_node, end_dict in arcs.items():
            
            for end_node, data in end_dict.items():
                print(start_node, end_node, data)
                l = data['length']
                max_v_str = data.get('maxspeed')

                # Handle max speeds
                if type(max_v_str) == list:
                    max_max_v = None
                    for x in max_v_str:
                        try:
                            u = convert_str_to_float(x)
                        except:
                            u = None
                        if u is not None:
                            if max_max_v is None:
                                max_max_v = u
                            elif u > max_max_v:
                                max_max_v = u
                    max_v_str = str(max_max_v)
                if not max_v_str or max_v_str == "none":
                    print("no maximal velocity defined on this edge! -> {} km/h considered currently".format(DEFAULT_MAX_V))
                    max_v = DEFAULT_MAX_V
                    if speed_unit == "mph":
                        max_v = DEFAULT_MAX_V / 1.6
                elif max_v_str == "walk":
                    print("walking edge??")
                    continue
                else:
                    max_v = convert_str_to_float(max_v_str)
                # computation from mph
                if speed_unit == "mph":
                    max_v = max_v * 1.6
                # check for unrealistic values -> set to default value
                if max_v < MIN_MAX_V:
                    print("maximal street velocity {} below threshold {}. Changing value to threshold.".format(max_v, MIN_MAX_V))
                    max_v = MIN_MAX_V
                elif max_v > MAX_MAX_V:
                    print("maximal street velocity {} above threshold {}. Changing value to threshold.".format(max_v, MAX_MAX_V))
                    max_v = MAX_MAX_V

                roadtype = data.get('highway', '')
                if type(roadtype) == list:
                    roadtype = ";".join(roadtype)

                polyline = []
                if data.get("geometry"):
                    polyline = list(data["geometry"].coords)
                if len(polyline) == 0:
                    polyline = [self.nodes[start_node].coordinates, self.nodes[end_node].coordinates]

                osmid = data.get("osmid", None)
                if type(osmid) == list:
                    print("multiple osmids! take first")
                    osmid = osmid[0]

                edge = NetworkEdge(
                    start_node, 
                    end_node, 
                    float(data["length"])/max_v*3.6, 
                    float(data["length"]), 
                    source_edge_id=osmid, 
                    roadtype=roadtype, 
                    polyline=polyline, 
                    edge_index="{};{}".format(start_node, end_node)
                )

                #print("tt ", float(data["length"])/max_v*3.6, "length", float(data["length"]))

                self.addEdge(edge)

        self.plotNetwork()


    def splitEdge(self, edge_id, split_coord):
        """
        Splits an edge into two at the specified coordinates and adds a new node at that point.
        
        :param edge_id: The identifier of the edge to split.
        :param split_coord: A tuple (x, y) representing the coordinates where the edge should be split.
        """
        if edge_id not in self.edge_id_to_edge:
            print("Edge with id {} does not exist.".format(edge_id))
            return

        # Retrieve the original edge
        original_edge = self.edge_id_to_edge[edge_id]
        start_node_index = original_edge.start_node_index
        end_node_index = original_edge.end_node_index

        # Create a new node at the split coordinates
        new_node_index = len(self.nodes)
        new_node = NetworkNode(new_node_index, split_coord[0], split_coord[1])
        self.addNode(new_node)

        # Create two new edges from the start node to the new node and from the new node to the end node
        new_edge1 = NetworkEdge(start_node_index, new_node_index, 
                                travel_time=original_edge.travel_time / 2,  # Simplified calculation
                                travel_distance=original_edge.travel_distance / 2,
                                polyline=[self.nodes[start_node_index].coordinates, split_coord])
        new_edge2 = NetworkEdge(new_node_index, end_node_index,
                                travel_time=original_edge.travel_time / 2,  # Simplified calculation
                                travel_distance=original_edge.travel_distance / 2,
                                polyline=[split_coord, self.nodes[end_node_index].coordinates])

        # Add new edges to the network
        self.addEdge(new_edge1)
        self.addEdge(new_edge2)

        # Remove the original edge
        del self.edge_id_to_edge[edge_id]
        self.nodes[start_node_index].outgoing_edges.pop(edge_id, None)
        self.nodes[end_node_index].incoming_edges.pop(edge_id, None)

        print("Edge {} split at coordinates {}. New edges {} and {} created.".format(edge_id, split_coord, new_edge1.id, new_edge2.id))


    def plotNetwork(self):
        from matplotlib import pyplot as plt

        x = [node.coordinates[0] for node in self.nodes]
        y = [node.coordinates[1] for node in self.nodes]

        plt.plot(x, y, "rx")

        for arc in self.edge_id_to_edge.values():
            plt.plot([x[0] for x in arc.polyline], [y[1] for y in arc.polyline], "b-")

        for supernode in self.super_nodes.values():
            x = [supernode.polygon[i%len(supernode.polygon)][0] for i in range(len(supernode.polygon) + 1)]
            y = [supernode.polygon[i%len(supernode.polygon)][1] for i in range(len(supernode.polygon) + 1)]
            plt.plot(x, y, "g-")

        # Flexcode plot boarding points
        boarding_points_df = pd.read_csv(os.path.join(INFRA_DIR, 'line105a_stops.csv'))
        plt.plot(boarding_points_df['lon'], boarding_points_df['lat'], "go")

        plt.show()

    def convertFullInformationToGeoJSON(self, path):
        node_gpd_list = []
        for node in self.nodes:
            node_gpd_list.append(node.getAttributeDictGEOJSON())
        node_gpd = gpd.GeoDataFrame(node_gpd_list)
        node_gpd.to_file(os.path.join(path, "nodes_all_infos.geojson"), driver="GeoJSON")

        edge_gpd_list = []
        for edge in self.edge_id_to_edge.values():
            edge_gpd_list.append(edge.getAttributeDictGEOJSON())
        edge_gpd = gpd.GeoDataFrame(edge_gpd_list)
        edge_gpd.to_file(os.path.join(path, "edges_all_infos.geojson"), driver="GeoJSON")

        if len(self.super_nodes.keys()) > 0:
            supernode_gpd_list = []
            for supernode in self.super_nodes.values():
                supernode_gpd_list.append(supernode.getAttributeDictGEOJSON())
            supernode_gpd = gpd.GeoDataFrame(supernode_gpd_list)
            # print(supernode_gpd.head())
            # print(supernode_gpd.to_json())
            supernode_gpd.to_file(os.path.join(path, "supernodes_all_infos.geojson"), driver="GeoJSON")

    def convertBaseInformationToCSV(self, path):
        node_pd_list = []
        for node in self.nodes:
            node_pd_list.append(node.getAttributeDictBaseFile())
        node_pd = pd.DataFrame(node_pd_list)
        node_pd.to_csv(os.path.join(path, "nodes.csv"), index=False)

        edge_pd_list = []
        for edge in self.edge_id_to_edge.values():
            edge_pd_list.append( edge.getAttributeDictBaseFile() )
        edge_pd = pd.DataFrame(edge_pd_list)
        edge_pd.to_csv(os.path.join(path, "edges.csv"), index=False)

    def createCRSfile(self, path):
        with open(os.path.join(path, "crs.info"), "w") as file:
            file.write(self.networkXGraph.graph["crs"])

    def saveOriginalOSMGraph(self, path):
        ox.io.save_graphml(self.networkXGraph, os.path.join(path, "network.graphml"))        


class NetworkNode():
    def __init__(self, node_index, pos_x, pos_y, is_stop_only = False, source_edge_id = None, ch_value = -1):
        self.index = node_index
        self.coordinates = (pos_x, pos_y)
        self.is_stop_only = is_stop_only
        self.ch_value = ch_value
        self.source_edge_id = source_edge_id

        self.outgoing_edges = {}
        self.incoming_edges = {}

        self.outgoing_ch_edges = {}
        self.incoming_ch_edges = {}

    def addIncomingEdge(self, edge):
        self.incoming_edges[edge.id] = edge

    def addOutgoingEdge(self, edge):
        self.outgoing_edges[edge.id] = edge

    def __str__(self):
        s = "{},{},{}".format(self.index, self.coordinates[0], self.coordinates[1])
        if self.is_stop_only:
            s += ",{}".format(1)
        else:
            s += ","
        s += ",{}".format(self.ch_value)
        return s

    def getAttributeDictGEOJSON(self):
        att_dict = {"node_index" : self.index, "is_stop_only" : self.is_stop_only, "source_edge_id" : self.source_edge_id, "geometry" : Point(self.coordinates)}
        return att_dict

    def getAttributeDictBaseFile(self):
        att_dict = {"node_index" : self.index, "is_stop_only" : self.is_stop_only, "pos_x" : self.coordinates[0], "pos_y" : self.coordinates[1] }
        return att_dict

class NetworkSuperNode():
    def __init__(self, id, node_id_list, polygon = None, source_edge_id = None):
        self.node_collection = node_id_list[:]
        self.id = id
        self.polygon = polygon
        self.source_edge_id = source_edge_id

    def __str__(self):
        return "{},{},{},{}".format(self.id, self.source_edge_id, ";".join([str(x) for x in self.node_collection]), convertCoordListToString(self.polygon))

    def getAttributeDictGEOJSON(self):
        att_dict = {"index" : self.id, "node_collection" : ";".join([str(x) for x in self.node_collection]), "source_edge_id" : self.source_edge_id, "geometry" : Polygon(self.polygon) }
        #print(type(np.array(self.node_collection, dtype='int64')))
        return att_dict

class NetworkEdge():
    def __init__(self, start_node_index, end_node_index, travel_time, travel_distance, edge_index = None, source_edge_id = None, shortcut_def = None, customized_cost_val = None, polyline = None, roadtype = None):
        self.start_node_index = start_node_index
        self.start_node = None
        self.end_node_index = end_node_index
        self.end_node = None

        self.travel_time = travel_time
        self.travel_distance = travel_distance

        self.customized_cost_val = customized_cost_val

        self.id = edge_index
        if self.id is None:
            self.id = "{};{}".format(self.start_node_index, self.end_node_index)
        
        self.source_edge_id = source_edge_id
        self.shortcut_def = shortcut_def

        self.polyline = polyline
        #print(self.polyline)
        self.roadtype = roadtype

    def getStartNodeIndex(self):
        return self.start_node_index

    def getEndNodeIndex(self):
        return self.end_node_index

    def __str__(self):
        s = "{},{},{},{},{},{},{},{}".format(self.start_node_index, self.end_node_index, self.travel_time, self.travel_distance, self.id, self.source_edge_id,self.roadtype,convertCoordListToString(self.polyline))
        return s

    def getAttributeDictGEOJSON(self):
        att_dict = {"from_node" : self.start_node_index, "to_node" : self.end_node_index, "distance" : self.travel_distance, "travel_time" : self.travel_time, "source_edge_id" : self.source_edge_id, "road_type" : self.roadtype, "geometry" : LineString(self.polyline)}
        return att_dict

    def getAttributeDictBaseFile(self):
        att_dict = {"from_node" : self.start_node_index, "to_node" : self.end_node_index, "distance" : self.travel_distance, "travel_time" : self.travel_time, "source_edge_id" : self.source_edge_id}
        return att_dict


#------------------------------------------------------------------------------------------------------------#
# MAIN FUNCTION #
#------------------------------------------------------------------------------------------------------------#
def createNetwork(network_name, bbox=None, polygon=None, by_name=None, network_type='drive', osmnG=None, unit_speeds="kmh", from_crs_to_crs = None):
    """ creates network by extracting data from osmnx
    :param network_name: name of the network after extraction
    :param bbox: bounding box (x_max, x_min, y_max, y_min) in lon-lat coordinates for the network extraction (either bbox, polygon or by_name has to be given)
    :param polygon: shapely polygon with corresponding coordinates for the network extraction (either bbox, polygon or by_name has to be given)
    :param by_name: name of the area for the network extraction (defined by osmnx) (either bbox, polygon or by_name has to be given)
    :param network_type: type of the network (e.g. drive, all; modes defined by osmnx)
    :param osmnG: (optional) osmnx graph object for the network extraction
    :param unit_speeds: unit of the speed which it will be converted to (kmh or mph); kmh per default
    :param from_crs_to_crs: (optional) tuple with the epsg code of the current and the target coordinate system (osm system used if not given)
    """
    nw = NetworkOSMCreator()
    if osmnG is None:
        nw.loadNetworkFromOSM(polygon=polygon, bounding_box=bbox, by_name=by_name, network_type=network_type)
    else:
        nw.networkXGraph = osmnG
    nw.createNetworkFromNetwokXGraph(speed_unit=unit_speeds)
    new_network_folder = os.path.join(NETWORK_DIR, network_name)
    createDir(new_network_folder)
    base_folder = os.path.join(new_network_folder, "base")
    createDir(base_folder)
    if from_crs_to_crs:
        nw.convert_crs(from_crs_to_crs[0], from_crs_to_crs[1])
    nw.convertBaseInformationToCSV(base_folder)
    nw.convertFullInformationToGeoJSON(base_folder)
    nw.saveOriginalOSMGraph(base_folder)
    nw.createCRSfile(base_folder)




if __name__ == "__main__":
    
    # Get Hellevoetsluis by name
    network_name = "hellevoetsluis_network_osm"
    createNetwork(network_name, by_name="Voorne_Putten_Rozenburg", network_type="drive")

    # Get hellevoetsluis by bbox (very slow... takes > 10 minutes)
    # hellevoetsluis_oudenhoorn_bbox = (51.81259324714577,4.071979655408526,51.864565569055316,4.2177201644417295)
    # createNetwork(network_name, bbox=hellevoetsluis_oudenhoorn_bbox, network_type="drive")
