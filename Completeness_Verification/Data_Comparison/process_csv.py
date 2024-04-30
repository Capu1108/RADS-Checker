import os
import csv
import re
import json

data_type = {
    'IP': r"\bip[\s\-_]?address\b|\bip\b",
    'Android ID': r'Android[-_\s]?ID|Device[-_\s]?ID|ID\b|Identifier',
    'Phone': r'MCC|MNC|SIM|Region',
    'Location': r'Latitude|Longitude|Location|Country|City|Street|State|Long|\bLat\b'  
}

def read_csv_files(folder_path):
    data_dict = {}

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".csv"):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8-sig') as csv_file:
                    try:
                        reader = csv.reader(x.replace('\0', '') for x in csv_file)
                        data = [row for row in reader]
                    except Exception as e:
                        print(f"Error reading file {file_path}: {e}")

                    if len(data) > 0:
                        header = data[0]
                        if len(header) == 2:  
                            for row in data[1:]:
                                key, value = row[0], row[1]
                                if key in data_dict:
                                    data_dict[key].append(value)
                                else:
                                    data_dict[key] = value
                        else:  
                            for col in range(0, len(header)):
                                try:
                                    key = header[col]
                                    values = [row[col] for row in data[1:]]
                                    if key in data_dict:
                                        data_dict[key].extend(values)
                                    else:
                                        data_dict[key] = values
                                except Exception as e:
                                    print(f"Error {file_path}: {values}")

    return data_dict

def remove_duplicates(csv_data):
    result = {}

    for key, values in csv_data.items():
        if isinstance(values, list):
            result[key] = list(set(values))
        else:
            result[key] = values
    return result

def extract_data(csv_data, data_type):
    result_dict = {}
    
    for key, pattern in data_type.items():
        result_dict[key] = []

        for csv_key, row in csv_data.items():
            if re.search(pattern, csv_key, flags=re.IGNORECASE):
                result_dict[key].append({csv_key: row})

    return result_dict


folder_path = "Uber" # Path to the folder containing the CSV files
output_file = f'output_{folder_path}_csv.json' # Store data in csv in a uniform format as a dictionary
result_output = f'result_{folder_path}_csv.json' # Extract data for specific data categories

csv_data = read_csv_files(folder_path)
unique_csv_data = remove_duplicates(csv_data)
result = extract_data(unique_csv_data, data_type)

for key, value in result.items():
    print(f"Key: {key}")
    print(f"Value: {value}")
    print()

with open(output_file, 'w') as f:
    json.dump(unique_csv_data, f, indent=4)

with open(result_output, 'w') as f:
    json.dump(result, f, indent=4)

