import pandas as pd
import os
import numpy as np


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
REGULAR_BUS_DATA_DIR = os.path.join(ROOT_DIR, 'data', 'regular_bus')
BOARDING_POINTS_DIR = os.path.join(ROOT_DIR, 'data', 'infra', 'hellevoetsluis_infra', 'hellevoetsluis_network_osm')


line91a_stops = [
    "Hellevoetsluis, Winkelcentrum",
    "Hellevoetsluis, Plataanlaan",
    "Hellevoetsluis, Vlasakkerlaan",
    "Hellevoetsluis, Vesting",
    "Hellevoetsluis, J.Blankenstraat",
    "Hellevoetsluis, Kanaalweg",
    "Hellevoetsluis, Sportlaan",
    "Hellevoetsluis, Amnesty Int.laan",
    "Hellevoetsluis, Hoonaartstraat",
    "Hellevoetsluis, Koninginnelaan",
    "Hellevoetsluis, J.van Brakelpad",
    "Hellevoetsluis, A.Schweitzerlaan",
    "Hellevoetsluis, M.L.Kinglaan",
    "Hellevoetsluis, Wkc.Bonsenhoek",
    "Hellevoetsluis, Bonseweg",
    "Hellevoetsluis, Uniceflaan",
    "Hellevoetsluis, Kickersbloem",
]

line91a_time_diff = np.array([0,1,1,1,1,1,2,1,1,1,2,1,1,1,2,1,4]) * 60

line91b_stops = [
    'Oudenhoorn, Oudenhoorn', 
    'Hellevoetsluis, Kickersbloem',
    'Hellevoetsluis, Uniceflaan', 
    'Hellevoetsluis, Bonseweg', 
    'Hellevoetsluis, Wkc.Bonsenhoek', 
    'Hellevoetsluis, M.L.Kinglaan', 
    'Hellevoetsluis, A.Schweitzerlaan',
    'Hellevoetsluis, J.van Brakelpad', 
    'Hellevoetsluis, Koninginnelaan',
    'Hellevoetsluis, Hoonaartstraat',
    'Hellevoetsluis, Amnesty Int.laan', 
    'Hellevoetsluis, Sportlaan', 
    'Hellevoetsluis, Struytse Hoeck',
    'Hellevoetsluis, De Sprong', 
    'Hellevoetsluis, Winkelcentrum', 
]

line91b_time_diff = np.array([0,5,2,1,1,1,1,2,2,2,1,1,1,1,2]) * 60


line102a_stops = [
    'Hellevoetsluis, Amnesty Int.laan',
    'Hellevoetsluis, Hoonaartstraat',
    'Hellevoetsluis, Koninginnelaan',
    'Hellevoetsluis, J.van Brakelpad',
    'Hellevoetsluis, A.Schweitzerlaan', 
    'Hellevoetsluis, M.L.Kinglaan',
    'Hellevoetsluis, Wkc.Bonsenhoek',
    'Hellevoetsluis, Bonseweg', 
    'Hellevoetsluis, Uniceflaan', 
    'Hellevoetsluis, Kickersbloem',
    'Heenvliet, Heenvliet',
    'Geervliet, Geervliet',
    'Spijkenisse, Laanweg',
    'Spijkenisse, Halfweg 2',
    'Spijkenisse, Zinkseweg',
    'Spijkenisse, De Ritte',
    'Spijkenisse, Metro Centrum',
]

line102a_time_diff = np.array([0,1,1,3,2,1,1,2,1,3,7,2,3,1,2,2,3]) * 60

line102b_stops = list(reversed(line102a_stops))

line102b_time_diff = np.array([0,2,1,1,1,3,2,8,2,1,2,1,1,2,2,2,1]) * 60

