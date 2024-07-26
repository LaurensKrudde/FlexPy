import pandas as pd
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
SCENARIOS_DIR = os.path.join(ROOT_DIR, 'studies', 'hellevoetsluis', 'scenarios')
DEMAND_DIR = os.path.join(ROOT_DIR, 'data', 'demand', 'hellevoetsluis', 'matched', 'hellevoetsluis_network_osm')


OPTIMIZATION = ["IR", "BO"]
REPOSITINING = [None, "SimpleRepositioning"]
OBJECTIVE = ["func_key:IRS_study_standard"]
DEMAND_SCALAR = [
    [1.0],
    [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]
]
VEHICLE_TYPE = ["flex_bus", "taxi"]


# Abbreviations
AB = {
    "SimpleRepositioning": "SR",
    "flex_bus": "FB",
    "taxi": "TX",
    "func_key:IRS_study_standard": "D+WT",
}


if __name__ == "__main__":

    scenarios = []

    # Number of simulations per scenario
    n = 25

    ### 1. Demand ###
    demand_name = 'line91_week'
    demand_scalars = [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]
    # demand_scalars = [0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0]
    # demand_scalars = [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 3.0, 4.0, 5.0]

    ### 2. Supply ###
    vehicle_name = 'taxi' # 'flex_bus'
    n_vehicles = 2
    active_fleet_size = "line91.csv"

    ### 3. Operator strategy ###
    opt = 'BO'
    objective = 'func_key:IRS_study_standard'
    repo = None #'SimpleRepositioning' 

    for a in demand_scalars:
        for i in range(n):

            d = {}

            # Parameters
            configs_str = f"{opt}_{AB[objective]}_{AB[vehicle_name]}_{n_vehicles}"
            
            if repo:
                configs_str += f"_{AB[repo]}"
                d['op_repo_method'] = repo
                d['op_repo_timestep'] = 300
                d['op_repo_lock'] = False
                d['op_repo_horizons'] = "I believe this is not used"
            
            if opt == 'IR':
                d['op_module'] = 'PoolingIRSOnly'
                d['sim_env'] = 'ImmediateDecisionsSimulation'
            elif opt == 'BO':
                d['op_module'] = 'RidePoolingBatchAssignmentFleetcontrol'
                d['sim_env'] = 'BatchOfferSimulation'
                d['op_max_wait_time'] = 1800
                d['op_max_detour_factor'] = 40          

            d['scenario_name'] = f"{demand_name}/{a}/sample_{i}/{configs_str}/"
            d['rq_file'] = f"{demand_name}/{a}/sample_{i}.csv"
            d['demand_scalar'] = a
            d['op_fleet_composition'] = f"{vehicle_name}:{n_vehicles}" 
            d['op_vr_control_func_dict'] = objective
            d['op_act_fs_file'] = active_fleet_size

            scenarios.append(d)

    pd.DataFrame(scenarios).to_csv(os.path.join(SCENARIOS_DIR, f"{configs_str}.csv"))
