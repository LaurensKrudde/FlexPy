if __name__ == "__main__":
    
    # On average, a bus driver in the Netherlands has a gross salary of 2770 euros per month. (40 hour work week)
    # https://www.werkzoeken.nl/salaris/buschauffeur/#:~:text=Hoeveel%20verdient%20een%20Buschauffeur%20gemiddeld%20in%20Nederland%3F&text=Een%20Buschauffeur%20in%20Nederland%20verdient,tot%20%E2%82%AC%203.190%20(hoog).
    monthly_gross_salary = 2770

    # On average, the total costs for an employer are 130% of the gross income of the employee.
    # https://www.sazas.nl/kennisbank/financieel/wat-kost-personeel-dit-zijn-de-personeelskosten-voor-u-als-werkgever#:~:text=Gemiddeld%20zijn%20de%20totale%20loonkosten,'n%20%E2%82%AC%205.200%2C%2D.
    monthly_costs = 1.3 * monthly_gross_salary

    # On average, a 40 hour workweek accounts for 173 hour worked in a month
    # https://www.personio.nl/hr-woordenboek/werkuren-per-maand/
    hourly_costs = monthly_costs / 173

    print(f"Average hourly bus driver costs: {hourly_costs} euro")
    print(f"Average 8-hour workday costs: {hourly_costs * 8} euro")

    # Average diesel use 9 person bus
    # https://voorraad.autodatawheelerdelta.nl/renault/trafic/passenger-16-dci-8-pers-l2h1-inclbpm-btw-vrij-navi-ac-cruise-pdc-mf-stuur/occ18091798-35de5
    diesel_liters_per_100km = 7.9

    flexbus20_km_per_liter = 6
    flexbus16_km_per_liter = 8
    flexbus12_km_per_liter = 10
    flexbus8_km_per_liter = 12.5
    car_km_per_liter = 15

    # Average benzine use car 1 op 15
    # https://www.unitedconsumers.com/blog/auto/zuinig-rijden.jsp#:~:text=Een%20gemiddelde%20benzineauto%20rijdt%20ongeveer,dieselauto%20ongeveer%201%20op%2021.
    benzine_liters_per_100km = 100 / 15

    # CO2-emission 174 gram / km (same ref as above)
    co2_emission_grams_per_km = 174

    # Gas price
    # https://www.nu.nl/brandstof?referrer=https%3A%2F%2Fwww.google.com%2F
    diesel_euro_per_liter = 1.88
    benzine_euro_per_liter = 2.17

    # https://www.nibud.nl/onderwerpen/uitgaven/autokosten/
    gas_costs_to_total_costs_ratio = 2.0

    print(f"Average gas costs per km (car 1): {benzine_euro_per_liter / car_km_per_liter}")
    print(f"Average gas costs per km (taxi): {benzine_euro_per_liter * benzine_liters_per_100km / 100}")
    print(f"Average gas costs per km (8 person bus): {diesel_euro_per_liter * diesel_liters_per_100km / 100}")
    print(f"Average gas costs per km (flexbus8): {diesel_euro_per_liter / flexbus8_km_per_liter}")
    print(f"Average gas costs per km (flexbus12): {diesel_euro_per_liter / flexbus12_km_per_liter}")
    print(f"Average gas costs per km (flexbus16): {diesel_euro_per_liter / flexbus16_km_per_liter}")
    print(f"Average gas costs per km (flexbus20): {diesel_euro_per_liter / flexbus20_km_per_liter}")

    print(f"Average costs [cents] per km (car 1): {benzine_euro_per_liter / car_km_per_liter * 100 * gas_costs_to_total_costs_ratio}")
    print(f"Average costs [cents] per km (taxi): {benzine_euro_per_liter * benzine_liters_per_100km / 100 * 100 * gas_costs_to_total_costs_ratio}")
    print(f"Average costs [cents] per km (8 person bus): {diesel_euro_per_liter * diesel_liters_per_100km / 100 * 100 * gas_costs_to_total_costs_ratio}")
    print(f"Average costs [cents] per km (flexbus8): {diesel_euro_per_liter / flexbus8_km_per_liter * 100 * gas_costs_to_total_costs_ratio}")
    print(f"Average costs [cents] per km (flexbus12): {diesel_euro_per_liter / flexbus12_km_per_liter * 100 * gas_costs_to_total_costs_ratio}")
    print(f"Average costs [cents] per km (flexbus16): {diesel_euro_per_liter / flexbus16_km_per_liter * 100 * gas_costs_to_total_costs_ratio}")
    print(f"Average costs [cents] per km (flexbus20): {diesel_euro_per_liter / flexbus20_km_per_liter * 100 * gas_costs_to_total_costs_ratio}")

    # Average dieselbus CO2-emission
    # https://www.anwb.nl/auto/brandstof/uitstoot
    diesel_co2_g_per_liter = 2606
    benzine_co2_g_per_liter = 2269
    print(f"Average CO2 emission per km (taxi): {benzine_co2_g_per_liter / car_km_per_liter}")
    print(f"Average CO2 emission per km (8 person bus): {diesel_co2_g_per_liter * diesel_liters_per_100km / 100}")
    print(f"Average CO2 emission per km (flexbus8): {diesel_co2_g_per_liter / flexbus8_km_per_liter}")
    print(f"Average CO2 emission per km (flexbus12): {diesel_co2_g_per_liter / flexbus12_km_per_liter}")
    print(f"Average CO2 emission per km (flexbus16): {diesel_co2_g_per_liter / flexbus16_km_per_liter}")
    print(f"Average CO2 emission per km (flexbus20): {diesel_co2_g_per_liter / flexbus20_km_per_liter}")

    

    ### Stadsbus

    # Average dieselbus CO2-emission
    # https://www.mobiliteit.nl/ov/bus/2022/12/09/hoe-vervuilend-zijn-dieselbussen-in-het-openbaar-vervoer/
    stad_bus_co2_emission_grams_per_km = 1100

    # Stadbus rijdt ongeveer 1 liter op 3.5 km
    # https://waterstofgate.nl/Praktijk/Businesscase-Bussen-verbruik/Businesscase-Bussen-CO2-uitstoot/#:~:text=Diesel%20stads%2D%20en%20lijnbussen%20rijden,elektriciteit%20verbruikt%20tijdens%20de%20productie.
    stadbus_gas_costs_per_km = diesel_euro_per_liter / 3.5

    print(f"Average gas costs per km (stadbus): {stadbus_gas_costs_per_km}")
    print(f"Average CO2 emission per km (stadbus): {stad_bus_co2_emission_grams_per_km}")