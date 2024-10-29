import os
import pandas as pd


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
REGULAR_BUS_COUNTS_DIR = os.path.join(ROOT_DIR, 'data', 'demand', 'regular_bus_counts')
REGULAR_BUS_DATA_DIR = os.path.join(ROOT_DIR, 'data', 'regular_bus')

HOLIDAYS_NOT_SUNDAY_2023 = 8 # https://www.wettelijke-feestdagen.nl/
WEEKDAYS_2023 = 52 * 5 - HOLIDAYS_NOT_SUNDAY_2023
SATURDAYS_2023 = 52
SUNDAYS_2023 = 52 + 1 + HOLIDAYS_NOT_SUNDAY_2023


def process_ebs_data(excel_file_name, in_uit, folder_name, week_sa_su):
    """ Extract data based on boarding/alighting, week/sa/su and direction from original data excel file """

    data = pd.read_excel(os.path.join(REGULAR_BUS_COUNTS_DIR, excel_file_name), sheet_name=in_uit)

    trip_numbers = pd.read_csv(os.path.join(REGULAR_BUS_DATA_DIR, folder_name, 'trip_times.csv'))['trip_number']
    stop_order = pd.read_csv(os.path.join(REGULAR_BUS_DATA_DIR, folder_name, 'stop_order.csv'))['name']

    # Filter ritten
    data = data[data['Ritnummer'].isin(trip_numbers)]

    # Replace '<= 5' TODO
    if in_uit == "Instappers":
        # print("5 or less", len(data[(data['Som van Aantal'] == '5 reizigers of minder') | (data['Som van Aantal'] == '5 of minder reizigers')]))
        data = data.replace(to_replace='5 reizigers of minder', value=3)
        data = data.replace(to_replace='5 of minder reizigers', value=3)
    elif in_uit == "Uitstappers":
        # print("5 or less", len(data[(data['Som van Aantal'] == '5 reizigers of minder') | (data['Som van Aantal'] == '5 of minder reizigers')]))
        data = data.replace(to_replace='5 reizigers of minder', value=3)
        data = data.replace(to_replace='5 of minder reizigers', value=3)

    # Calculate average daily instap
    if week_sa_su == 'week':
        data['Dag gemiddelde'] = data['Som van Aantal'] / WEEKDAYS_2023
    elif week_sa_su == 'saturday':
        data['Dag gemiddelde'] = data['Som van Aantal'] / SATURDAYS_2023
    elif week_sa_su == 'sunday':
        data['Dag gemiddelde'] = data['Som van Aantal'] / SUNDAYS_2023
    else:
        raise ValueError()

    # Pivot to table
    data = data.pivot(index='Ritnummer', columns='Station', values='Dag gemiddelde')
    # print(len(data) * len(data.columns))

    # Make sure all stops are present, if not: create column with zeros
    for stop_name in stop_order:
        if stop_name not in data:
            data[stop_name] = 0

    # Make sure all trip numbers are present, if not: create row with zeros
    for trip_number in trip_numbers:
        if trip_number not in data.index:
            data.loc[trip_number] = 0

    # Fix
    if folder_name == 'line105a_week' or folder_name == 'line105b_week':
        data['Spijkenisse, Metro Centrum'] = 0

    # NaN can be replaced with 0
    data = data.fillna(0)

    # Select and set stops in correct order
    expected_data = data[stop_order]
    other = data[data.columns.difference(stop_order)]

    # The first stop should have no alighting passengers
    if in_uit == 'Uitstappers':
        expected_data.iloc[:, 0] = 0
    # The last stop should have no boarding passengers
    elif in_uit == 'Instappers':
        expected_data.iloc[:, -1] = 0

    # Save to csv
    other.to_csv(os.path.join(REGULAR_BUS_DATA_DIR, folder_name, f"left_over_{in_uit}.csv"))

    return expected_data


def create_instap_uitstap_csv(original_excel_file_name, folder_name, week_sa_su):
    """ Concatenate the boarding and alighting data into a single csv file """

    instap = process_ebs_data(original_excel_file_name, 'Instappers', folder_name, week_sa_su)
    uitstap = process_ebs_data(original_excel_file_name, 'Uitstappers', folder_name, week_sa_su)

    # Scale instap and uitstap to match
    sum_instap = instap.sum().sum()
    sum_uitstap = uitstap.sum().sum()
    instap *= (sum_instap + sum_uitstap) / (2 * sum_instap)
    uitstap *= (sum_instap + sum_uitstap) / (2 * sum_uitstap)

    instap['in_uit'] = "Instappers"
    uitstap['in_uit'] = 'Uitstappers'

    instap_uitstap = pd.concat([instap.reset_index(), uitstap.reset_index()])
    instap_uitstap = instap_uitstap.set_index(['Ritnummer', 'in_uit']).sort_index()

    # Remove trips with no passengers
    empty_trips = []
    instap_uitstap_copy = instap_uitstap.copy()
    for trip_id, rows in instap_uitstap.groupby(level=0):
        if rows.sum().sum() == 0:
            empty_trips.append(trip_id)
            instap_uitstap_copy = instap_uitstap_copy.drop(index=trip_id, level=0)
    print(empty_trips)

    instap_uitstap_copy.to_csv(os.path.join(REGULAR_BUS_DATA_DIR, folder_name, 'counts.csv'))

    return instap_uitstap_copy


if __name__ == "__main__":
  
    # create_instap_uitstap_csv("line91_2023.xlsx", 'line91a_week', 'week')
    # create_instap_uitstap_csv("line91_2023.xlsx", 'line91b_week', 'week')

    # create_instap_uitstap_csv("line91_2023.xlsx", 'line91a_saturday', 'saturday')
    # create_instap_uitstap_csv("line91_2023.xlsx", 'line91b_saturday', 'saturday')

    # create_instap_uitstap_csv("line91_2023.xlsx", 'line91a_sunday', 'sunday')
    # create_instap_uitstap_csv("line91_2023.xlsx", 'line91b_sunday', 'sunday')

    # create_instap_uitstap_csv("line102_2023.xlsx", 'line102a_week', 'week')
    # create_instap_uitstap_csv("line102_2023.xlsx", 'line102b_week', 'week')

    # create_instap_uitstap_csv("line105_2023.xlsx", 'line105a_week', 'week')
    # create_instap_uitstap_csv("line105_2023.xlsx", 'line105b_week', 'week')

    # create_instap_uitstap_csv("line105_2023.xlsx", 'line105a_week_s', 'week')
    # create_instap_uitstap_csv("line105_2023.xlsx", 'line105b_week_s', 'week')

    create_instap_uitstap_csv("line106_2023.xlsx", 'line106a_week', 'week')
    create_instap_uitstap_csv("line106_2023.xlsx", 'line106b_week', 'week')
