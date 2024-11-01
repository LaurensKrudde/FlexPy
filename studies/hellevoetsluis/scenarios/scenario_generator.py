import pandas as pd
import os
import json

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
SCENARIOS_DIR = os.path.join(ROOT_DIR, 'studies', 'hellevoetsluis', 'scenarios')
DEMAND_DIR = os.path.join(ROOT_DIR, 'data', 'demand', 'hellevoetsluis', 'matched', 'hellevoetsluis_network_osm')


# Abbreviations
AB = {
    "SimpleRepositioning": "SR",
    "flex_bus": "FB",
    "taxi": "TX",
    "func_key:IRS_study_standard": "D+WT",
    "func_key:user_times": "UT",
    "func_key:1_wait_and_1_travel_time_users": "1W1TT",
    "func_key:1_wait_and_2_travel_time_users": "1W2TT",
    "func_key:1_wait_and_3_travel_time_users": "1W3TT",
    "func_key:1_wait_and_4_travel_time_users": "1W4TT",
    "func_key:1_wait_and_5_travel_time_users": "1W5TT",
    "reservation": "R",
    "func_key:distance_and_user_times;vot:0.45": "D+UT0.45",
    "func_key:distance_and_user_times_with_walk;vot:0.45": "D+UTW0.45",
}


NAME = "on_demand_IR_vs_IB"

# Number of simulations per scenario
N_SIMULATIONS = 10

### 1. Demand ###
DEMAND_NAME = 'line91_week'
DEMAND_SCALARS = [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 3.0, 4.0, 5.0]
# DEMAND_SCALARS = [0.25, 0.5, 0.75, 1.0, 1.25, 1.5]
# DEMAND_SCALARS = [3.0]
# DEMAND_SCALARS = ['dummy']
DEMAND_TYPE = ['on-demand'] # ['on-demand', 'reservation'] #['wave', 'on-demand'] # ['reservation', 'on-demand']

### 2. Supply ###
VEHICLE_TYPE = ["flex_bus"]#, "taxi"]
NUMBER_OF_VEHICLES = [1, 2]
OPTIMIZATION = ["IR", "IB"]#, "BO"]#, "IB"]#, "BO"]
OBJECTIVE = ["func_key:user_times"] # ["func_key:distance_and_user_times;vot:0.45"] #["func_key:1_wait_and_1_travel_time_users"] #["func_key:user_times", "func_key:IRS_study_standard"] #, "func_key:distance_and_user_times"]
MAX_WAIT_TIME = [900]
# REPOSITINING = [None]#, "SimpleRepositioning"]


def create_config_str(opt, wait_time, objective, vehicle_name, n_vehicles, repo):
    configs_str = f"{opt}_{wait_time}_{AB[objective]}_{AB[vehicle_name]}_{n_vehicles}"
    if repo:
        configs_str += f"_{AB[repo]}"
    return configs_str


