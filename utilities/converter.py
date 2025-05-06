import csv
import json
from datetime import datetime

# Define the category names in order
categories = [
    "Alimentos Y Bebidas No Alcohólicas",
    "Bebidas Alcohólicas Y Tabaco",
    "Prendas De Vestir Y Calzado",
    "Alojamiento, Agua, Electricidad, Gas Y Otros Combustibles",
    "Muebles, Artículos Para El Hogar Y Para La Conservación Ordinaria Del Hogar",
    "Salud",
    "Transporte",
    "Información Y Comunicación",
    "Recreación Y Cultura",
    "Educación",
    "Restaurantes Y Hoteles",
    "Bienes Y Servicios Diversos"
]


def parse_month_year(month_str):
    # Convert spanish month abbreviations to datetime
    month_map = {
        'ene': 'Jan', 'feb': 'Feb', 'mar': 'Mar', 'abr': 'Apr',
        'may': 'May', 'jun': 'Jun', 'jul': 'Jul', 'ago': 'Aug',
        'sept': 'Sep', 'oct': 'Oct', 'nov': 'Nov', 'dic': 'Dec'
    }
    month_abbr, year = month_str.split('-')
    month_english = month_map[month_abbr.lower()]
    date_str = f"01-{month_english}-20{year}"
    return datetime.strptime(date_str, '%d-%b-%Y').strftime('%Y-%m-%d')


def csv_to_json(csv_file_path):
    json_data = []

    with open(csv_file_path, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        current_date = None

        for row in csv_reader:
            if not row or not row[0]:
                continue

            # Check if it's a date row (e.g., "ene-19;")
            if '-' in row[0] and len(row[0].split('-')[0]) == 3:
                if current_date:
                    json_data.append({
                        "fecha": current_date,
                        "datos": current_data
                    })
                current_date = parse_month_year(row[0].replace(';', ''))
                current_data = []
                continue

            # It's a data row
            if len(row) >= 2 and current_date:
                try:
                    ponderado = float(row[0].replace(',', '.'))
                    mensual = float(row[1].replace(',', '.')) if row[1] else None

                    if len(current_data) < len(categories):
                        category = categories[len(current_data)]
                        current_data.append({
                            "categoria": category,
                            "ponderado": ponderado,
                            "mensual": mensual
                        })
                except ValueError:
                    continue

    # Add the last month's data
    if current_date and current_data:
        json_data.append({
            "fecha": current_date,
            "datos": current_data
        })

    return json_data


# Example usage
csv_file_path = '../data/completo.csv'
json_output = csv_to_json(csv_file_path)

# Save to JSON file
with open('../data/output.json', 'w', encoding='utf-8') as json_file:
    json.dump(json_output, json_file, ensure_ascii=False, indent=2)

print("JSON file has been created successfully!")