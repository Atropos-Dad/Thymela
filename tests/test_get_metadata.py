"""
Unit tests for the get_metadata file
"""

import src.webscraping.get_metadata as get_metadata

def test_get_metadata():
    assert get_metadata.get_metadata() == "data"

