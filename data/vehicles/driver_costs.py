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

    # Average benzine use car
    # https://www.unitedconsumers.com/blog/auto/zuinig-rijden.jsp#:~:text=Een%20gemiddelde%20benzineauto%20rijdt%20ongeveer,dieselauto%20ongeveer%201%20op%2021.
    benzine_liters_per_100km = 6.67

    # CO2-emission 174 gram / km (same ref as above)
    co2_emission_grams_per_km = 174

    # Gas price
    # https://www.nu.nl/brandstof?referrer=https%3A%2F%2Fwww.google.com%2F
    diesel_euro_per_liter = 1.86
    benzine_euro_per_liter = 2.19

    print(f"Average gas costs per km (taxi): {benzine_euro_per_liter * benzine_liters_per_100km / 100}")
    print(f"Average gas costs per km (8 person bus): {diesel_euro_per_liter * diesel_liters_per_100km / 100}")
