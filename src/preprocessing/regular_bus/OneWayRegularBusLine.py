import pandas as pd
import os
import random
import numpy as np
import math
import time
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib
from scipy import stats
import datetime


SIZE_DEFAULT = 15
SIZE_LARGE = 16
plt.rc("font", family="Roboto")  # controls default font
plt.rc("font", weight="normal")  # controls default font
plt.rc("font", size=SIZE_DEFAULT)  # controls default text sizes
plt.rc("axes", titlesize=SIZE_LARGE)  # fontsize of the axes title
plt.rc("axes", labelsize=SIZE_LARGE)  # fontsize of the x and y labels
plt.rc("xtick", labelsize=SIZE_DEFAULT)  # fontsize of the tick labels
plt.rc("ytick", labelsize=SIZE_DEFAULT)  # fontsize of the tick labels


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
# DEMAND_DIR = os.path.join(ROOT_DIR, 'data', 'demand', 'hellevoetsluis', 'matched', 'hellevoetsluis_network_osm')
REGULAR_BUS_DATA_DIR = os.path.join(ROOT_DIR, 'data', 'regular_bus')
# REGULAR_BUS_DEMAND_EVAL_DIR = os.path.join(ROOT_DIR, 'data', 'demand', 'hellevoetsluis', 'regular_bus_eval')
# NETWORK_DIR = os.path.join(ROOT_DIR, "data", "networks")
VEHICLE_DIR = os.path.join(ROOT_DIR, 'data', 'vehicles')


# Random offset wrt timetable time for the request time
MAX_RANDOM_OFFSET_MINUTES = 30


def lighten_color(color, amount=0.5):
    """
    Lightens the given color by multiplying (1-luminosity) by the given amount.
    Input can be matplotlib color string, hex string, or RGB tuple.

    Examples:
    >> lighten_color('g', 0.3)
    >> lighten_color('#F034A3', 0.6)
    >> lighten_color((.3,.55,.1), 0.5)
    """
    import matplotlib.colors as mc
    import colorsys
    try:
        c = mc.cnames[color]
    except:
        c = color
    c = colorsys.rgb_to_hls(*mc.to_rgb(c))
    return colorsys.hls_to_rgb(c[0], 1 - amount * (1 - c[1]), c[2])


