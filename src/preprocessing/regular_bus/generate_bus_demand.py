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
INFRA_DIR = os.path.join(ROOT_DIR, 'data', 'infra', 'hellevoetsluis_infra', 'hellevoetsluis_network_osm')


def fix_costs():
    for folder in os.listdir(os.path.join(REGULAR_BUS_DEMAND_EVAL_DIR, 'line91_week')):
        for file in os.listdir(os.path.join(REGULAR_BUS_DEMAND_EVAL_DIR, 'line91_week', folder)):
            with open(os.path.join(REGULAR_BUS_DEMAND_EVAL_DIR, 'line91_week', folder, file), 'r') as f:
                bus_stats_dict = json.load(f)
                # bus_stats_dict['driver costs [euro]'] = 291.2 * 2 # old: 478.4
                bus_stats_dict['total costs [euro]'] = bus_stats_dict['driver costs [euro]'] + bus_stats_dict['gas costs [euro]']
            with open(os.path.join(REGULAR_BUS_DEMAND_EVAL_DIR, 'line91_week', folder, file), 'w') as f:
                f.write(json.dumps(bus_stats_dict, indent=4))    


def generate_calabro_demand():
    pass


def generate_random_demand():
    boarding_points_df = pd.read_csv(os.path.join(INFRA_DIR, 'boarding_points_stops.csv'))
    start_time = 30000
    end_time = 86400
    requests = []
    for i in range(500):
        
        request = {
            "request_id": i,
            "start": boarding_points_df.sample(1)['node_index'].values[0],
            "end": boarding_points_df.sample(1)['node_index'].values[0],
            "rq_time": start_time + (end_time - start_time) * random.uniform(0, 1),
        }
        requests.append(request)
    requests_df = pd.DataFrame(requests)
    requests_df.to_csv(os.path.join(DEMAND_DIR, 'avlm_demo_sim.csv'), index=False)


def recreate_demand_from_user_stats():

    user_stats = pd.read_csv(os.path.join(RESULT_DIR, 'greater_hellevoetsluis', 'planned', '1.0', 'sample_0', 'IB_900_D+UT0.45_FB_4', '1_user-stats.csv'))
    user_stats['start'] = user_stats['start'].apply(lambda x: x.split(';')[0])
    user_stats['end'] = user_stats['end'].apply(lambda x: x.split(';')[0])
    user_stats['request_id'] = range(len(user_stats))
    user_stats[['request_id', 'rq_time', 'start', 'end']].to_csv(
        os.path.join(DEMAND_DIR, 'greater_hellevoetsluis', '1.0', 'sample_0.csv'), 
        index=False
    )


def fix_outlier_demands():

    demand_scalars = [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]
    for a in demand_scalars:
        for i in range(25):
            demand_df = pd.read_csv(os.path.join(DEMAND_DIR, 'greater_hellevoetsluis', f"{a}", f"sample_{i}.csv"))
            for index, row in demand_df.iterrows():
                if row['rq_time'] < 14400 or row['rq_time'] > 90000:
                    demand_df.at[index, 'rq_time'] = random.randint(21600, 86400)
            demand_df.to_csv(os.path.join(DEMAND_DIR, 'greater_hellevoetsluis', f"{a}", f"sample_{i}.csv"), index=False)


if __name__ == "__main__":

    n_samples = 10
    # demand_scalar = [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]
    # demand_scalar = [3.0, 4.0, 5.0]
    demand_scalar = [6.0, 7.0, 8.0, 9.0, 10.0]

    # BusLine91aweek = OneWayRegularBusLine('line91a_week')
    # line91a_sample = BusLine91aweek.sample_OD_pairs()
    # print(BusLine91aweek.create_requests_from_OD_sample(line91a_sample))
    # print(BusLine91aweek.evaluate_OD_sample(line91a_sample))

    multibusline = MultipleRegularBusLine(['line91a_week', 'line91b_week'])
    multibusline.generate_demand_samples('line91_week', demand_scalar, n_samples)
    
    # multibusline = MultipleRegularBusLine(['line102a_week', 'line102b_week'])
    # multibusline.generate_demand_samples('line102_week', demand_scalar, n_samples)

    # multibusline = MultipleRegularBusLine(['line105a_week', 'line105b_week'])
    # multibusline.generate_demand_samples('line105_week', demand_scalar, n_samples)

    # multibusline = MultipleRegularBusLine(['line106a_week', 'line106b_week'])
    # multibusline.generate_demand_samples('line106_week', demand_scalar, n_samples)

    # multibusline = MultipleRegularBusLine(['line91a_week', 'line91b_week', 
    #                                     #    'line102a_week', 'line102b_week', 
    #                                        'line105a_week_s', 'line105b_week_s', 
    #                                        'line106a_week', 'line106b_week'])
    # multibusline.generate_demand_samples('greater_hellevoetsluis', demand_scalar, n_samples)

    # generate_random_demand()

    # recreate_demand_from_user_stats()
    