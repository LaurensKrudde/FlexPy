import os
import json
import pandas as pd
import random

from MultipleRegularBusLine import MultipleRegularBusLine


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DEMAND_DIR = os.path.join(ROOT_DIR, 'data', 'demand', 'hellevoetsluis', 'matched', 'hellevoetsluis_network_osm')
REGULAR_BUS_DATA_DIR = os.path.join(ROOT_DIR, 'data', 'regular_bus')
REGULAR_BUS_DEMAND_EVAL_DIR = os.path.join(ROOT_DIR, 'data', 'demand', 'hellevoetsluis', 'regular_bus_eval')
NETWORK_DIR = os.path.join(ROOT_DIR, "data", "networks")
VEHICLE_DIR = os.path.join(ROOT_DIR, 'data', 'vehicles')
RESULT_DIR = os.path.join(ROOT_DIR, 'studies', 'hellevoetsluis', 'results')


def create_folder_if_not_exists(path):
    if not os.path.exists(path):
        os.mkdir(path)


def create_flag_requests(folder, demand_scalars, number_of_samples):

    for a in demand_scalars:

        create_folder_if_not_exists(os.path.join(DEMAND_DIR, folder, "flag"))
        create_folder_if_not_exists(os.path.join(DEMAND_DIR, folder, "flag", str(a)))
        for i in range(number_of_samples):
            
            demand_df = pd.read_csv(os.path.join(DEMAND_DIR, folder, str(a), f'sample_{i}.csv')).drop(columns=['bus_end_tt', 'bus_tt'])

            demand_df['flag'] = [True for _ in range(len(demand_df))]

            demand_df.to_csv(os.path.join(DEMAND_DIR, folder, "flag", str(a), f'sample_{i}.csv'), index=False)

            # Get regular bus eval and save in results folder
            with open(os.path.join(ROOT_DIR, 'data', 'demand', 'hellevoetsluis', 'regular_bus_eval', folder, str(a), f'sample_{i}.json'), 'r') as f:
                bus_stats_dict = json.load(f)
            
            create_folder_if_not_exists(os.path.join(ROOT_DIR, 'data', 'demand', 'hellevoetsluis', 'regular_bus_eval', folder, "flag"))
            create_folder_if_not_exists(os.path.join(ROOT_DIR, 'data', 'demand', 'hellevoetsluis', 'regular_bus_eval', folder, "flag", str(a)))
            with open(os.path.join(ROOT_DIR, 'data', 'demand', 'hellevoetsluis', 'regular_bus_eval', folder, "flag", str(a), f'sample_{i}.json'), 'w') as f:
                f.write(json.dumps(bus_stats_dict, indent=4))



def create_test_scenario():

    rq0 = {
        'request_id': 0,
        'rq_time': 40070,
        'start': 4451,
        'end': 616,
        'flag': True
    }
    rq1 = {
        'request_id': 1,
        'rq_time': 40000,
        'start': 5754,
        'end': 5283,
        'flag': True
    }

    demand = pd.DataFrame([rq0, rq1])

    demand.to_csv(os.path.join(DEMAND_DIR, 'line91_week', 'flag', 'dummy', 'sample_0.csv'), index=False)


if __name__ == "__main__":

    folder = 'line91_week'
    # folder = 'greater_hellevoetsluis'
    # demand_scalars = [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]#, 
    # demand_scalars = [3.0, 4.0, 5.0]
    demand_scalars = [6.0, 7.0, 8.0, 9.0, 10.0]
    # demand_scalars = [0.25]
    number_of_samples = 10

    create_flag_requests(folder, demand_scalars, number_of_samples)

    # create_test_scenario()