line105a_week_stops = [
    'Hellevoetsluis, Kickersbloem',
    'Hellevoetsluis, Mandenmaker',
    'Hellevoetsluis, Kooistee',
    'Hellevoetsluis, Ebstroom',
    'Hellevoetsluis, Plataanlaan',
    'Hellevoetsluis, Vlasakkerlaan',
    'Hellevoetsluis, Vesting',
    'Hellevoetsluis, J.Blankenstraat',
    'Hellevoetsluis, Kanaalweg',
    'Hellevoetsluis, Sportlaan',
    'Hellevoetsluis, Amnesty Int.laan',
    'Hellevoetsluis, Hoonaartstraat',
    'Hellevoetsluis, Koninginnelaan',
    'Nieuwenhoorn, Nieuwenhoorn',
    'Brielle, G.J. van den Boogerdweg',
    'Brielle, Busstation Rugge', # 2x
    'Brielle, Brielle Centrum',
    'Brielle, Nieuwland',
    'Vierpolders, Seggelant',
    'Rozenburg, Volgerweg',
    'Rozenburg, Raadhuisplein',
    'Botlek, Botlekstraat',
    'Botlek, Theemsweg',
    'Botlek, Chemieweg',
    'Botlek, Welplaatweg',
    'Botlek, Esso',
    'Spijkenisse, Halfweg 2',
    'Spijkenisse, Zinkseweg',
    'Spijkenisse, De Ritte',
    'Spijkenisse, Metro Centrum',
]

line105a_time_diff = np.array([0,2,2,1,1,1,1,2,1,2,1,1,2,4,8,4,2,1,2,13,5,7,1,1,2,2,4,1,2,3]) * 60

line105b_week_stops = [
    'Spijkenisse, Metro Centrum', 
    'Spijkenisse, De Ritte',
    'Spijkenisse, Zinkseweg',
    'Spijkenisse, Halfweg 2', 
    'Botlek, Esso', 
    'Botlek, Welplaatweg', 
    'Botlek, Chemieweg',
    'Botlek, Theemsweg',
    'Botlek, Botlekstraat',
    # 'Rozenburg, Eikenlaan', # occurs only a few times
    'Rozenburg, Raadhuisplein', 
    'Rozenburg, Volgerweg',
    'Vierpolders, Seggelant',
    'Brielle, Nieuwland',
    'Brielle, Brielle Centrum',
    'Brielle, Busstation Rugge', # 2x
    'Brielle, G.J. van den Boogerdweg', 
    'Nieuwenhoorn, Nieuwenhoorn', 
    'Hellevoetsluis, Koninginnelaan', 
    'Hellevoetsluis, Hoonaartstraat',
    # 'Hellevoetsluis, Smitsweg', # occurs once
    'Hellevoetsluis, Amnesty Int.laan', 
    'Hellevoetsluis, Sportlaan',
    'Hellevoetsluis, Kanaalweg', 
    'Hellevoetsluis, J.Blankenstraat',
    'Hellevoetsluis, Vesting', 
    'Hellevoetsluis, Vlasakkerlaan',
    'Hellevoetsluis, Plataanlaan',
    'Hellevoetsluis, Ebstroom',
    'Hellevoetsluis, Kooistee',
    'Hellevoetsluis, Mandenmaker',
    'Hellevoetsluis, Kickersbloem',
]

line105b_time_diff = np.array([0,2,1,1,4,2,2,2,1,6,5,10,2,2,7,1,7,4,2,1,1,1,1,2,1,1,1,2,2,3]) * 60

# Day time
line106a_week_stops = [
    'Hellevoetsluis, Kickersbloem',
    'Oudenhoorn, Oudenhoorn',
    'Zuidland, Harregat',
    'Zuidland, Julianastraat',
    'Zuidland, Stationsweg',
    'Zuidland, Zuidland Centrum',
    'Simonshaven, Simonshaven',
    'Hekelingen, Dorpsstraat',
    'Spijkenisse, Metro Heemraadlaan',
    'Spijkenisse, Hekelingseweg',
    'Spijkenisse, Metro Centrum',
]

line106a_time_diff = np.array([0,4,7,2,1,1,3,4,3,1,4]) * 60

# In the evening
line106a_week_evening_stops = [
    'Zuidland, Julianastraat',
    'Zuidland, Harregat',
    'Zuidland, Stationsweg',
    'Zuidland, Zuidland Centrum',
    'Simonshaven, Simonshaven',
    'Hekelingen, Dorpsstraat',
    'Spijkenisse, Metro Heemraadlaan',
    'Spijkenisse, Hekelingseweg',
    'Spijkenisse, Metro Centrum',
]

