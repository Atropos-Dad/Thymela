import csv
from bs4 import BeautifulSoup
import requests
# Metabolomics Workbench (Mwb) web scraping functions


def inital(html_file_path): 
    """A simple way to parse the HTML content of the Metabolomics Workbench (Mwb) website
    This needs to be developed to actually scrape the website initally (and this is possible for sure)
    But atm, primary focus is on the data and not the scraping itself
    """
    # Read the HTML file
    with open(html_file_path, 'r') as file:
        html_content = file.read()

    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the table with class 'datatable'
    tables = soup.find_all('table')
    if len(tables) < 2:
        raise ValueError('Could not find the second table with class "datatable"')

    table = tables[2]



    header = [
        'Study ID',
        'Study Title',
        'Species',
        'Institute',
        'Analysis',
        'Released',
        'Version',
        'Samples',
        'Download'
    ]


    # Extract rows from the table
    rows = []
    rows.append(header)

    for row in table.find_all('tr')[1:]:  # Skip the header row
        row_values = [cell.text.strip() for cell in row.find_all('td')]
        rows.append(row_values)
        # change the last column to be a link
        last_cell = row.find_all('td')[-1]
        link = last_cell.find('a')
        if link:
            row_values[-1] = link.get('href')
        else:
            row_values[-1] = ''



    # Write the data to a CSV file
    with open(f'{html_file_path}_ids.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(rows)

import requests
from bs4 import BeautifulSoup
import json
import concurrent.futures
import threading
import os
import logging
from tqdm import tqdm

class MwbScraper:
    def __init__(self, output_folder='src/webscraping/mwb_results/'):
        self.base_url = "https://www.metabolomicsworkbench.org/data/"
        self.lock = threading.Lock()
        self.output_folder = output_folder
        self.pbar = None
        
        if not os.path.exists(self.output_folder):
            with self.lock:
                if not os.path.exists(self.output_folder):
                    os.makedirs(self.output_folder)
        
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.log_lock = threading.Lock()

    def safe_log(self, level, message):
        with self.log_lock:
            if level == logging.INFO:
                logging.info(message)
            elif level == logging.ERROR:
                logging.error(message)
            if self.pbar:
                self.pbar.write(message)

    def metadata_gather(self, study_id):
        """
        Gather metadata from the Metabolomics Workbench (Mwb) website using a study_ID.
        """
        
        link = f"{self.base_url}study_textformat_list.php?JSON=YES&STUDY_ID={study_id}"
        try:
            response = requests.get(link)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            download_link = soup.find('a', string='Download')
            
            if download_link is None:
                raise ValueError('Could not find the link to download the metadata')
            
            download_link = download_link.get('href')
            download_link = f'{self.base_url}{download_link}'
            response = requests.get(download_link)
            response.raise_for_status()
            metadata = response.json()  # Assuming the response is in JSON format
            
            self.save_results(metadata, study_id)
            self.safe_log(logging.INFO, f'Metadata for study ID {study_id} has been successfully gathered and saved.')
            
            return True
        except requests.RequestException as e:
            self.safe_log(logging.ERROR, f'HTTP error occurred for study ID {study_id}: {e}')
        except ValueError as e:
            self.safe_log(logging.ERROR, f'Error for study ID {study_id}: {e}')
        except Exception as e:
            self.safe_log(logging.ERROR, f'An unexpected error occurred for study ID {study_id}: {e}')
        
        return False

    def save_results(self, data, study_id):
        filename = os.path.join(self.output_folder, f'study_{study_id}_metadata.json')
        with self.lock:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)

    def gather_metadata_concurrently(self, study_ids):
        """
        Gather metadata for multiple study IDs concurrently.
        """
        total_studies = len(study_ids)
        successful_studies = 0
        
        with tqdm(total=total_studies, desc="Studies processed") as self.pbar:
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                future_to_study = {executor.submit(self.metadata_gather, study_id): study_id for study_id in study_ids}
                
                for future in concurrent.futures.as_completed(future_to_study):
                    study_id = future_to_study[future]
                    try:
                        if future.result():
                            with self.lock:
                                successful_studies += 1
                    except Exception as e:
                        self.safe_log(logging.ERROR, f'Error gathering metadata for study ID {study_id}: {e}')
                    finally:
                        with self.lock:
                            self.pbar.update(1)
        
        self.safe_log(logging.INFO, f'Metadata gathering completed. Successfully processed {successful_studies} out of {total_studies} studies.')

# fetch the study IDs from the csv 
def fetch_study_ids():
    study_ids = []
    with open('src/webscraping/mwb_csvs/mwb_with_metadata_link.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        for row in reader:
            study_id = row[0]
            study_ids.append(study_id)
    return study_ids

def main():
    study_ids = fetch_study_ids()
    scraper = MwbScraper()
    scraper.gather_metadata_concurrently(study_ids)


main()