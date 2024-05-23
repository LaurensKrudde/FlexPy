import pandas as pd
import os
import random
import numpy as np
import math
import json


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DEMAND_DIR = os.path.join(ROOT_DIR, 'data', 'demand', 'hellevoetsluis', 'matched', 'hellevoetsluis_network_osm')
REGULAR_BUS_DATA_DIR = os.path.join(ROOT_DIR, 'data', 'regular_bus')
REGULAR_BUS_DEMAND_EVAL_DIR = os.path.join(ROOT_DIR, 'data', 'demand', 'hellevoetsluis', 'regular_bus_eval')


def OD_probabilities(instap, uitstap):
    """ Create probabilities of OD pair occurrence for a single trip (rit) """

    od_prob_dict = dict()
    remaining_instappers = instap
    prob_Ds = uitstap / sum(uitstap)

    for j in range(1, len(uitstap)):
        if sum(remaining_instappers[:j]) > 0:
            prob_Os_given_D = remaining_instappers[:j] / sum(remaining_instappers[:j])
            remaining_instappers[:j] = remaining_instappers[:j] - prob_Os_given_D * uitstap[j]
            for i in range(0, j):
                prob_OD = prob_Os_given_D[i] * prob_Ds[j]
                # print(f"P(O={i} | D={j}) = {prob_OD}")
                od_prob_dict[(i, j)] = prob_OD

    return od_prob_dict


class RegularBusLine():

    def __init__(self, folder_name):
        self.trip_times_df = pd.read_csv(os.path.join(REGULAR_BUS_DATA_DIR, folder_name, 'trip_times.csv'))
        self.stop_order_df = pd.read_csv(os.path.join(REGULAR_BUS_DATA_DIR, folder_name, 'stop_order.csv'))
        self.counts_df = pd.read_csv(os.path.join(REGULAR_BUS_DATA_DIR, folder_name, 'counts.csv'), index_col=[0,1])
        self.n_trips = len(self.trip_times_df)
        self.n_stops = len(self.stop_order_df)


    def sample_OD_pairs(self, demand_scalar=1.0):
        """ Sample requests based on the OD probabilites derived from the boarding/alighting counts """

        instap_bus_counts_df = self.counts_df.xs('Instappers', axis=0, level=1)
        uitstap_bus_counts_df = self.counts_df.xs('Uitstappers', axis=0, level=1)

        OD_pairs = []

        # Loop over the "ritten"
        for index, row in instap_bus_counts_df.iterrows():
            
            instap = row.values
            uitstap = uitstap_bus_counts_df.loc[index, :].values

            # Probabilistic rounding based on decimal number
            n_instap = sum(instap) * demand_scalar
            n_passengers_in_trip = math.ceil(n_instap) if random.random() < n_instap - int(n_instap) else math.floor(n_instap)

            OD_prob_dict = OD_probabilities(instap, uitstap)

            OD_samples_from_trip = random.choices(list(OD_prob_dict.keys()), list(OD_prob_dict.values()), k=n_passengers_in_trip)

            for OD_pair in OD_samples_from_trip:
                O_index = OD_pair[0]
                D_index = OD_pair[1]
                OD_pairs.append([
                    index, O_index, 
                    D_index, 
                    # self.stop_order_df['name'].iloc[O_index], 
                    # self.stop_order_df['name'].iloc[D_index],
                ])
            
        return pd.DataFrame(data=OD_pairs, columns=['trip_number', 'o_index', 'd_index'])
    

    def create_requests_from_OD_sample(self, OD_sample_df):
        """ Create demand file with additional information of the regular bus times/distance """

        og_start_times = [self.trip_times_df.loc[self.trip_times_df['trip_number'] == trip_number, 'start_time'].values[0] for trip_number in OD_sample_df['trip_number']]
        rq_time = [time + random.randint(0, 15 * 60) for time in og_start_times]

        start_info = self.stop_order_df.iloc[OD_sample_df['o_index'], :].reset_index(drop=True)
        end_info = self.stop_order_df.iloc[OD_sample_df['d_index'], :].reset_index(drop=True)

        requests = pd.DataFrame({
            'rq_time': rq_time,
            'start': start_info['node_index'],
            'end': end_info['node_index'],
        })

        requests.index.name = 'request_id'

        return requests
    

    def evaluate_OD_sample(self, OD_sample_df):
        """ Evaluate the performance of the regular bus w.r.t. the OD sample """

        total_m = len(self.trip_times_df) * self.stop_order_df['dist_cum_diff'].iloc[-1]
        total_time = len(self.trip_times_df) * self.stop_order_df['time_cum_diff'].iloc[-1]

        occupancy_m = 0
        occupancy_time = 0
        empty_m = 0
        empty_time = 0

        total_travel_time = 0

        total_rides = len(OD_sample_df)
        shared_rides = 0

        for trip_number in self.trip_times_df['trip_number']:

            sub_sample = OD_sample_df[OD_sample_df['trip_number'] == trip_number]

            occupancy = np.zeros(self.n_stops)

            for _, row_i in sub_sample.iterrows():

                # Occupancy
                occupancy[int(row_i['o_index']):int(row_i['d_index'])] += 1

                # Travel time
                total_travel_time += self.stop_order_df['time_cum_diff'].iloc[int(row_i['d_index'])] - self.stop_order_df['time_cum_diff'].iloc[int(row_i['o_index'])]

                # Shared ride
                sharing = False
                for _, row_j in sub_sample.iterrows():
                    if max(row_i['o_index'], row_j['o_index']) < min(row_i['d_index'], row_j['d_index']):   # Check for overlap
                        sharing = True
                if sharing:
                    shared_rides += 1

            # Occupancy / empty
            for k, count in enumerate(occupancy[:-1]):

                if count == 0:
                    empty_m += self.stop_order_df['dist_diff'].iloc[k+1]
                    empty_time += self.stop_order_df['time_diff'].iloc[k+1]

                else:
                    occupancy_m += count * self.stop_order_df['dist_diff'].iloc[k+1]
                    occupancy_time += count * self.stop_order_df['time_diff'].iloc[k+1]

        return {
            'total_vkm': total_m / 1000,
            'total_time': total_time,
            'total_travel_time': total_travel_time,
            'avg_travel_time': total_travel_time / total_rides,
            'occupancy_vkm': occupancy_m / 1000,
            'occupancy_time': occupancy_time,
            'occupancy_vkm_frac': occupancy_m / total_m,
            'occupancy_time_frac': occupancy_time / total_time,
            'empty_vkm': empty_m / 1000,
            'empty_time': empty_time,
            'empty_vkm_frac': empty_m / total_m,
            'empty_time_frac': empty_time / total_time,
            'total_passengers': total_rides,
            'shared_rides': shared_rides,
            'shared_rides_frac': shared_rides / total_rides,
        }
    

    def create_requests_and_evaluate(self, demand_scalar=1.0):

        OD_sample_df = self.sample_OD_pairs(demand_scalar)

        return self.create_requests_from_OD_sample(OD_sample_df), self.evaluate_OD_sample(OD_sample_df)