if __name__ == "__main__":

    scenarios = []
    
    for demand_type in DEMAND_TYPE:
        for opt in OPTIMIZATION:
            for wait_time in MAX_WAIT_TIME:
                for objective in OBJECTIVE:
                    for vehicle_name in VEHICLE_TYPE:
                        for n_vehicles in NUMBER_OF_VEHICLES:
                            for a in DEMAND_SCALARS:
                                for i in range(N_SIMULATIONS):

                                    d = {}

                                    # if demand_type == 'on-demand':
                                    #     objective = "func_key:user_times"
                                    #     configs_str = "IR_UT_FB_1"
                                    # elif demand_type == 'wave':
                                    #     objective = "func_key:1_wait_and_2_travel_time_users"
                                    #     configs_str = "IR_7200_1W1TT_FB_1"

                                    configs_str = create_config_str(opt, wait_time, objective, vehicle_name, n_vehicles, None)

                                    # Default values
                                    d['op_max_wait_time'] = wait_time
                                    d['op_max_detour_time_factor'] = 75
                                    d['op_reservation_module'] = "RollingHorizon"
                                    d['rq_type'] = "BasicRequest"

                                    if n_vehicles == 2 and DEMAND_NAME == 'line91_week':
                                        d['op_depot_file'] = 'depots.csv'
                                        d['op_dyn_fs_method'] = 'TimeBasedFS'
                                        d['op_act_fs_file'] = "line91.csv"
                                        d['avg_fs'] = 1.555
                                    elif n_vehicles == 1:
                                        d['avg_fs'] = 1.0

                                    if demand_type == "reservation":
                                        d['user_max_decision_time'] = 60
                                        # d['rq_type'] = "IndividualConstraintRequest"
                                        # d['op_rh_reservation_max_routes'] = 50
                                        # d['op_short_term_horizon'] = 900
                                        # d['op_max_wait_time'] = 1800
                                        # d['op_res_approach_buffer_time'] = 30
                                        # d['op_res_assignment_horizon'] = 900

                                    elif demand_type == "wave":
                                        d['op_max_detour_time_factor'] = 10000
                                        # d['op_reservation_module'] = "RollingHorizon"
                                        # d['op_rh_reservation_max_routes'] = 40
                                        # d['op_short_term_horizon'] = 900

                                    else:
                                        d['rq_type'] = "BasicRequest"
                                        d['user_max_decision_time'] = 0
                                        # d['op_rh_reservation_max_routes'] = None
                                        # d['op_short_term_horizon'] = None

                                    # if repo:
                                    #     d['op_repo_method'] = repo
                                    #     d['op_repo_timestep'] = 300
                                    #     d['op_repo_lock'] = False
                                    #     d['op_repo_horizons'] = "I believe this is not used"
                                    
                                    if opt == 'IR':
                                        d['op_module'] = 'PoolingIRSOnly'
                                        d['sim_env'] = 'ImmediateDecisionsSimulation'
                                    elif opt == 'IB':
                                        d['op_module'] = 'PoolingIRSAssignmentBatchOptimization'
                                        d['sim_env'] = 'ImmediateDecisionsSimulation'
                                        # d['op_max_wait_time'] = 1800
                                        # d['op_max_detour_time_factor'] = 50
                                        # d['op_reoptimisation_timestep'] = 600
                                    elif opt == 'BO':
                                        d['op_module'] = 'RidePoolingBatchAssignmentFleetcontrol'
                                        d['sim_env'] = 'BatchOfferSimulation'
                                        # d['op_max_wait_time'] = 1800
                                        # d['op_max_detour_time_factor'] = 40
                                        # d['op_reoptimisation_timestep'] = 60


                                    if demand_type == 'reservation':
                                        d['scenario_name'] = f"{DEMAND_NAME}/planned/{a}/sample_{i}/{configs_str}/"
                                        d['rq_file'] = f"{DEMAND_NAME}/planned/{a}/sample_{i}.csv"
                                    elif demand_type == 'wave':
                                        d['scenario_name'] = f"{DEMAND_NAME}/flag/{a}/sample_{i}/{configs_str}/"
                                        d['rq_file'] = f"{DEMAND_NAME}/flag/{a}/sample_{i}.csv"
                                    else:
                                        d['scenario_name'] = f"{DEMAND_NAME}/{a}/sample_{i}/{configs_str}/"
                                        d['rq_file'] = f"{DEMAND_NAME}/{a}/sample_{i}.csv"

                                    d['demand_folder'] = DEMAND_NAME
                                    d['demand_type'] = demand_type
                                    d['demand_scalar'] = a
                                    d['op_fleet_composition'] = f"{vehicle_name}:{n_vehicles}" 
                                    d['op_vr_control_func_dict'] = objective
                                    d['demand_scalar'] = a
                                    d['sample'] = f"sample_{i}"
                                    d['config_str'] = configs_str

                                    scenarios.append(d)


    pd.DataFrame(scenarios).to_csv(os.path.join(SCENARIOS_DIR, f"{NAME}.csv"))
