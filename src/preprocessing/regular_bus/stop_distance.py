import pandas as pd
import os
import numpy as np


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
REGULAR_BUS_DATA_DIR = os.path.join(ROOT_DIR, 'data', 'regular_bus')


if __name__=="__main__":

    small = ['line91a_week', 'line91b_week']
    large = ['line91a_week', 'line91b_week', 'line105a_week', 'line105b_week', 'line106a_week', 'line106b_week']

    small_n_stops = 0
    small_avg = 0
    for line in small:
        stop_order = pd.read_csv(os.path.join(REGULAR_BUS_DATA_DIR, line, "stop_order.csv"))
        small_avg += stop_order['dist_diff'].mean()
        small_n_stops += len(stop_order)
    small_avg = small_avg / len(small)

    large_n_stops = 0
    large_avg = 0
    for line in large:
        stop_order = pd.read_csv(os.path.join(REGULAR_BUS_DATA_DIR, line, "stop_order.csv"))
        large_avg += stop_order['dist_diff'].mean()
        large_n_stops += len(stop_order)
    large_avg = large_avg / len(large)

    print(f"Small: {small_avg}")
    print(f"Large: {large_avg}")

    print(f"Small: {small_n_stops/2}")
    print(f"Large: {large_n_stops/2}")

    
