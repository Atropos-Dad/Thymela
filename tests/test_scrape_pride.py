"""
Unit tests for the scrape_pride file
"""

import src.webscraping.scrape_pride
import json

def test_make_search(mocker):
    with open('tests/mock_data/pride_search_page1.json') as f:
        mock_data = json.load(f)

    mock_response = mocker.MagicMock()
    mock_response.json.return_value = mock_data    

    mocker.patch("requests.get", return_value=mock_response)

    result = src.webscraping.scrape_pride.make_search(1)

    assert type(result) == dict
    assert result == mock_data
    
    


def test_parse_search_results():
        # Mock the file data
        with open('tests/mock_data/pride_search_page1.json') as f:
            search_results = json.load(f)


        # Call the function under test
        result = src.webscraping.scrape_pride.parse_search_results(search_results)

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

        
    