class OneWayRegularBusLine():

    def __init__(self, folder_name):
        self.name = folder_name
        self.trip_times_df = pd.read_csv(os.path.join(REGULAR_BUS_DATA_DIR, folder_name, 'trip_times.csv'))
        self.stop_order_df = pd.read_csv(os.path.join(REGULAR_BUS_DATA_DIR, folder_name, 'stop_order.csv'))
        self.counts_df = pd.read_csv(os.path.join(REGULAR_BUS_DATA_DIR, folder_name, 'counts.csv'), index_col=[0,1])
        self.n_trips = len(self.trip_times_df)
        self.n_stops = len(self.stop_order_df)


    def sample_OD_pairs(self, demand_scalar=1.0):
        """ Sample requests based on the OD probabilites derived from the boarding/alighting counts.
            First samples a bus trip, then samples an origin-destination from that trip """
        
        # random.seed(int(time.time()))

        instap_bus_counts_df = self.counts_df.xs('Instappers', axis=0, level=1)
        uitstap_bus_counts_df = self.counts_df.xs('Uitstappers', axis=0, level=1)

        OD_pairs = []

        trips_dict_OD_prob_dict = {}

        # Loop over the "ritten" (bus trips) to create the OD probabilities for each trip
        for trip_number, row in instap_bus_counts_df.iterrows():
            
            instap = row.values
            uitstap = uitstap_bus_counts_df.loc[trip_number, :].values
            OD_prob_dict = OD_probabilities(instap, uitstap)

            trips_dict_OD_prob_dict[trip_number] = OD_prob_dict

        # Number of instappers per bus trip
        instap_per_trip = instap_bus_counts_df.sum(axis=1)

        # Total instappers (probabilistic rounding based on decimal number)
        n_instap = sum(instap_per_trip) * demand_scalar
        sample_size = math.ceil(n_instap) if random.random() < n_instap - int(n_instap) else math.floor(n_instap)

        for _ in range(sample_size):

            # Sample a bus trip and get the OD probabilities for that bus trip
            sampled_trip_number = random.choices(instap_bus_counts_df.index, instap_per_trip, k=1)[0]
            OD_probs_sampled_trip = trips_dict_OD_prob_dict[sampled_trip_number]

            # FIXME (problem was that line 105 trip 1003 had no uitstappers)
            if len(OD_probs_sampled_trip) == 0:
                continue

            # Sample OD from this bus trip
            OD_sample_from_trip = random.choices(list(OD_probs_sampled_trip.keys()), list(OD_probs_sampled_trip.values()), k=1)[0]        

            OD_pairs.append([
                sampled_trip_number,
                OD_sample_from_trip[0],
                OD_sample_from_trip[1],
                # self.stop_order_df['name'].iloc[O_index], 
                # self.stop_order_df['name'].iloc[D_index],
            ])
            
        return pd.DataFrame(data=OD_pairs, columns=['trip_number', 'o_index', 'd_index'])


    def sample_OD_pairs_old(self, demand_scalar=1.0):
        """ Sample requests based on the OD probabilites derived from the boarding/alighting counts """

        random.seed(int(time.time()))

        instap_bus_counts_df = self.counts_df.xs('Instappers', axis=0, level=1)
        uitstap_bus_counts_df = self.counts_df.xs('Uitstappers', axis=0, level=1)

        OD_pairs = []

        # Loop over the "ritten"
        for index, row in instap_bus_counts_df.iterrows():
            
            instap = row.values
            uitstap = uitstap_bus_counts_df.loc[index, :].values
            # print(instap.sum(), uitstap.sum())
            OD_prob_dict = OD_probabilities(instap, uitstap)

            # Check if non empty:
            if not OD_prob_dict:
                continue

            # Probabilistic rounding based on decimal number
            n_instap = sum(instap) * demand_scalar
            n_passengers_in_trip = math.ceil(n_instap) if random.random() < n_instap - int(n_instap) else math.floor(n_instap)

            OD_samples_from_trip = random.choices(list(OD_prob_dict.keys()), list(OD_prob_dict.values()), k=n_passengers_in_trip)

            for OD_pair in OD_samples_from_trip:
                O_index = OD_pair[0]
                D_index = OD_pair[1]
                OD_pairs.append([
                    index,
                    O_index, 
                    D_index,
                    # self.stop_order_df['name'].iloc[O_index], 
                    # self.stop_order_df['name'].iloc[D_index],
                ])
            
        return pd.DataFrame(data=OD_pairs, columns=['trip_number', 'o_index', 'd_index'])
    

    def create_requests_from_OD_sample(self, OD_sample_df):
        """ Create demand file with additional information of the regular bus times/distance """
        
        rq_time = []

        for i, row in OD_sample_df.iterrows():
            
            trip_number = row['trip_number']
            trip_index = self.trip_times_df[self.trip_times_df['trip_number'] == trip_number].index[0]

            trip_start_time = self.trip_times_df['start_time'].iloc[trip_index] #+ self.stop_order_df['time_cum_diff'].iloc[row['o_index']]

            if trip_index == 0:
                right_offset = (self.trip_times_df['start_time'].iloc[trip_index + 1] - trip_start_time) / 2
                left_offset = right_offset
            elif trip_index == len(self.trip_times_df) - 1:
                left_offset = (trip_start_time - self.trip_times_df['start_time'].iloc[trip_index - 1]) / 2
                right_offset = left_offset
            else:
                left_offset = (trip_start_time - self.trip_times_df['start_time'].iloc[trip_index - 1]) / 2
                right_offset = (self.trip_times_df['start_time'].iloc[trip_index + 1] - trip_start_time) / 2
            
            left_offset, right_offset = min(left_offset, MAX_RANDOM_OFFSET_MINUTES * 60), min(right_offset, MAX_RANDOM_OFFSET_MINUTES * 60)

            og_start_time = trip_start_time + self.stop_order_df['time_cum_diff'].iloc[int(row['o_index'])]

            rq_time.append(og_start_time + random.randint(-left_offset, right_offset))        

        start_info = self.stop_order_df.iloc[OD_sample_df['o_index'], :].reset_index(drop=True)
        end_info = self.stop_order_df.iloc[OD_sample_df['d_index'], :].reset_index(drop=True)

        requests = pd.DataFrame({
            'trip_id': [str(id) for id in OD_sample_df['trip_number']],
            'rq_time': rq_time,
            'start': start_info['node_index'],
            'end': end_info['node_index'],
            'start_trip_index': OD_sample_df['o_index'],
            'end_trip_index': OD_sample_df['d_index'],
            'start_name_osm': start_info['name_osm'],
            'end_name_osm': end_info['name_osm'],
            'bus_end_tt': rq_time + end_info['time_cum_diff'] - start_info['time_cum_diff'],
            'bus_tt': end_info['time_cum_diff'] - start_info['time_cum_diff'],
            'line': self.name,
        })

        requests.index.name = 'request_id'

        return requests
    

    def get_costs_and_co2(self, km_driven):

        vehicle_stats_dict = pd.read_csv(os.path.join(VEHICLE_DIR, 'flex_bus.csv'), index_col=0).transpose()
        hourly_costs_euro = vehicle_stats_dict['hourly_costs_euro'].iloc[0]

        # Streekbus. Aanname verbruik 1 liter op 3.5 km
        stadbus_gas_costs_per_km = 0.53

        if self.name == 'line91a_week' or self.name == 'line91b_week':

            # Line 91 is driven with an 8 person bus (same as the flex bus)
            bus8_gas_cost_euro_per_km = vehicle_stats_dict['gas_cost_euro_per_km'].iloc[0]

            # Total for line 91a and 91b: 2 bussen from 8 to 18 and 1 bus from 18 to 2am. So the cost for one line is half.
            driver_costs = (2 * 10 * hourly_costs_euro + 8 * hourly_costs_euro) / 2
            gas_costs = bus8_gas_cost_euro_per_km * km_driven

            # co2
            co2_emissions = 208 / 1000 * km_driven

        elif self.name == 'line102a_week' or self.name == 'line102b_week':
            
            # Costs derived from MultiRegularBusLine.regular_bus_trip_plot
            driver_costs = 280 / 2      # costs a and b combined divided by 2
            
            # Line 102 is driven with a normal bus
            gas_costs = stadbus_gas_costs_per_km * km_driven

            # co2
            co2_emissions = 1100 / 1000 * km_driven

        elif self.name == 'line105a_week' or self.name == 'line105b_week' or self.name == 'line105a_week_s' or self.name == 'line105b_week_s':

            # Costs derived from MultiRegularBusLine.regular_bus_trip_plot
            driver_costs = 1200 / 2      # costs a and b combined divided by 2

            # Line 105 is driven with a normal bus
            gas_costs = stadbus_gas_costs_per_km * km_driven

            # co2
            co2_emissions = 1100 / 1000 * km_driven

        elif self.name == 'line106a_week' or self.name == 'line106b_week':

            # Costs derived from MultiRegularBusLine.regular_bus_trip_plot
            driver_costs = 700 / 2      # costs a and b combined divided by 2

            # Line 106 is driven with a normal bus
            gas_costs = stadbus_gas_costs_per_km * km_driven

            # co2
            co2_emissions = 1100 / 1000 * km_driven

        else:
            driver_costs = 0
            gas_costs = 0
            co2_emissions = 0

        return {
            'driver_costs': driver_costs,
            'gas_costs': gas_costs,
            'costs': driver_costs + gas_costs,
            'co2_emissions': co2_emissions
        }
    

    def evaluate_OD_sample(self, OD_sample_df):
        """ Evaluate the performance of the regular bus w.r.t. the OD sample """

        n_trips = len(self.trip_times_df)
        # n_trips = len(self.counts_df.groupby(level=0))

        total_m = len(self.trip_times_df) * self.stop_order_df['dist_cum_diff'].iloc[-1]
        total_time = len(self.trip_times_df) * self.stop_order_df['time_cum_diff'].iloc[-1]

        waiting_time = 0

        occupancy_m = 0
        occupancy_time = 0
        empty_m = 0
        empty_time = 0

        total_travel_time = 0

        total_rides = len(OD_sample_df)
        shared_rides = 0

        for k, trip_number in enumerate(self.trip_times_df['trip_number']):

            sub_sample = OD_sample_df[OD_sample_df['trip_number'] == trip_number]

            occupancy = np.zeros(self.n_stops)

            for i, row_i in sub_sample.iterrows():

                # Waiting time
                if k > 0:
                    waiting_time += min(30 * 60, (self.trip_times_df['start_time'].iloc[k] - self.trip_times_df['start_time'].iloc[k-1]) / 2)

                # Occupancy
                occupancy[int(row_i['o_index']):int(row_i['d_index'])] += 1

                # Travel time
                total_travel_time += self.stop_order_df['time_cum_diff'].iloc[int(row_i['d_index'])] - self.stop_order_df['time_cum_diff'].iloc[int(row_i['o_index'])]

                # Shared ride
                sharing = False
                for j, row_j in sub_sample.iterrows():
                    if i != j:
                        if max(row_i['o_index'], row_j['o_index']) < min(row_i['d_index'], row_j['d_index']):   # Checks for overlap
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
            'n_trips': n_trips,
            'waiting_time': waiting_time,
            'avg_waiting_time': waiting_time / total_rides,
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
            'driver_costs': self.get_costs_and_co2(total_m / 1000)['driver_costs'],
            'gas_costs': self.get_costs_and_co2(total_m / 1000)['gas_costs'],
            'costs': self.get_costs_and_co2(total_m / 1000)['costs'],
            'co2_emissions': self.get_costs_and_co2(total_m / 1000)['co2_emissions']
        }
    

    def create_requests_and_evaluate(self, demand_scalar=1.0):

        OD_sample_df = self.sample_OD_pairs(demand_scalar)

        return self.create_requests_from_OD_sample(OD_sample_df), self.evaluate_OD_sample(OD_sample_df)
    

    def plot_trip_counts(self, ax=None):
        """ Sum per trip """
        
        # Create bar plot
        n_passengers = self.counts_df.xs('Instappers', axis=0, level=1).sum(axis=1).reset_index().rename(columns={0: 'Boarding'})
        ax.bar(
            pd.to_datetime(self.trip_times_df['start_time'], unit='s'), 
            n_passengers['Boarding'], 
            width=0.01
        ) 

        # Axis and title
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        ax.set_xlabel("Trip start time")
        ax.set_ylabel("Average passengers per day")
        ax.set_title(f"Passengers per trip")


    def plot_stop_counts(self, ax=None):
        """ Sum per stop """
        
        # Create bar plot
        pd.merge(
            self.counts_df.xs('Instappers', axis=0, level=1).sum(axis=0).reset_index().rename(columns={0: 'Boarding'}),
            self.counts_df.xs('Uitstappers', axis=0, level=1).sum(axis=0).reset_index().rename(columns={0: 'Alighting'}),
            on='index'
        ).plot.bar(x='index', ax=ax)

        sum_instap = self.counts_df.xs('Instappers', axis=0, level=1).sum(axis=0).sum()
        sum_uitstap = self.counts_df.xs('Uitstappers', axis=0, level=1).sum(axis=0).sum()

        print(
            self.name,
            sum_instap,
            sum_uitstap
            )
        
        # Create x axis
        ax.set_xlabel("Bus stop")
        # xlabels = [str.split(', ')[1] for str in self.counts_df.columns]
        xlabels = self.counts_df.columns
        ax.set_xticklabels(labels=xlabels, rotation=90, ha='right')

        # Create y axis
        ax.set_ylabel("Average passengers per day")

        # Set title
        ax.set_title(f"Passengers per stop")

    
    def plot_trip_counts_sample(self, n_samples=1):

        fig, ax = plt.subplots(figsize=(10, 6))

        offset = 340
        width = 0.008

        # Create bar plot
        n_passengers = self.counts_df.xs('Instappers', axis=0, level=1).sum(axis=1).reset_index().rename(columns={0: 'Boarding'})
        ax.bar(
            pd.to_datetime(self.trip_times_df['start_time'] - offset, unit='s'), 
            n_passengers['Boarding'], 
            width=width,
            label='Data'
        ) 

        # Sample some samples
        samples = []
        for _ in range(n_samples):
            singe_sample_df = self.sample_OD_pairs()
            samples.append(singe_sample_df)
        OD_sample_df = pd.concat(samples)
        
        # Aggregate the sample on trip number
        agg_sample = OD_sample_df.groupby('trip_number')['trip_number'].count().reset_index(name='count')
        start_time = self.trip_times_df[self.trip_times_df['trip_number'].isin(agg_sample['trip_number'])]['start_time'].values
        
        # Plot sample
        ax.bar(
            pd.to_datetime(start_time + offset, unit='s'), 
            agg_sample['count'] / n_samples, 
            width=width,
            label='Sample',
            color=lighten_color('tab:blue', 0.5)
        ) 

        # Axis and title
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        ax.set_xlabel("Trip start time")
        ax.set_ylabel("Average passengers per day")
        ax.set_title("")
        ax.legend()

        plt.savefig(f'figures/samples/{self.name}_trip_counts_{n_samples}_samples.png')
        plt.close()
        # plt.show()

    
    def plot_stop_counts_sample(self, n_samples=1):

        fig, ax = plt.subplots(figsize=(10, 6))
        """ Sum per stop """
        
        # Boarding Alighting data
        data_df = pd.merge(
            self.counts_df.xs('Instappers', axis=0, level=1).sum(axis=0).reset_index().rename(columns={0: 'Boarding'}),
            self.counts_df.xs('Uitstappers', axis=0, level=1).sum(axis=0).reset_index().rename(columns={0: 'Alighting'}),
            on='index'
        )
        data_df.rename(columns={'index': 'stop_name', 'Boarding': 'Data Boarding', 'Alighting': 'Data Alighting'}, inplace=True)

        # Sample
        samples = []
        for _ in range(n_samples):
            singe_sample_df = self.sample_OD_pairs()
            samples.append(singe_sample_df)
        OD_sample_df = pd.concat(samples)

        # Aggregate the sample on stop
        bc_sample = pd.merge(
            OD_sample_df.groupby('o_index')['trip_number'].count().reset_index().rename(columns={'o_index': 'index', 'trip_number': 'Boarding'}),
            OD_sample_df.groupby('d_index')['trip_number'].count().reset_index().rename(columns={'d_index': 'index', 'trip_number': 'Alighting'}),
            on='index',
            how='outer'
        ).fillna(0)
        bc_sample.set_index('index', inplace=True)

        # Get daily average
        bc_sample['Boarding'] = bc_sample['Boarding'] / n_samples
        bc_sample['Alighting'] = bc_sample['Alighting'] / n_samples

        # Merge data and sample
        data_df = data_df.join(bc_sample, how='outer', lsuffix='_data', rsuffix='_sample')
        
        # Create bar plot
        data_df.plot.bar(
            x='stop_name',
            y=['Data Boarding', 'Boarding', 'Data Alighting', 'Alighting'],
            color=['tab:blue', lighten_color('tab:blue', 0.5), 'tab:orange', lighten_color('tab:orange')],
            ax=ax
        )
        
        # Create x axis
        ax.set_xlabel("Bus stop")
        xlabels = self.counts_df.columns
        ax.set_xticklabels(labels=xlabels, rotation=45, ha='right')
        ax.set_ylabel("Average passengers per day")
        
        ax.legend(['Boarding data', 'Boarding sample', 'Alighting data', 'Alighting sample'])
        
        ax.set_title("")
        fig.subplots_adjust(left=0.2, right=1, bottom=0.4)

        plt.savefig(f'figures/samples/{self.name}_stop_counts_{n_samples}_samples.png')
        plt.close()
        # plt.show()


    def plot_samples(self, demand_scalar=1.0):
        """ Generate samples and plot the results """

        OD_sample_df = self.sample_OD_pairs(demand_scalar)

        fig, axs = plt.subplots(1, 2)
        
        ### By trip
        # OD_sample_df.groupby('trip_number')['trip_number'].count().plot.bar(ax=axs[0])
        # axs[0].set_xticks(self.trip_times_df['trip_number'])
        # axs[0].set_xticklabels(labels=self.trip_times_df['trip_number'])
        
        # Aggregate the sample on trip number
        agg_sample = OD_sample_df.groupby('trip_number')['trip_number'].count().reset_index(name='count')  #.plot.bar(ax=axs[0])
        
        # Create x axis
        # start_time = self.trip_times_df[self.trip_times_df['trip_number'].isin(agg_sample['trip_number'])]['start_time'].values
        # time_label = [dt.strftime('%H:%M') for dt in pd.to_datetime(self.trip_times_df['start_time'], unit='s')]
        # axs[0].bar(start_time, agg_sample['count'] / demand_scalar, width=(start_time[len(start_time)-1] - start_time[0]) * 0.025)
        # axs[0].set_xticks(start_time)
        # axs[0].set_xticklabels(time_label, rotation=40, ha='center')
        # axs[0].set_xlabel("Trip start time")
        
        start_time = self.trip_times_df[self.trip_times_df['trip_number'].isin(agg_sample['trip_number'])]['start_time'].values
        axs[0].bar(
            pd.to_datetime(start_time, unit='s'), 
            agg_sample['count'] / demand_scalar, 
            width=0.01#(start_time[len(start_time)-1] - start_time[0]) * 0.025
        )
        
        # Create y axis
        axs[0].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        axs[0].set_ylabel("Average number of passengers per day")

        ### By stop
        bc_sample = pd.merge(
            OD_sample_df.groupby('o_index')['trip_number'].count().reset_index().rename(columns={'o_index': 'index', 'trip_number': 'Boarding'}),
            OD_sample_df.groupby('d_index')['trip_number'].count().reset_index().rename(columns={'d_index': 'index', 'trip_number': 'Alighting'}),
            on='index',
            how='outer'
        ).fillna(0)

        # Get daily average
        bc_sample['Boarding'] = bc_sample['Boarding'] / demand_scalar
        bc_sample['Alighting'] = bc_sample['Alighting'] / demand_scalar
        
        # Create plot
        bc_sample.plot.bar(x='index', ax=axs[1])

        # Create x axis
        axs[1].set_xticks(self.stop_order_df.index)
        xlabels = [str.split(', ')[1] for str in self.counts_df.columns]
        axs[1].set_xticklabels(labels=xlabels, rotation=30, ha='right')
        axs[1].set_xlabel("Bus stop")

        # Create y axis
        axs[1].set_ylabel("Average number of passengers per day")

        fig.suptitle(f'Average daily counts over {demand_scalar} samples')
        plt.show()

    
    def sample_error(self, n_samples, demand_scalar=1.0):

        counts_sample = pd.DataFrame().reindex_like(self.counts_df).fillna(0)

        for _ in range(n_samples):
            OD_sample_df = self.sample_OD_pairs(demand_scalar)
            for _, row in OD_sample_df.iterrows():
                counts_sample.loc[row['trip_number'], 'Instappers'][int(row['o_index'])] += 1
                counts_sample.loc[row['trip_number'], 'Uitstappers'][int(row['d_index'])] += 1

        rmse = math.sqrt(((self.counts_df - counts_sample / n_samples) ** 2).sum().sum())
        return rmse
    
    
    def percent_deviation_l1(self, n_samples, demand_scalar=1.0):
            
        counts_sample = pd.DataFrame().reindex_like(self.counts_df).fillna(0)

        for _ in range(n_samples):
            OD_sample_df = self.sample_OD_pairs(demand_scalar)
            for _, row in OD_sample_df.iterrows():
                counts_sample.loc[row['trip_number'], 'Instappers'][int(row['o_index'])] += 1
                counts_sample.loc[row['trip_number'], 'Uitstappers'][int(row['d_index'])] += 1

        l1 = (abs(self.counts_df - counts_sample / n_samples) / self.counts_df).mean().mean()
        return l1

    
    def plot_error(self, n_samples_list, n_resample, demand_scalar=1.0):

        rmse_lists = []

        for i in range(n_resample):

            single_rmse_list = []

            for n in n_samples_list:
                print(f"Resample {i+1}/{n_resample}: Sample {n}/{n_samples_list[-1]}")
                # rmse = self.sample_error(n, demand_scalar)
                rmse = self.sample_error(n, demand_scalar)
                single_rmse_list.append(rmse)
            
            rmse_lists.append(single_rmse_list)


        # Calculate the mean and standard error
        mean = np.mean(rmse_lists, axis=0)
        stderr = np.std(rmse_lists, axis=0) #/ np.sqrt(data.shape[0])

        # 95% confidence interval
        conf_interval = 1.96 * stderr

        # Plotting
        plt.figure(figsize=(10, 6))
        plt.plot(n_samples_list, mean, label='Mean', color='blue')
        # plt.fill_between(n_samples_list, mean - conf_interval, mean + conf_interval, color='blue', alpha=0.2, label='95% Confidence Interval')

        # Optional: Plot the individual lines for reference
        # for line in rmse_lists:
        #     plt.plot(n_samples_list, line, color='gray', alpha=0.3)

        # Plot a fill-between between the max and min of the individual lines
        plt.fill_between(n_samples_list, np.min(rmse_lists, axis=0), np.max(rmse_lists, axis=0), color='gray', alpha=0.2)

        plt.xlabel('Number of samples')
        plt.ylabel('RMSE')
        plt.title('RMSE with respect to the original data')
        plt.legend(['Mean', 'Individual RMSE'])
        plt.show()  


