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

    


