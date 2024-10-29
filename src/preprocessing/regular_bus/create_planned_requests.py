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


def create_planned_requests(folder, new_folder, demand_scalars, number_of_samples):

    # Minimum time between reservation and pickup
    MINIMUM_RESERVATION_TIME = 30 * 60

    # Time between earliest and latest pickup time
    PICKUP_WINDOW = 2 * 60 * 60
    
    for a in demand_scalars:

        create_folder_if_not_exists(os.path.join(DEMAND_DIR, folder, new_folder))
        if not os.path.exists(os.path.join(DEMAND_DIR, folder, new_folder, str(a))):
            os.mkdir(os.path.join(DEMAND_DIR, folder, new_folder, str(a)))

        for i in range(number_of_samples):
            
            demand_df = pd.read_csv(os.path.join(DEMAND_DIR, folder, str(a), f'sample_{i}.csv')).drop(columns=['bus_end_tt', 'bus_tt'])

            demand_df['earliest_pickup_time'] = demand_df['rq_time']
            # demand_df['latest_pickup_time'] = demand_df['rq_time'] + PICKUP_WINDOW

            # demand_df['rq_time'] = [random.randint(29000, ept - MINIMUM_RESERVATION_TIME) for ept in demand_df['earliest_pickup_time']]
            demand_df['rq_time'] = [max(14400, ept - MINIMUM_RESERVATION_TIME) for ept in demand_df['earliest_pickup_time']]
            # demand_df['rq_time'] = [28800 for _ in demand_df['earliest_pickup_time']]

            demand_df['reservation_time'] = demand_df['earliest_pickup_time'] - demand_df['rq_time']
            demand_df.sort_values(by='earliest_pickup_time', inplace=True)
            demand_df['request_id'] = range(len(demand_df))

            demand_df.to_csv(os.path.join(DEMAND_DIR, folder, new_folder, str(a), f'sample_{i}.csv'), index=False)

            # Get regular bus eval and save in results folder
            with open(os.path.join(ROOT_DIR, 'data', 'demand', 'hellevoetsluis', 'regular_bus_eval', folder, str(a), f'sample_{i}.json'), 'r') as f:
                bus_stats_dict = json.load(f)
            
            create_folder_if_not_exists(os.path.join(ROOT_DIR, 'data', 'demand', 'hellevoetsluis', 'regular_bus_eval', folder, new_folder))
            create_folder_if_not_exists(os.path.join(ROOT_DIR, 'data', 'demand', 'hellevoetsluis', 'regular_bus_eval', folder, new_folder, str(a)))
            with open(os.path.join(ROOT_DIR, 'data', 'demand', 'hellevoetsluis', 'regular_bus_eval', folder, new_folder, str(a), f'sample_{i}.json'), 'w') as f:
                f.write(json.dumps(bus_stats_dict, indent=4))


if __name__ == "__main__":

    # folder = 'line91_week'
    # new_folder = 'day_ahead'
    # # demand_scalars = [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 3.0, 4.0, 5.0]
    # demand_scalars = [1.0]
    # number_of_samples = 25

    folder = 'greater_hellevoetsluis'
    new_folder = 'planned'
    # demand_scalars = [1.0]
    demand_scalars = [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]
    number_of_samples = 25

    create_planned_requests(folder, new_folder, demand_scalars, number_of_samples)
