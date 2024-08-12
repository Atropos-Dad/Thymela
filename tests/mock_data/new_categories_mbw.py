import pandas as pd
import json
import threading
from collections import defaultdict

# Load the CSV file
file_path = 'tests/mock_data/MBW_Studies.csv'
df = pd.read_csv(file_path, header=None, names=['id', 'studyId', 'json_data', 'studyTitle', 'species', 'institute', 'analysis', 'release_date', 'samples', 'metadataLink'])

#i did this through "big" categories in rows that are like json 
def analyze_row(row, results):
    try:
        data = json.loads(row['json_data'])
        
        sections_to_analyze = ['PROJECT', 'STUDY', 'SUBJECT_SAMPLE_FACTORS', 'SUBJECT', 'COLLECTION', 'TREATMENT', 'SAMPLEPREP', 'CHROMATOGRAPHY', 'ANALYSIS', 'MS']
        
        for section in sections_to_analyze:
            section_data = data.get(section, {})
            
            if isinstance(section_data, list):  # Handling lists like SUBJECT_SAMPLE_FACTORS
                for item in section_data:
                    for key, value in item.items():
                        if isinstance(value, dict):
                            for sub_key, sub_value in value.items():
                                if sub_value == "-":
                                    results['missing'][sub_key] += 1
                                elif sub_key not in df.columns:
                                    results['new_categories'][sub_key] += 1
                        elif value == "-":
                            results['missing'][key] += 1
                        elif key not in df.columns:
                            results['new_categories'][key] += 1
            else:  # Handling dictionaries like PROJECT, STUDY, SUBJECT, etc.
                for key, value in section_data.items():
                    if value == "-":
                        results['missing'][key] += 1
                    elif key not in df.columns:
                        results['new_categories'][key] += 1

    except json.JSONDecodeError:
        pass  

def parallel_analyze(df):
    results = {
        'missing': defaultdict(int),
        'new_categories': defaultdict(int)
    }
    threads = []
    for _, row in df.iterrows():
        thread = threading.Thread(target=analyze_row, args=(row, results))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    return results

results = parallel_analyze(df)

#i put 50 idk if thats valid
threshold = len(df) * 0.5


missing_df = pd.DataFrame(list(results['missing'].items()), columns=['Category', 'Missing Occurrences'])

# Apply threshold filter and sort by 'Missing Occurrences' in descending order
missing_df = missing_df[missing_df['Missing Occurrences'] > threshold].sort_values(by='Missing Occurrences', ascending=False).reset_index(drop=True)

print("Missing Data Statistics (Occurrences > 50% of total rows):")
print(missing_df)


new_categories_df = pd.DataFrame(list(results['new_categories'].items()), columns=['Potential New Category', 'Occurrences'])
new_categories_df = new_categories_df[new_categories_df['Occurrences'] > threshold].sort_values(by='Occurrences', ascending=False).reset_index(drop=True)
new_categories_df.to_csv('potential_new_categories.csv', index=False)

first_10 = new_categories_df.head(10)

print("\nPotential 10 New Categories Statistics (Occurrences > 50% of total rows):")
print(first_10)

print("\n other potential categories in the csv bc there is a lot of data mentioned >50%")

