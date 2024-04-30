import json
import re
import os

data_type = {
    'IP': r"\bip[\s\-_]?address\b|\bip\b",
    'Android ID': r'Android[-_\s]?ID|Device[-_\s]?ID|ID\b|Identifier',
    'Phone': r'MCC|MNC|SIM|Region',
    'Location': r'Latitude|Longitude|Location|Country|City|Street|State|Long|\bLat\b'  
}

def flatten_dict(data, parent_key='', sep='_'):
    flattened_dict = {}
    for key, value in data.items():
        new_key = parent_key + sep + key if parent_key else key
        if isinstance(value, dict):
            flattened_dict.update(flatten_dict(value, new_key, sep=sep))
        elif isinstance(value, list):
            if len(value) == 0:
                flattened_dict[new_key] = value
            else:
                for i, item in enumerate(value):
                    new_key_with_index = new_key + sep + str(i)
                    if isinstance(item, dict):
                        flattened_dict.update(flatten_dict(item, new_key_with_index, sep=sep))
                    else:
                        flattened_dict[new_key_with_index] = item
        else:
            flattened_dict[new_key] = value
    return flattened_dict

def extract_data(json_data, data_type):
    result_dict = {}
    
    for key, pattern in data_type.items():
        result_dict[key] = []

        for json_key, row in json_data.items():
            if re.search(pattern, json_key, flags=re.IGNORECASE):
                result_dict[key].append({json_key: row})

    return result_dict

folder_path = 'SHEIN' # Path to the folder containing the JSON files
output_file = f'output_{folder_path}.json' # Store data in json in a uniform format as a dictionary
result_output = f'result_{folder_path}.json' # Extract data for specific data categories


merged_data = {}

for root, dirs, files in os.walk(folder_path):
    for file in files:
        if file.endswith('.json'):  
            file_path = os.path.join(root, file)

            with open(file_path, 'r', encoding='utf-8') as f:
                data_list = json.load(f)  

            if isinstance(data_list, list):
                for data in data_list:
                    flattened_data = flatten_dict(data)

                    for key, value in flattened_data.items():
                        if key in merged_data:
                            merged_data[key].append(value)
                        else:
                            merged_data[key] = [value]
            else:
                flattened_data = flatten_dict(data_list)
                for key, value in flattened_data.items():
                    if key in merged_data:
                        merged_data[key].append(value)
                    else:
                        merged_data[key] = [value]
        
            
for key, value in merged_data.items():
    unique_values = []
    for item in value:
        if item not in unique_values:
            unique_values.append(item)
    merged_data[key] = unique_values


with open(output_file, 'w') as f:
    json.dump(merged_data, f, indent=4)


result = extract_data(merged_data, data_type)

for key, value in result.items():
    print(f"Key: {key}")
    print(f"Value: {value}")
    print()

with open(result_output, 'w') as f:
    json.dump(result, f, indent=4)