import json

def merge_json_files(file1_path, file2_path, output_path="output.json"):
    try:
        # Load first JSON file
        with open(file1_path, "r", encoding="utf-8") as file1:
            data1 = json.load(file1)
        
        # Load second JSON file
        with open(file2_path, "r", encoding="utf-8") as file2:
            data2 = json.load(file2)
        
        # Merge the two JSON structures
        merged_data = {}
        
        # Iterate through keys in both files
        for key in sorted(set(data1.keys()).union(data2.keys())):
            if key in data1 and key in data2:
                if isinstance(data1[key], dict) and isinstance(data2[key], dict):
                    merged_data[key] = {**data1[key], **data2[key]}  # Merge dictionaries
                else:
                    merged_data[key] = [data1[key], data2[key]]  # Store non-dict values as list
            elif key in data1:
                merged_data[key] = data1[key]
            else:
                merged_data[key] = data2[key]
        
        # Save the merged data to output.json with sorted keys
        with open(output_path, "w", encoding="utf-8") as output_file:
            json.dump(merged_data, output_file, indent=4, sort_keys=True)
        
        print(f"Merged JSON saved to {output_path}")
    except Exception as e:
        print(f"Error: {e}")

merge_json_files("../SWE-bench/setup_result/setup_map.json", "../SWE-bench/setup_result/tasks_map.json", "../SWE-bench/setup_result/full_map.json")
