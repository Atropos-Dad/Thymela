"""
Unit tests for the scrape_pride file
"""

import src.webscraping.scrape_pride
import json

mocked_total_pages = 283

def test_verify_results():
    # Mock the file data
    with open('tests/mock_data/pride_search_page1.json') as f:
        search_results = json.load(f)

    # Call the function under test
    scraper = src.webscraping.scrape_pride.PrideScrapper(total_pages=mocked_total_pages)
    result = scraper.verify_results(search_results)

    # Assert the result
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

    assert result == (len(compact_projects) == expected_num_results)

def test_parse_search_results():
        # Mock the file data
        with open('tests/mock_data/pride_search_page1.json') as f:
            search_results = json.load(f)


        # Call the function under test
        scraper = src.webscraping.scrape_pride.PrideScrapper(total_pages=mocked_total_pages)
        result = scraper.parse_search_results(search_results)

        # Assert the result
        assert len(result) == len(search_results['_embedded']['compactprojects'])

        # # Assert the first project's data
        # first_project = result[0]
        # assert first_project['accession'] == 'PXD000001'
        # assert first_project['title'] == 'Project Title 1'
        # assert first_project['projectDescription'] == 'Project Description 1'
        # assert first_project['sampleProcessingProtocol'] == 'Sample Processing Protocol 1'
        # assert first_project['dataProcessingProtocol'] == 'Data Processing Protocol 1'
        # assert first_project['keywords'] == 'Keywords 1'
        # assert first_project['submissionDate'] == '2022-01-01'
        # assert first_project['publicationDate'] == '2022-01-02'
        # assert first_project['license'] == 'License 1'
        # assert first_project['updatedDate'] == '2022-01-03'
        # assert first_project['submitters'] == 'Submitters 1'
        # assert first_project['labPIs'] == 'Lab PIs 1'
        # assert first_project['affiliations'] == 'Affiliations 1'
        # assert first_project['instruments'] == 'Instruments 1'
        # assert first_project['organisms'] == 'Organisms 1'
        # assert first_project['organismParts'] == 'Organism Parts 1'
        # assert first_project['references'] == 'References 1'
        # assert first_project['queryScore'] == 'Query Score 1'
        # assert first_project['diseases'] == 'Diseases 1'
        # assert first_project['projectTags'] == 'Project Tags 1'

        
    