def OD_probabilities(instap, uitstap):
    """ Create probabilities of OD pair occurrence for a single trip (rit) """

    # Weird case caused by 0 total alighting counts
    if sum(uitstap) == 0.0:
        return {}

    od_prob_dict = dict()
    remaining_instappers = instap.copy()
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


def line91_count_plot():
    busline91a = OneWayRegularBusLine('line91a_week')
    busline91b = OneWayRegularBusLine('line91b_week')

    fig, axs = plt.subplots(2,2)
    busline91a.plot_trip_counts(ax=axs[0,0])
    busline91b.plot_trip_counts(ax=axs[0,1])
    busline91a.plot_stop_counts(ax=axs[1,0])
    busline91b.plot_stop_counts(ax=axs[1,1])
    fig.subplots_adjust(wspace=0.2, hspace=0.4, bottom=0.2, top=0.9)
    plt.savefig(os.path.join(ROOT_DIR, 'figures', 'bus_data', 'line91_counts.png'))
    plt.show()


def line102_count_plot():
    busline102a = OneWayRegularBusLine('line102a_week')
    busline102b = OneWayRegularBusLine('line102b_week')

    fig, axs = plt.subplots(2,2)
    busline102a.plot_trip_counts(ax=axs[0,0])
    busline102b.plot_trip_counts(ax=axs[0,1])
    busline102a.plot_stop_counts(ax=axs[1,0])
    busline102b.plot_stop_counts(ax=axs[1,1])
    fig.subplots_adjust(wspace=0.2, hspace=0.4)
    plt.show()


