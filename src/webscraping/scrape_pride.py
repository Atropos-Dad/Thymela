import requests
import json
import concurrent.futures
import threading
import os
from tqdm import tqdm

class PrideScrapper:
    def __init__(self, total_pages, results_per_page=100, output_folder='pride_results'):
        self.total_pages = total_pages
        self.results_per_page = results_per_page
        self.lock = threading.Lock()
        self.output_folder = output_folder
        
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
        
        self.pbar = tqdm(total=self.total_pages, desc="Pages processed")

    def save_results(self, data, page_number):
        filename = os.path.join(self.output_folder, f'page_{page_number}.json')
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

    def verify_results(self, search_results):
        total_pages = search_results['page']['totalPages']
        current_page = search_results['page']['number']
        page_size = search_results['page']['size']
        total_elements = search_results['page']['totalElements']
        compact_projects = search_results['_embedded']['compactprojects']

        if total_pages == current_page:
            expected_num_results = total_elements % page_size
            if expected_num_results == 0:
                expected_num_results = page_size
        else:
            expected_num_results = page_size

        return len(compact_projects) == expected_num_results

    def parse_search_results(self, search_results):
        projects = search_results['_embedded']['compactprojects']
        project_data = []

        for project in projects:
            project_dict = {
                'accession': project.get('accession', 'unknown'),
                'title': project.get('title', 'unknown'),
                'projectDescription': project.get('projectDescription', 'unknown'),
                'sampleProcessingProtocol': project.get('sampleProcessingProtocol', 'unknown'),
                'dataProcessingProtocol': project.get('dataProcessingProtocol', 'unknown'),
                'keywords': project.get('keywords', 'unknown'),
                'submissionDate': project.get('submissionDate', 'unknown'),
                'publicationDate': project.get('publicationDate', 'unknown'),
                'license': project.get('license', 'unknown'),
                'updatedDate': project.get('updatedDate', 'unknown'),
                'submitters': project.get('submitters', 'unknown'),
                'labPIs': project.get('labPIs', 'unknown'),
                'affiliations': project.get('affiliations', 'unknown'),
                'instruments': project.get('instruments', 'unknown'),
                'organisms': project.get('organisms', 'unknown'),
                'organismParts': project.get('organismParts', 'unknown'),
                'references': project.get('references', 'unknown'),
                'queryScore': project.get('queryScore', 'unknown'),
                'diseases': project.get('diseases', 'unknown'),
                'projectTags': project.get('projectTags', 'unknown')
            }
            project_data.append(project_dict)

        return project_data

    def fetch_search(self, page_number):
        url = f"https://www.ebi.ac.uk/pride/ws/archive/v2/search/projects?sortDirection=DESC&page={page_number}&pageSize={self.results_per_page}&dateGap=+1YEAR&keyword=*:*"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            results_count = len(data['_embedded']['compactprojects'])
            
            parsed_results = self.parse_search_results(data)
            
            with self.lock:
                self.save_results(parsed_results, page_number)
                self.pbar.update(1)
            
            if not self.verify_results(data):
                self.pbar.write(f"Warning: Page {page_number} returned {results_count} results instead of the expected number")
            
            return results_count
        else:
            self.pbar.write(f"Error fetching page {page_number}: Status code {response.status_code}")
            return 0

    def fetch_all_pages(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_page = {executor.submit(self.fetch_search, page): page for page in range(0, self.total_pages)}
            
            for future in concurrent.futures.as_completed(future_to_page):
                page = future_to_page[future]
                try:
                    future.result()
                except Exception as exc:
                    self.pbar.write(f"Page {page} generated an exception: {exc}")
        
        self.pbar.close()

def main():
    manager = PrideScrapper(total_pages=283, results_per_page=100, output_folder='pride_results')
    manager.fetch_all_pages()

# if __name__ == "__main__":
main()