import pandas as pd
import os
import numpy as np
import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime

from OneWayRegularBusLine import OneWayRegularBusLine


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DEMAND_DIR = os.path.join(ROOT_DIR, 'data', 'demand', 'hellevoetsluis', 'matched', 'hellevoetsluis_network_osm')
# REGULAR_BUS_DATA_DIR = os.path.join(ROOT_DIR, 'data', 'regular_bus')
REGULAR_BUS_DEMAND_EVAL_DIR = os.path.join(ROOT_DIR, 'data', 'demand', 'hellevoetsluis', 'regular_bus_eval')
# NETWORK_DIR = os.path.join(ROOT_DIR, "data", "networks")
VEHICLE_DIR = os.path.join(ROOT_DIR, 'data', 'vehicles')


class MultipleRegularBusLine():

    def __init__(self, folder_name_list):
        self.RegularBusLine_list = [OneWayRegularBusLine(folder_name) for folder_name in folder_name_list]


    def generate_sample(self, demand_scalar=1.0):

        request_df_list = []

        for bus_line in self.RegularBusLine_list:

            requests = bus_line.sample_OD_pairs(demand_scalar)
            request_df_list.append(requests)
            
        requests = pd.concat(request_df_list, axis=0).reset_index(drop=True)
        requests.index.name = 'request_id'

        return requests


    def create_requests_and_evaluate(self, scenario_name, demand_scalar=1.0, write_to_file=True):

        request_df_list = []
        eval_dict_list = []

        for bus_line in self.RegularBusLine_list:

            requests, eval = bus_line.create_requests_and_evaluate(demand_scalar)

            request_df_list.append(requests)
            eval_dict_list.append(eval)
            
        requests = pd.concat(request_df_list, axis=0).sort_values('rq_time').reset_index(drop=True)
        requests.index.name = 'request_id'
        if write_to_file:
            requests.to_csv(os.path.join(DEMAND_DIR, f'{scenario_name}.csv'))

        evaluation = self.concat_eval(eval_dict_list)
        if write_to_file:
            with open(os.path.join(REGULAR_BUS_DEMAND_EVAL_DIR, f'{scenario_name}.json'), 'w') as f:
                f.write(json.dumps(evaluation, indent=4))

        return requests, evaluation


    def concat_eval(self, eval_dict_list):

        total_n_trips = float(np.sum([eval['n_trips'] for eval in eval_dict_list]))
        total_waiting = float(np.sum([eval['waiting_time'] for eval in eval_dict_list]))
        total_vkm = float(np.sum([eval['total_vkm'] for eval in eval_dict_list]))
        total_time = float(np.sum([eval['total_time'] for eval in eval_dict_list]))
        total_travel_time = float(np.sum([eval['total_travel_time'] for eval in eval_dict_list]))
        occupancy_vkm = float(np.sum([eval['occupancy_vkm'] for eval in eval_dict_list]))
        occupancy_time = float(np.sum([eval['occupancy_time'] for eval in eval_dict_list]))
        empty_vkm = float(np.sum([eval['empty_vkm'] for eval in eval_dict_list]))
        empty_time = float(np.sum([eval['empty_time'] for eval in eval_dict_list]))
        total_passengers = float(np.sum([eval['total_passengers'] for eval in eval_dict_list]))
        shared_rides = float(np.sum([eval['shared_rides'] for eval in eval_dict_list]))
        costs = float(np.sum([eval['costs'] for eval in eval_dict_list]))
        driver_costs = float(np.sum([eval['driver_costs'] for eval in eval_dict_list]))
        gas_costs = float(np.sum([eval['gas_costs'] for eval in eval_dict_list]))
        co2_emissions = float(np.sum([eval['co2_emissions'] for eval in eval_dict_list]))

        return {
            'total_n_trips': total_n_trips,
            # 'total waiting time': total_waiting,
            'avg waiting time [sec]': total_waiting / total_passengers,
            'number users': total_passengers,
            'served users': total_passengers,
            'total driven distance [km]': total_vkm,
            # 'total_time': total_time,
            # 'total_travel_time': total_travel_time,
            'avg travel time [sec]': total_travel_time / total_passengers,
            # 'occupancy_vkm': occupancy_vkm,
            # 'occupancy_time': occupancy_time,
            'occupancy': occupancy_vkm / total_vkm,
            # 'occupancy_time_frac': occupancy_time / total_time,
            # 'empty_vkm': empty_vkm,
            # 'empty_time': empty_time,
            'empty vkm [frac]': empty_vkm / total_vkm,
            # 'empty_time_frac': empty_time / total_time,
            # 'total_passengers': total_passengers,
            # 'shared_rides': shared_rides,
            'shared rides [frac]': shared_rides / total_passengers,
            'total costs [euro]': costs,
            'driver costs [euro]': driver_costs,
            'gas costs [euro]': gas_costs,
            'co2 emissions [kg]': co2_emissions,
        }


    def generate_demand_samples(self, scenario_name, demand_scalar_list, number_of_samples, sample_start_index=0):

        if not os.path.isdir(os.path.join(DEMAND_DIR, scenario_name)):
            os.mkdir(os.path.join(DEMAND_DIR, scenario_name))
            os.mkdir(os.path.join(REGULAR_BUS_DEMAND_EVAL_DIR, scenario_name))

        for a in demand_scalar_list:

            if not os.path.isdir(os.path.join(DEMAND_DIR, scenario_name, f'{a}')):
                os.mkdir(os.path.join(DEMAND_DIR, scenario_name, f'{a}'))
                os.mkdir(os.path.join(REGULAR_BUS_DEMAND_EVAL_DIR, scenario_name, f'{a}'))
                
            for i in range(sample_start_index, sample_start_index + number_of_samples):
                
                    _, _ = self.create_requests_and_evaluate(f'{scenario_name}\\{a}\\sample_{i}', a)

    
    def fix_waiting_times(self, scenario_name, demand_scalar_list, number_of_samples, sample_start_index=0):

        for a in demand_scalar_list:
                
            for i in range(sample_start_index, sample_start_index + number_of_samples):
                
                    _, eval = self.create_requests_and_evaluate(f'{scenario_name}\\{a}\\sample_{i}', a, write_to_file=False)

                    with open(os.path.join(REGULAR_BUS_DEMAND_EVAL_DIR, scenario_name, str(a), f'sample_{i}.json'), 'r') as f:
                        bus_stats_dict = json.load(f)
                        bus_stats_dict['avg waiting time [sec]'] = eval['avg waiting time [sec]']
                    with open(os.path.join(REGULAR_BUS_DEMAND_EVAL_DIR, scenario_name, str(a), f'sample_{i}.json'), 'w') as f:
                        f.write(json.dumps(bus_stats_dict, indent=4))    

    def fix_co2(self, scenario_name, demand_scalar_list, number_of_samples, sample_start_index=0):

        for a in demand_scalar_list:
                
            for i in range(sample_start_index, sample_start_index + number_of_samples):
                
                    _, eval = self.create_requests_and_evaluate(f'{scenario_name}\\{a}\\sample_{i}', a, write_to_file=False)

                    with open(os.path.join(REGULAR_BUS_DEMAND_EVAL_DIR, scenario_name, str(a), f'sample_{i}.json'), 'r') as f:
                        bus_stats_dict = json.load(f)
                        bus_stats_dict['CO2 emissions [kg]'] = eval['co2 emissions [kg]']
                    with open(os.path.join(REGULAR_BUS_DEMAND_EVAL_DIR, scenario_name, str(a), f'sample_{i}.json'), 'w') as f:
                        f.write(json.dumps(bus_stats_dict, indent=4))    

    
    @staticmethod
    def calculate_demand_density(folder, demand_scalar, number_of_samples, start_hour=4, end_hour=26):

        max_density = np.zeros(number_of_samples)
        density95 = np.zeros(number_of_samples)

        fig, axs = plt.subplots(1, 2)

        all_rq_times = np.array([])

        for i in range(number_of_samples):

            sample = pd.read_csv(os.path.join(DEMAND_DIR, folder, str(demand_scalar), f'sample_{i}.csv'))

            rq_times = sample['rq_time'].values

            t, density = rolling_demand_density(rq_times, start_hour, end_hour, time_step=600)

            max_density[i] = np.max(density)
            density95[i] = np.percentile(density, 95)

            axs[0].plot(
                pd.to_datetime(t, unit='s'),
                density, 
                alpha=0.5
            )
            axs[0].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

        
            axs[1].hist(
                pd.to_datetime(rq_times, unit='s'),
                bins=pd.to_datetime([3600 * i for i in range(start_hour, end_hour+1)], unit='s'),
                alpha=0.5,
                # edgecolor='black',
                # linewidth=1,
            )
        axs[1].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        axs[1].set_ylabel('Average number of passengers')

        print(f'Max density {demand_scalar}: {np.max(max_density)}. 95th percentile: {np.mean(density95)}')

        plt.show()

    
    @staticmethod
    def demand_histogram(folder, demand_scalar, number_of_samples, start_hour=8, end_hour=26):

        fig, axs = plt.subplots(1, 1)

        all_rq_times = np.array([])

        for i in range(number_of_samples):

            sample = pd.read_csv(os.path.join(DEMAND_DIR, folder, str(demand_scalar), f'sample_{i}.csv'))

            rq_times = sample['rq_time'].values
            all_rq_times = np.concatenate((all_rq_times, rq_times))

        axs.hist(
            pd.to_datetime(all_rq_times, unit='s'),
            bins=pd.to_datetime([3600 * i for i in range(start_hour, end_hour+1)], unit='s'),
            edgecolor='black',
            linewidth=1,
        )
        axs.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        axs.set_xlabel('Time of day')

        y_vals = axs.get_yticks()
        axs.set_yticklabels(['{:3.0f}'.format(x / number_of_samples) for x in y_vals])
        axs.set_ylabel('Average number of passengers per hour')

        # axs.set_title(f'Demand distribution for {folder} over {number_of_samples} days')
        axs.set_title('Demand density')
        plt.savefig(f"figures/samples/demand_density_{folder}.png")
        plt.show()


    @staticmethod
    def plot_single_demand_sample(folder, demand_scalar, sample_index):

        def rand_jitter(arr):
            stdev = .01 * (max(arr) - min(arr))
            return arr + np.random.randn(len(arr)) * stdev

        sample = pd.read_csv(os.path.join(DEMAND_DIR, folder, str(demand_scalar), f'sample_{sample_index}.csv'))

        bus_stop_info_a = pd.read_csv(os.path.join(ROOT_DIR, 'data', 'regular_bus', 'line91a_week', 'stop_order.csv'))
        bus_stop_info_b = pd.read_csv(os.path.join(ROOT_DIR, 'data', 'regular_bus', 'line91b_week', 'stop_order.csv'))
        bus_stop_info = pd.concat([
            bus_stop_info_a[['name_osm', 'node_index', 'lon', 'lat']], 
            bus_stop_info_b[['name_osm', 'node_index', 'lon', 'lat']]
            ], axis=0).reset_index(drop=True)
        bus_stop_info = bus_stop_info.drop_duplicates()
        bus_stop_info.set_index('node_index', inplace=True)

        fig, axs = plt.subplots(1, 1)

        axs.scatter(
            rand_jitter(sample['rq_time']),
            bus_stop_info.loc[sample['start']]['name_osm'].values,
            # rand_jitter(sample['start']),
            c='tab:blue',
            label='Origin'
        )
        axs.scatter(
            rand_jitter(sample['rq_time']),
            bus_stop_info.loc[sample['start']]['name_osm'].values,
            # rand_jitter(sample['end']),
            c='tab:orange',
            label='Destination'
        )
        plt.legend()
        plt.show()

    
    @staticmethod
    def plot_timetable_trips(busline_a='line105a_week_s', busline_b='line105b_week_s'):

        dwell_time_at_start_end = 6 * 60

        busses_in_use = np.zeros(100000)

        vehicle_stats_dict = pd.read_csv(os.path.join(VEHICLE_DIR, 'flex_bus.csv'), index_col=0).transpose()
        seconds_costs_euro = vehicle_stats_dict['hourly_costs_euro'].iloc[0] / 3600

        # Busline a infos
        trip_times_a = pd.read_csv(os.path.join(ROOT_DIR, 'data', 'regular_bus', busline_a, 'trip_times.csv'))
        bus_stop_info_a = pd.read_csv(os.path.join(ROOT_DIR, 'data', 'regular_bus', busline_a, 'stop_order.csv'))
        drive_time_a = bus_stop_info_a['time_cum_diff'].iloc[-1]

        # Add busses in use for busline a
        for i, row in trip_times_a.iterrows():
            start = row['start_time'] - dwell_time_at_start_end
            end = row['start_time'] + drive_time_a + dwell_time_at_start_end
            busses_in_use[start:end] += 1

        # Busline b infos
        trip_times_b = pd.read_csv(os.path.join(ROOT_DIR, 'data', 'regular_bus', busline_b, 'trip_times.csv'))
        bus_stop_info_b = pd.read_csv(os.path.join(ROOT_DIR, 'data', 'regular_bus', busline_b, 'stop_order.csv'))
        drive_time_b = bus_stop_info_b['time_cum_diff'].iloc[-1]

        # Add busses in use for busline b
        for i, row in trip_times_b.iterrows():
            start = row['start_time'] - dwell_time_at_start_end
            end = row['start_time'] + drive_time_b + dwell_time_at_start_end
            busses_in_use[start:end] += 1

        fig, axs = plt.subplots(1, 2)

        axs[0].barh(
            y=trip_times_a['trip_number'],
            left=trip_times_a['start_time'],
            width=drive_time_a,
            color='tab:blue',
            label='Line 105a'
        )
        axs[0].barh(
            y=trip_times_b['trip_number'],
            left=trip_times_b['start_time'],
            width=drive_time_a,
            color='tab:orange',
            label='Line 105b'
        )
        axs[1].plot(
            pd.to_datetime(np.arange(100000), unit='s'),
            busses_in_use,
            )
        # axs[1].plot(
        #     pd.to_datetime(np.arange(100000), unit='s'),
        #     np.cumsum(busses_in_use * seconds_costs_euro),
        #     )
        axs[1].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        plt.show()
        print(np.cumsum(busses_in_use * seconds_costs_euro)[-1])

    
    @staticmethod
    def plot_busses_in_use(buslines):

        dwell_time_at_start_end = 6 * 60

        busses_in_use = np.zeros(100000)

        vehicle_stats_dict = pd.read_csv(os.path.join(VEHICLE_DIR, 'flex_bus.csv'), index_col=0).transpose()
        seconds_costs_euro = vehicle_stats_dict['hourly_costs_euro'].iloc[0] / 3600

        # Busline a infos
        for busline in buslines:
            trip_times_a = pd.read_csv(os.path.join(ROOT_DIR, 'data', 'regular_bus', busline, 'trip_times.csv'))
            bus_stop_info_a = pd.read_csv(os.path.join(ROOT_DIR, 'data', 'regular_bus', busline, 'stop_order.csv'))
            drive_time_a = bus_stop_info_a['time_cum_diff'].iloc[-1]

            # Add busses in use for busline a
            for i, row in trip_times_a.iterrows():
                start = row['start_time'] - dwell_time_at_start_end
                end = row['start_time'] + drive_time_a + dwell_time_at_start_end
                busses_in_use[start:end] += 1

        fig, axs = plt.subplots()
        axs.plot(
            pd.to_datetime(np.arange(100000), unit='s'),
            busses_in_use,
            )
        # axs[1].plot(
        #     pd.to_datetime(np.arange(100000), unit='s'),
        #     np.cumsum(busses_in_use * seconds_costs_euro),
        #     )
        axs.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        axs.set_ylabel('Number of buses in use')
        plt.show()
        print(np.cumsum(busses_in_use * seconds_costs_euro)[-1])


