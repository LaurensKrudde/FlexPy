import os
import pandas as pd
import numpy as np

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
NETWORK_PATH = os.path.join(ROOT_DIR, "data", "networks")
DEMAND_PATH = os.path.join(ROOT_DIR, "data", "demand")
OUTPUT_PATH = os.path.join(DEMAND_PATH, "example_demand", "matched")

def generate_fully_random_demand(network_name, number_of_requests):

    NODES_PATH = os.path.join(NETWORK_PATH, network_name, "base", "nodes.csv")
    nodes_df = pd.read_csv(NODES_PATH, index_col=False)

    request_df = pd.DataFrame()
    request_df['request_id'] = np.arange(0, number_of_requests)
    request_df['rq_time'] = np.sort(np.random.randint(0, 7200, size=number_of_requests))
    request_df['start'] = nodes_df.sample(n=number_of_requests)['node_index'].values
    request_df['end'] = nodes_df.sample(n=number_of_requests)['node_index'].values

    OUTPUT_DEMAND_PATH = os.path.join(OUTPUT_PATH, network_name, "example.csv")

    request_df.to_csv(OUTPUT_DEMAND_PATH, index=False)

    return -1


if __name__ == "__main__":

    network_name = "hellevoetsluis_network_osm"

    generate_fully_random_demand(network_name, 100)
