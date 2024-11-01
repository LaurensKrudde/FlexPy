import pandas as pd
import os
import json
import itertools

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
SCENARIOS_DIR = os.path.join(ROOT_DIR, 'studies', 'hellevoetsluis', 'scenarios')
DEMAND_DIR = os.path.join(ROOT_DIR, 'data', 'demand', 'hellevoetsluis', 'matched', 'hellevoetsluis_network_osm')


AB = {
    "SimpleRepositioning": "SR",
    "flex_bus": "FB",
    "flex_bus_4": "FB4",
    "flex_bus_12": "FB12",
    "flex_bus_16": "FB16",
    "flex_bus_20": "FB20",
    "taxi": "TX",
    "func_key:IRS_study_standard": "D+WT",
    "func_key:user_times": "UT",
    "func_key:distance_and_user_times;vot:0.45": "D+UT0.45",
    "func_key:distance_and_user_times_with_walk;vot:0.45": "D+UTW0.45",
}

veh2cap = {
    "flex_bus": 8,
    "flex_bus_4": 4,
    "flex_bus_12": 12,
    "flex_bus_16": 16,
    "flex_bus_20": 20,
    "taxi": 1,
}


def create_config_str(opt, wait_time, objective, vehicle_name, n_vehicles, obj_str=None):
    if obj_str:
        return f"{opt}_{wait_time}_{obj_str}_{AB[vehicle_name]}_{n_vehicles}"
    else:
        return f"{opt}_{wait_time}_{AB[objective]}_{AB[vehicle_name]}_{n_vehicles}"


def create_scenarios(scenario_name):

    with open(os.path.join(SCENARIOS_DIR, 'scenario_configs.json')) as f:
        scenario_configs = json.load(f)
        config = scenario_configs[scenario_name]

    scenarios = []

    demand_name = config['demand_name']
    
    for demand_type in config['demand_types']:
        for sim_env in config['sim_env']:
            for wait_time in config['max_wait_times']:
                for dc in config['obj_weights']['dc']:
                    for vot in config['obj_weights']['vot']:
                        for vehicle_name in config['vehicle_types']:
                            for a in config['demand_scalars']:
                                for n_vehicles in config['n_vehicles']:
                                    for i in range(config['n_simulations']):

                                        d = {}

                                        # if dc == 0 and vot == 0:
                                        #     continue

                                        objective = f"func_key:distance_and_user_times_man;dc:{dc/1000};vot:{vot}"
                                        obj_str = f"D{dc}UT{vot}"

                                        configs_str = create_config_str(sim_env, wait_time, objective, vehicle_name, n_vehicles, obj_str)

                                        # Default values
                                        d['op_max_wait_time'] = wait_time
                                        d['op_max_detour_time_factor'] = 75
                                        d['op_reservation_module'] = "RollingHorizon"
                                        d['rq_type'] = "BasicRequest"

                                        if n_vehicles == 2 and demand_name == 'line91_week':
                                            d['op_depot_file'] = 'depots.csv'
                                            d['op_dyn_fs_method'] = 'TimeBasedFS'
                                            d['op_act_fs_file'] = "line91.csv"
                                            d['avg_fs'] = 1.555
                                        elif n_vehicles == 1:
                                            d['avg_fs'] = 1.0

                                        if demand_type == "reservation":
                                            # d['rq_type'] = "IndividualConstraintRequest"
                                            d['op_rh_reservation_max_routes'] = 50
                                            d['op_short_term_horizon'] = config['op_short_term_horizon']
                                            # d['op_max_wait_time'] = 1800
                                            # d['op_res_approach_buffer_time'] = 30
                                            # d['op_res_assignment_horizon'] = 900
                                            

                                        elif demand_type == "day_ahead":
                                            # d['op_reservation_module'] = "RollingHorizon"
                                            # d['op_rh_reservation_max_routes'] = 40
                                            d['op_short_term_horizon'] = 1e6

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
                                        
                                        if sim_env == 'IR':
                                            d['op_module'] = 'PoolingIRSOnly'
                                            d['sim_env'] = 'ImmediateDecisionsSimulation'
                                            d['user_max_decision_time'] = 0
                                        elif sim_env == 'IB':
                                            d['op_module'] = 'PoolingIRSAssignmentBatchOptimization'
                                            d['sim_env'] = 'ImmediateDecisionsSimulation'
                                            d['user_max_decision_time'] = 0
                                            d['op_reoptimisation_timestep'] = config['op_reoptimisation_timestep']
                                        elif sim_env == 'BO':
                                            d['op_module'] = 'RidePoolingBatchAssignmentFleetcontrol'
                                            d['sim_env'] = 'BatchOfferSimulation'
                                            d['user_max_decision_time'] = 60
                                            d['op_reoptimisation_timestep'] = config['op_reoptimisation_timestep']


                                        if demand_type == 'reservation':
                                            d['scenario_name'] = f"{demand_name}/planned/{a}/sample_{i}/{configs_str}/"
                                            d['rq_file'] = f"{demand_name}/planned/{a}/sample_{i}.csv"
                                        elif demand_type == 'day_ahead':
                                            d['scenario_name'] = f"{demand_name}/day_ahead/{a}/sample_{i}/{configs_str}/"
                                            d['rq_file'] = f"{demand_name}/day_ahead/{a}/sample_{i}.csv"
                                        elif demand_type == 'wave':
                                            d['scenario_name'] = f"{demand_name}/flag/{a}/sample_{i}/{configs_str}/"
                                            d['rq_file'] = f"{demand_name}/flag/{a}/sample_{i}.csv"
                                        else:
                                            d['scenario_name'] = f"{demand_name}/{a}/sample_{i}/{configs_str}/"
                                            d['rq_file'] = f"{demand_name}/{a}/sample_{i}.csv"

                                        d['demand_folder'] = demand_name
                                        d['demand_type'] = demand_type
                                        d['demand_scalar'] = a
                                        d['op_fleet_composition'] = f"{vehicle_name}:{n_vehicles}" 
                                        d['op_vr_control_func_dict'] = objective
                                        d['demand_scalar'] = a
                                        d['sample'] = f"sample_{i}"
                                        d['config_str'] = configs_str
                                        d['capacity'] = veh2cap[vehicle_name]
                                        d['dc [cent/km]'] = dc
                                        d['vot [euro/h]'] = vot * 3600 / 100

                                        scenarios.append(d)


    pd.DataFrame(scenarios).to_csv(os.path.join(SCENARIOS_DIR, f"{scenario_name}.csv"))


if __name__ == "__main__":
    create_scenarios('greater_hellevoetsluis_objectives')
