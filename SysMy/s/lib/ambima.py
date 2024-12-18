import csv

FILEPATH = 'anbima.csv'

def load_holidays(filepath):
    with open(filepath) as file:
        content = file.readlines()
        items = csv.DictReader(content)
        holidays = list(items)

    return holidays

from collections import defaultdict
from datetime import datetime

def generate_holidays_file(holidays):
    holidays_by_year = defaultdict(dict)
    for holiday in holidays:
        date = datetime.strptime(holiday['date'], '%d/%m/%y')
        holiday_name = holiday['name']
        if holiday_name in holidays_by_year[date.year]:
            holiday_name += ' 2'

        holidays_by_year[date.year][holiday_name] = f"date({date.year}, {date.month}, {date.day})"

    with open('anbima_holidays.py', 'w') as file:
        file.write("from datetime import date \n\n")
        file.write("HOLIDAYS = {\n")
        for year, holidays in holidays_by_year.items():
            file.write(f'    "{year}": {{\n')
            for name, date in holidays.items():
                file.write(f'        "{name}": {date},\n')
            file.write("    },\n")
        file.write("}\n")
holidays = load_holidays(FILEPATH)
generate_holidays_file(holidays)