def rolling_demand_density(rq_times, start_hour, end_hour, time_step=60, window_size=3600):
    """ Calculates the number of passengers within window_size every time_step.
        Setting window_size = 3600 computes the demand density in passengers per hour """

    t_start = start_hour * 3600
    t_end = end_hour * 3600

    t = np.arange(t_start, t_end, time_step)
    density = np.zeros(len(t))

    for i, t_max in enumerate(t):

        t_min = max(t_start, t_max - window_size)

        density[i] = np.sum((rq_times >= t_min) & (rq_times < t_max))

    return t, density
        





if __name__ == '__main__':

    # for a in [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 3.0, 4.0, 5.0]:
    #     MultipleRegularBusLine.calculate_demand_density('line91_week', a, 25)

    # MultipleRegularBusLine.calculate_demand_density('line91_week', 1.0, 25, start_hour=8)
    # MultipleRegularBusLine.calculate_demand_density('greater_hellevoetsluis', 1.0, 25, start_hour=4)

    # MultipleRegularBusLine.demand_histogram('line91_week', 1.0, 25, start_hour=8)
    # MultipleRegularBusLine.demand_histogram('greater_hellevoetsluis', 1.0, 25, start_hour=4)

    # MultipleRegularBusLine.plot_single_demand_sample('line91_week', 1.0, 0)

    # MultipleRegularBusLine.plot_timetable_trips('line91a_week', 'line91b_week')
    # MultipleRegularBusLine.plot_timetable_trips('line105a_week_s', 'line105b_week_s')
    # MultipleRegularBusLine.plot_timetable_trips('line105a_week', 'line105b_week')
    # MultipleRegularBusLine.plot_timetable_trips('line106a_week', 'line106b_week')

    buslines = [
        'line91a_week', 'line91b_week',
        # 'line105a_week', 'line105b_week',
        'line105a_week_s', 'line105b_week_s',
        'line106a_week', 'line106b_week',
    ]
    MultipleRegularBusLine.plot_busses_in_use(buslines)

    # MultipleRegularBusLine.calculate_demand_density('line91_week', 1.0, 25, start_hour=8)