line106b_week_stops = [
    'Spijkenisse, Metro Centrum', 
    'Spijkenisse, Hekelingseweg', 
    'Spijkenisse, Metro Heemraadlaan', 
    'Hekelingen, Dorpsstraat', 
    'Simonshaven, Simonshaven', 
    'Zuidland, Zuidland Centrum', 
    'Zuidland, Stationsweg', 
    'Zuidland, Julianastraat', # Stops here in the evening
    'Zuidland, Harregat', 
    'Oudenhoorn, Oudenhoorn', 
    'Hellevoetsluis, Kickersbloem',
]

line106b_time_diff = np.array([0,2,2,3,3,2,1,1,2,6,6]) * 60


def create_stop_order_csv(stop_list, time_diff, folder_name, stop_info_osm_file_name=None):

    file_name = 'stop_order.csv'

    stop_order_df = pd.DataFrame({
        'name': stop_list,
        'time_diff': time_diff,
        'time_cum_diff': np.cumsum(time_diff)
    })

    if stop_info_osm_file_name:

        stop_info_osm_df = pd.read_csv(os.path.join(BOARDING_POINTS_DIR, stop_info_osm_file_name))

        assert len(stop_order_df) == len(stop_info_osm_df)

        stop_order_df = pd.concat([stop_order_df, stop_info_osm_df], axis=1)
    
    stop_order_df.to_csv(os.path.join(REGULAR_BUS_DATA_DIR, folder_name, file_name))


def create_stop_order_subset(folder, start_index=0, end_index=None):

    file_name = 'stop_order.csv'

    stop_order_df = pd.read_csv(os.path.join(REGULAR_BUS_DATA_DIR, folder, file_name), index_col=0)

    if end_index is None:
        end_index = len(stop_order_df)
        
    stop_order_df = stop_order_df.iloc[start_index:end_index]

    if start_index != 0:
        stop_order_df['time_cum_diff'] = stop_order_df['time_cum_diff'] - stop_order_df['time_cum_diff'].iloc[0]
        stop_order_df['time_diff'].iloc[0] = 0

        stop_order_df['dist_cum_diff'] = stop_order_df['dist_cum_diff'] - stop_order_df['dist_cum_diff'].iloc[0]
        stop_order_df['dist_diff'].iloc[0] = 0

    os.makedirs(os.path.join(REGULAR_BUS_DATA_DIR, f"{folder}-"), exist_ok=True)
    stop_order_df.to_csv(os.path.join(REGULAR_BUS_DATA_DIR, f"{folder}-", file_name))


if __name__ == "__main__":

    # create_stop_order_csv(line91a_stops, line91a_time_diff, 'line91a_week', 'line91a_stops.csv')
    # create_stop_order_csv(line91b_stops, line91b_time_diff, 'line91b_week', 'line91b_stops.csv')

    # create_stop_order_csv(line91a_stops, line91a_time_diff, 'line91a_saturday', 'line91a_stops.csv')
    # create_stop_order_csv(line91b_stops, line91b_time_diff, 'line91b_saturday', 'line91b_stops.csv')

    # create_stop_order_csv(line91a_stops, line91a_time_diff, 'line91a_sunday', 'line91a_stops.csv')
    # create_stop_order_csv(line91b_stops, line91b_time_diff, 'line91b_sunday', 'line91b_stops.csv')

    # create_stop_order_csv(line102a_stops, line102a_time_diff, 'line102a_week', 'line102a_stops.csv')
    # create_stop_order_csv(line102b_stops, line102b_time_diff, 'line102b_week', 'line102b_stops.csv')

    # create_stop_order_csv(line105a_week_stops, line105a_time_diff, 'line105a_week', 'line105a_stops.csv')
    # create_stop_order_csv(line105b_week_stops, line105b_time_diff, 'line105b_week', 'line105b_stops.csv')

    create_stop_order_subset('line105a_week', end_index=19)
    create_stop_order_subset('line105b_week', start_index=11)

    # create_stop_order_csv(line106a_week_stops, line106a_time_diff, 'line106a_week', 'line106a_stops.csv')
    # create_stop_order_csv(line106b_week_stops, line106b_time_diff, 'line106b_week', 'line106b_stops.csv')