def line105_count_plot():
    busline105a = OneWayRegularBusLine('line105a_week')
    busline105b = OneWayRegularBusLine('line105b_week')

    fig, axs = plt.subplots(2,2)
    busline105a.plot_trip_counts(ax=axs[0,0])
    busline105b.plot_trip_counts(ax=axs[0,1])
    busline105a.plot_stop_counts(ax=axs[1,0])
    busline105b.plot_stop_counts(ax=axs[1,1])
    fig.subplots_adjust(wspace=0.2, hspace=0.4)
    plt.show()


def line105min_count_plot():
    busline105a = OneWayRegularBusLine('line105a_week-')
    busline105b = OneWayRegularBusLine('line105b_week-')

    fig, axs = plt.subplots(2,2)
    busline105a.plot_trip_counts(ax=axs[0,0])
    busline105b.plot_trip_counts(ax=axs[0,1])
    busline105a.plot_stop_counts(ax=axs[1,0])
    busline105b.plot_stop_counts(ax=axs[1,1])
    fig.subplots_adjust(wspace=0.2, hspace=0.4)
    plt.show()


def line106_count_plot():
    busline106a = OneWayRegularBusLine('line106a_week')
    busline106b = OneWayRegularBusLine('line106b_week')

    fig, axs = plt.subplots(2,2)
    busline106a.plot_trip_counts(ax=axs[0,0])
    busline106b.plot_trip_counts(ax=axs[0,1])
    busline106a.plot_stop_counts(ax=axs[1,0])
    busline106b.plot_stop_counts(ax=axs[1,1])
    fig.subplots_adjust(wspace=0.2, hspace=0.4)
    plt.show()


