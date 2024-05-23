import numpy as np
import pandas as pd
import os
import time

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
REGULAR_BUS_DATA_DIR = os.path.join(ROOT_DIR, 'data', 'regular_bus')

HALF_HOUR = 30 * 60
HOUR = 3600
MIN = 60

def get_line91a_week_times():

    ritnummer = [1001 + 2 * i for i in range(24)]

    start_hour = 9
    start_min = 6
    start_time = start_hour * 3600 + start_min * 60

    L91a_day_times = [
        start_time + i * HALF_HOUR for i in range(18)
    ]
    L91a_evening_times = [
        L91a_day_times[-1] + i * HOUR for i in range(1, 7)
    ]
    L91a_times = L91a_day_times + L91a_evening_times
    
    return dict(zip(ritnummer, L91a_times))


def get_line91b_week_times():

    ritnummer = [1002 + 2 * i for i in range(24)]

    start_hour = 8
    start_min = 48
    start_time = start_hour * 3600 + start_min * 60

    L91b_day_times = [
        start_time + i * HALF_HOUR for i in range(18)
    ]
    L91b_evening_times = [
        L91b_day_times[-1] + i * HOUR for i in range(1, 7)
    ]
    L91b_times = L91b_day_times + L91b_evening_times
    
    return dict(zip(ritnummer, L91b_times))


def get_line102a_week_times():

    trip_numbers = [1001 + 2 * i for i in range(7)]

    start_hour = 6
    start_min = 1
    start_time = start_hour * 3600 + start_min * 60

    day_times = [
        start_time + i * HALF_HOUR for i in range(6)
    ]
    start_times = day_times + [9 * 3600 + 41 * 60]
    
    return dict(zip(trip_numbers, start_times))


def get_line102b_week_times():
    
    trip_numbers = [1002 + 2 * i for i in range(10)]

    start_time = 6 * 3600 + 27 * 60
    day_times = [
        start_time + i * HALF_HOUR for i in range(4)
    ]

    afternoon_start = 15 * 3600 + 43 * 60
    afternoon_times = [
        afternoon_start + i * HALF_HOUR for i in range(6)
    ]

    start_times = day_times + afternoon_times
    
    return dict(zip(trip_numbers, start_times))


def get_line105a_week_times():
    
    trip_numbers = [1001 + 2 * i for i in range(28)]

    start_times = [
        5 * HOUR + 45 * MIN + i * HALF_HOUR for i in range(7)
    ] \
    + [
        9 * HOUR + 49 * MIN + i * HOUR for i in range(3)
    ] \
    + [
        12 * HOUR + 18 * MIN + i * HALF_HOUR for i in range(12)
    ] \
    + [
        17 * HOUR + 54 * MIN + i * HALF_HOUR for i in range(3)
    ] \
    + [
        19 * HOUR + 30 * MIN + i * HOUR for i in range(3)
    ]

    return dict(zip(trip_numbers, start_times))


def get_line105b_week_times():
    
    trip_numbers = [1002 + 2 * i for i in range(34)]

    start_times = [5 * HOUR + 8 * MIN] \
    + [6 * HOUR + 8 * MIN + i * HALF_HOUR for i in range(5)] \
    + [8 * HOUR + 4 * MIN] \
    + [8 * HOUR + 36 * MIN] \
    + [9 * HOUR + 10 * MIN + i * HOUR for i in range(4)] \
    + [12 * HOUR + 38 * MIN + i * HALF_HOUR for i in range(7)] \
    + [15 * HOUR + 53 * MIN] \
    + [16 * HOUR + 8 * MIN + i * HALF_HOUR for i in range(2)] \
    + [16 * HOUR + 53 * MIN] + [17 * HOUR + 8 * MIN] + [17 * HOUR + 38 * MIN] \
    + [18 * HOUR + 8 * MIN] + [18 * HOUR + 24 * MIN] \
    + [17 * HOUR + 53 * MIN] + [18 * HOUR + 53 * MIN + i * HOUR for i in range(5)] \
    + [24 * HOUR + 24 * MIN]

    return dict(zip(trip_numbers, start_times))


def get_line106a_week_times():
    
    trip_numbers = [1001 + 2 * i for i in range(36)]

    start_times = [5 * HOUR + 55 * MIN + i * HALF_HOUR for i in range(35)] \
    + [24 * HOUR + 0 * MIN]

    return dict(zip(trip_numbers, start_times))


def get_line106b_week_times():
    
    trip_numbers = [1002 + 2 * i for i in range(36)]

    start_times = [6 * HOUR + 14 * MIN + i * HALF_HOUR for i in range(34)] \
    + [23 * HOUR + 46 * MIN] \
    + [24 * HOUR + 16 * MIN]

    return dict(zip(trip_numbers, start_times))


def create_time_csv(trip_time_dict, folder_name):

    file_name = 'trip_times.csv'

    pd.DataFrame({
        'trip_number': trip_time_dict.keys(), 
        'start_time': trip_time_dict.values(),
        'time': [time.strftime('%H:%M:%S', time.gmtime(start_time)) for start_time in trip_time_dict.values()]
    }).to_csv(os.path.join(REGULAR_BUS_DATA_DIR, folder_name, file_name))


if __name__ == "__main__":

    # create_time_csv(get_line91a_week_times(), 'line91a_week')
    # create_time_csv(get_line91b_week_times(), 'line91b_week')

    # create_time_csv(get_line102a_week_times(), 'line102a_week')
    # create_time_csv(get_line102b_week_times(), 'line102b_week')

    # create_time_csv(get_line105a_week_times(), 'line105a_week')
    # create_time_csv(get_line105b_week_times(), 'line105b_week')

    create_time_csv(get_line106a_week_times(), 'line106a_week')
    create_time_csv(get_line106b_week_times(), 'line106b_week')