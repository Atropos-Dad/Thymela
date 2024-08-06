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
    
    