def save_plots():

    folders = ['line91a_week', 'line91b_week', 'line102a_week', 'line102b_week', 'line105a_week', 'line105b_week', 'line106a_week', 'line106b_week']
    # folders = ['line105a_week_s', 'line105b_week_s']

    line_numbers = {
        'line91a_week': 91,
        'line91b_week': 91,
        'line102a_week': 102,
        'line102b_week': 102,
        'line105a_week': 105,
        'line105b_week': 105,
        'line105a_week_s': 105,
        'line105b_week_s': 105,
        'line106a_week': 106,
        'line106b_week': 106,
    }

    for folder in folders:
            
            busline = OneWayRegularBusLine(folder)
            number = line_numbers[folder]
            start_stop = busline.stop_order_df['name'][0]
            end_stop = busline.stop_order_df['name'][busline.n_stops-1]

            # Plot by trip
            fig, axs = plt.subplots(figsize=(10, 6))
            busline.plot_trip_counts(ax=axs)
            axs.set_title(f"Line {number}: {start_stop} - {end_stop}")
            plt.tight_layout()
            plt.savefig(os.path.join(ROOT_DIR, 'figures', 'bus_data', f'{folder}_trip_counts.png'))
            plt.close()

            # Plot by stop
            fig, axs = plt.subplots(figsize=(10, 8))
            busline.plot_stop_counts(ax=axs)
            axs.set_title(f"Line {number}: {start_stop} - {end_stop}")
            fig.subplots_adjust(left=0.2, right=0.9, bottom=0.4)
            plt.tight_layout()
            plt.savefig(os.path.join(ROOT_DIR, 'figures', 'bus_data', f'{folder}_stop_counts.png'))
            plt.close()


def sample_plots():

    folders = ['line91a_week', 'line91b_week', 'line102a_week', 'line102b_week', 'line105a_week', 'line105b_week', 'line106a_week', 'line106b_week']

    for folder in folders:
            
            busline = OneWayRegularBusLine(folder)

            # Plot by trip
            busline.plot_trip_counts_sample(1)
            busline.plot_trip_counts_sample(25)

            # Plot by stop
            busline.plot_stop_counts_sample(1)
            busline.plot_stop_counts_sample(25)



if __name__ == "__main__":

    # busline = OneWayRegularBusLine('line91a_week')
    # busline.plot_error(
    #     # [1 + i*5 for i in range(21)],
    #     [1, 5, 10, 15, 20, 25, 30, 40, 50, 75, 100, 150, 250],
    #     n_resample=15,
    #     demand_scalar=1.0
    # )

    save_plots()
    # sample_plots()

