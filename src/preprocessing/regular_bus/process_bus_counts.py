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
        data = data.replace(to_replace='5 reizigers of minder', value=3)
        data = data.replace(to_replace='5 of minder reizigers', value=3)
    elif in_uit == "Uitstappers":
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

    # Make sure all stops are present, if not: create column with zeros
    for stop_name in stop_order:
        if stop_name not in data:
            data[stop_name] = 0

    # NaN can be replaced with 0
    data = data.fillna(0)

    # Select and set stops in correct order
    expected_data = data[stop_order]
    other = data[data.columns.difference(stop_order)]

    # Save to csv
    other.to_csv(os.path.join(REGULAR_BUS_DATA_DIR, folder_name, f"left_over_{in_uit}.csv"))

    return expected_data


def create_instap_uitstap_csv(original_excel_file_name, folder_name, week_sa_su):
    """ Concatenate the boarding and alighting data into a single csv file """

    instap = process_ebs_data(original_excel_file_name, 'Instappers', folder_name, week_sa_su)
    uitstap = process_ebs_data(original_excel_file_name, 'Uitstappers', folder_name, week_sa_su)

    instap['in_uit'] = "Instappers"
    uitstap['in_uit'] = 'Uitstappers'

    instap_uitstap = pd.concat([instap.reset_index(), uitstap.reset_index()])
    instap_uitstap = instap_uitstap.set_index(['Ritnummer', 'in_uit']).sort_index()

    instap_uitstap.to_csv(os.path.join(REGULAR_BUS_DATA_DIR, folder_name, 'counts.csv'))

    return instap_uitstap


if __name__ == "__main__":
  
    # create_instap_uitstap_csv("line91_2023.xlsx", 'line91a_week', 'week')
    # create_instap_uitstap_csv("line91_2023.xlsx", 'line91b_week', 'week')

    # create_instap_uitstap_csv("line102_2023.xlsx", 'line102a_week', 'week')
    # create_instap_uitstap_csv("line102_2023.xlsx", 'line102b_week', 'week')

    create_instap_uitstap_csv("line105_2023.xlsx", 'line105a_week', 'week')
    create_instap_uitstap_csv("line105_2023.xlsx", 'line105b_week', 'week')

    create_instap_uitstap_csv("line106_2023.xlsx", 'line106a_week', 'week')
    create_instap_uitstap_csv("line106_2023.xlsx", 'line106b_week', 'week')
