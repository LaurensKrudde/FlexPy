# -------------------------------------------------------------------------------------------------------------------- #
# external imports
# ----------------
import sys
import traceback
import pandas as pd
import multiprocessing as mp

# src imports
# -----------
import src.misc.config as config
from src.misc.init_modules import load_simulation_environment
from src.misc.globals import *
from src.evaluation.standard import create_eval_overview


# main functions
# --------------
def run_single_simulation(scenario_parameters):
    SF = load_simulation_environment(scenario_parameters)
    if scenario_parameters.get("bugfix", False):
        try:
            SF.run()
        except:
            traceback.print_exc()
    else:
        SF.run()

    # Get regular bus eval and save in results folder
    bus_file = os.path.join(MAIN_DIR, 'data', 'demand', 'hellevoetsluis', 'regular_bus_eval', f"{scenario_parameters['rq_file'][:-4]}.json")
    if os.path.isfile(bus_file):
        with open(bus_file, 'r') as f:
            bus_stats_dict = json.load(f)
        with open(os.path.join(MAIN_DIR, 'studies', 'hellevoetsluis', 'results', scenario_parameters['scenario_name'], 'regular_bus_eval.json'), 'w') as f:
            f.write(json.dumps(bus_stats_dict, indent=4))
    else:
        print(f"Regular bus evaluation not found. Skipping ...")


def run_scenarios(constant_config_file, scenario_file, n_parallel_sim=1, n_cpu_per_sim=1, evaluate=1, log_level="info",
                  keep_old=False, continue_next_after_error=False, force_run=False):

    constant_cfg = config.ConstantConfig(constant_config_file)
    scenario_cfgs = config.ScenarioConfig(scenario_file)
    const_abs = os.path.abspath(constant_config_file)
    study_name = os.path.basename(os.path.dirname(os.path.dirname(const_abs)))
    constant_cfg[G_STUDY_NAME] = study_name
    constant_cfg["n_cpu_per_sim"] = n_cpu_per_sim
    constant_cfg["evaluate"] = evaluate
    constant_cfg["log_level"] = log_level
    constant_cfg["keep_old"] = keep_old

    # combine constant and scenario parameters into verbose scenario parameters
    for i, scenario_cfg in enumerate(scenario_cfgs):
        scenario_cfgs[i] = constant_cfg + scenario_cfg

    # perform simulation(s)
    print(f"Simulation of {len(scenario_cfgs)} scenarios on {n_parallel_sim} processes with {n_cpu_per_sim} cpus per simulation ...")
    if n_parallel_sim == 1:
        for i, scenario_cfg in enumerate(scenario_cfgs):

            if force_run:
                run_single_simulation(scenario_cfg)
            else:
                results_already_exists = False
                results_uptodate = False
                if os.path.isfile(os.path.join(MAIN_DIR, 'studies', 'hellevoetsluis', 'results', scenario_cfg['scenario_name'], 'regular_bus_eval.json')):
                    # print(f"Results for {scenario_cfg['scenario_name']} already exist. Checking ...")
                    results_already_exists = True
                    
                    # Check whether simulated demand is equal to current (newest) demand
                    demand_df = pd.read_csv(os.path.join(MAIN_DIR, 'data', 'demand', 'hellevoetsluis', 'matched', 'hellevoetsluis_network_osm', f"{scenario_cfg['rq_file']}"))
                    demand_o = [o for o in demand_df['start']] 
                    demand_d = [d for d in demand_df['end']]
                    
                    user_df = pd.read_csv(os.path.join(MAIN_DIR, 'studies', 'hellevoetsluis', 'results', f"{scenario_cfg['scenario_name']}", '1_user-stats.csv')).sort_values(by='request_id')
                    sim_o = [int(o.split(';')[0]) for o in user_df['start']]
                    sim_d = [int(d.split(';')[0]) for d in user_df['end']]

                    if demand_o == sim_o and demand_d == sim_d: 
                        results_uptodate = True
                    elif len(demand_o) != len(sim_o):
                        print("Lengths of demand and simulation do not match.")
                    else:
                        for i in range(len(demand_o)):
                            if demand_o[i] != sim_o[i] or demand_d[i] != sim_d[i]:
                                print(i)
                                
                    

                if results_already_exists and results_uptodate:
                    print(f"Existing results for {scenario_cfg['scenario_name']} are correct. Skipping ...")
                    continue
                elif results_already_exists and not results_uptodate:
                    print(f"Existing results for {scenario_cfg['scenario_name']} are outdated. Running simulation ...")
                    print("Running scenario {}/{}: {}".format(i + 1, len(scenario_cfgs), scenario_cfg['scenario_name']))
                    run_single_simulation(scenario_cfg)
                else:
                    print(f"No results found for {scenario_cfg['scenario_name']}. Running simulation ...")
                    print("Running scenario {}/{}: {}".format(i + 1, len(scenario_cfgs), scenario_cfg['scenario_name']))
                    run_single_simulation(scenario_cfg)


    else:
        if n_cpu_per_sim == 1:
            mp_pool = mp.Pool(n_parallel_sim)
            mp_pool.map(run_single_simulation, scenario_cfgs)
        else:
            n_scenarios = len(scenario_cfgs)
            rest_scenarios = n_scenarios
            current_scenario = 0
            while rest_scenarios != 0:
                if rest_scenarios >= n_parallel_sim:
                    par_processes = [None for i in range(n_parallel_sim)]
                    for i in range(n_parallel_sim):
                        par_processes[i] = mp.Process(target=run_single_simulation, args=(scenario_cfgs[current_scenario],))
                        current_scenario += 1
                        par_processes[i].start()
                    for i in range(n_parallel_sim):
                        par_processes[i].join()
                        rest_scenarios -= 1
                else:
                    par_processes = [None for i in range(rest_scenarios)]
                    for i in range(rest_scenarios):
                        par_processes[i] = mp.Process(target=run_single_simulation, args=(scenario_cfgs[current_scenario],))
                        current_scenario += 1
                        par_processes[i].start()
                    for i in range(rest_scenarios):
                        par_processes[i].join()
                        rest_scenarios -= 1

# -------------------------------------------------------------------------------------------------------------------- #
# ----> you can replace the following part by your respective if __name__ == '__main__' part for run_private*.py <---- #
# -------------------------------------------------------------------------------------------------------------------- #

# global variables for testing
# ----------------------------
MAIN_DIR = os.path.dirname(__file__)
MOD_STR = "MoD_0"
MM_STR = "Assertion"
LOG_F = "standard_bugfix.log"

from studies.hellevoetsluis.results.create_overview import create_overview

# -------------------------------------------------------------------------------------------------------------------- #
if __name__ == "__main__":
    mp.freeze_support()

    if len(sys.argv) > 1:
        run_scenarios(*sys.argv)
    else:
        import time
        # touch log file
        with open(LOG_F, "w") as _:
            pass

        
    # Line 91 week multiple samples
    study_name = "hellevoetsluis"
    scs_path = os.path.join(MAIN_DIR, "studies", study_name, "scenarios")
    log_level = "info"
    



    cc = os.path.join(scs_path, "constant_line91_week.csv")
    # cc = os.path.join(scs_path, "constant_greater_hellevoetsluis.csv")
    scenario_file = 'line91_week.csv'




    sc = os.path.join(scs_path, scenario_file)
    run_scenarios(cc, sc, n_cpu_per_sim=1, n_parallel_sim=1, force_run=False, log_level="info")
    create_overview(scenario_file)
