import pandas as pd
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
SCENARIOS_DIR = os.path.join(ROOT_DIR, 'studies', 'hellevoetsluis', 'scenarios')
DEMAND_DIR = os.path.join(ROOT_DIR, 'data', 'demand', 'hellevoetsluis', 'matched', 'hellevoetsluis_network_osm')

if __name__ == "__main__":

    demand_name = 'line102_week'
    demand_df = pd.read_csv(os.path.join(DEMAND_DIR, f"{demand_name}.csv"))
    start_time = min(demand_df['rq_time']) - 10 * 60
    end_time = max(demand_df['rq_time']) + 30 * 60

    n_DRT_vehicles = range(2,4)
    n_taxis = range(2,4)

    op_max_wait_time = 1800

    scenarios = []

    for i in n_DRT_vehicles:
        d = {}
        d['scenario_name'] = f"{demand_name}_flex_{i}"
        d['op_fleet_composition'] = f"flex_bus:{i}"
        scenarios.append(d)

    for i in n_taxis:
        d = {}
        d['scenario_name'] = f"{demand_name}_taxi_{i}"
        d['op_fleet_composition'] = f"taxi:{i}"
        scenarios.append(d)

    for d in scenarios:
        d['rq_file'] = f"{demand_name}.csv"
        # d['start_time'] = start_time
        # d['end_time'] = end_time
        d['op_max_wait_time'] = op_max_wait_time

    pd.DataFrame(scenarios).to_csv(os.path.join(SCENARIOS_DIR, f"{demand_name}.csv"))