class MultipleRegularBusLine():

    def __init__(self, folder_name_list):
        self.RegularBusLine_list = [RegularBusLine(folder_name) for folder_name in folder_name_list]

    def create_requests_and_evaluate(self, scenario_name, demand_scalar=1.0):

        request_df_list = []
        eval_dict_list = []

        for bus_line in self.RegularBusLine_list:

            requests, eval = bus_line.create_requests_and_evaluate(demand_scalar)

            request_df_list.append(requests)
            eval_dict_list.append(eval)
            
        requests = pd.concat(request_df_list, axis=0).sort_values('rq_time').reset_index(drop=True)
        requests.index.name = 'request_id'
        requests.to_csv(os.path.join(DEMAND_DIR, f'{scenario_name}.csv'))

        evaluation = self.concat_eval(eval_dict_list)
        with open(os.path.join(REGULAR_BUS_DEMAND_EVAL_DIR, f'{scenario_name}.json'), 'w') as f:
            json.dump(evaluation, f)

        return requests, evaluation

    def concat_eval(self, eval_dict_list):

        total_vkm = float(np.sum([eval['total_vkm'] for eval in eval_dict_list]))
        total_time = float(np.sum([eval['total_time'] for eval in eval_dict_list]))
        total_travel_time = float(np.sum([eval['total_travel_time'] for eval in eval_dict_list]))
        occupancy_vkm = float(np.sum([eval['occupancy_vkm'] for eval in eval_dict_list]))
        occupancy_time = float(np.sum([eval['occupancy_time'] for eval in eval_dict_list]))
        empty_vkm = float(np.sum([eval['empty_vkm'] for eval in eval_dict_list]))
        empty_time = float(np.sum([eval['empty_time'] for eval in eval_dict_list]))
        total_passengers = float(np.sum([eval['total_passengers'] for eval in eval_dict_list]))
        shared_rides = float(np.sum([eval['shared_rides'] for eval in eval_dict_list]))

        return {
            'total_vkm': total_vkm,
            'total_time': total_time,
            'total_travel_time': total_travel_time,
            'avg_travel_time': total_travel_time / total_passengers,
            'occupancy_vkm': occupancy_vkm,
            'occupancy_time': occupancy_time,
            'occupancy_vkm_frac': occupancy_vkm / total_vkm,
            'occupancy_time_frac': occupancy_time / total_time,
            'empty_vkm': empty_vkm,
            'empty_time': empty_time,
            'empty_vkm_frac': empty_vkm / total_vkm,
            'empty_time_frac': empty_time / total_time,
            'total_passengers': total_passengers,
            'shared_rides': shared_rides,
            'shared_rides_frac': shared_rides / total_passengers,
        }


if __name__ == "__main__":

    # BusLine91aweek = RegularBusLine('line91a_week')
    # line91a_sample = BusLine91aweek.sample_OD_pairs()
    # print(BusLine91aweek.evaluate_OD_sample(line91a_sample))

    # multibusline = MultipleRegularBusLine(['line91a_week', 'line91b_week'])
    # requests, eval = multibusline.create_requests_and_evaluate('line91_week', 1.0)

    # multibusline = MultipleRegularBusLine(['line91a_week', 'line91b_week'])
    # requests, eval = multibusline.create_requests_and_evaluate('line91_week_x2', 2.0)

    multibusline = MultipleRegularBusLine(['line102a_week', 'line102b_week'])
    requests, eval = multibusline.create_requests_and_evaluate('line102_week')
