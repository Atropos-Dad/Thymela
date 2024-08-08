import pytest
from unittest import mock
from src.webscraping.post_process_mwb import mbw_get_all_studies

def test_mbw_get_all_studies():
    # Mock the file data
    mock_csv_data = [
        ["header,header,header,header,header,header,header,header,header,header,header"],
        ['ST002258', 'Lipidomic profiling reveals age-dependent changes in complex plasma membrane lipids that regulate neural stem cell aging (Part 2)', 'Mus musculus', 'Stanford University', 'LC-MS#', '2024-08-05', '1', '48', '/data/DRCCStudySummary.php?Mode=SetupRawDataDownload&StudyID=ST002258', 'https://www.metabolomicsworkbench.org/data/study_textformat_list.php?JSON=YES&STUDY_ID=ST002258', 'True'],
        ['ST002808', 'The ECHO Cohort Exposome: First Steps using HHEAR Analysis – An Opportunity for ALL ECHO Cohorts to Contribute Type A Samples – Untargeted Analysis (DINE Cohorts)', 'Homo sapiens', 'Zucker School of Medicine at Hofstra / Northwell', 'LC-MS#', '2024-08-05', '1', '526', '/data/DRCCStudySummary.php?Mode=SetupRawDataDownload&StudyID=ST002808', 'https://www.metabolomicsworkbench.org/data/study_textformat_list.php?JSON=YES&STUDY_ID=ST002808', 'True'],
        ['ST002811', 'Metabolomics panel associated with cystic fibrosis-related diabetes towards biomarker discovery', 'Homo sapiens', 'King Faisal Specialist Hospital and Research Centre (KFSHRC)', 'LC-MS#', '2024-08-05', '1', '72', '/data/DRCCStudySummary.php?Mode=SetupRawDataDownload&StudyID=ST002811', 'https://www.metabolomicsworkbench.org/data/study_textformat_list.php?JSON=YES&STUDY_ID=ST002811', 'True']
]

    with mock.patch('builtins.open', mock.mock_open(read_data='\n'.join([','.join(row) for row in mock_csv_data]))) as mock_file:
        studies = mbw_get_all_studies()

    for i in studies:
        print(i)
    assert len(studies) == 3

    def test_mbw_get_all_studies():
        # Mock the file data
        mock_csv_data = [
            ['ST002258', 'Lipidomic profiling reveals age-dependent changes in complex plasma membrane lipids that regulate neural stem cell aging (Part 2)', 'Mus musculus', 'Stanford University', 'LC-MS#', '2024-08-05', '1', '48', '/data/DRCCStudySummary.php?Mode=SetupRawDataDownload&StudyID=ST002258', 'https://www.metabolomicsworkbench.org/data/study_textformat_list.php?JSON=YES&STUDY_ID=ST002258', 'True'],
            ['ST002808', 'The ECHO Cohort Exposome: First Steps using HHEAR Analysis – An Opportunity for ALL ECHO Cohorts to Contribute Type A Samples – Untargeted Analysis (DINE Cohorts)', 'Homo sapiens', 'Zucker School of Medicine at Hofstra / Northwell', 'LC-MS#', '2024-08-05', '1', '526', '/data/DRCCStudySummary.php?Mode=SetupRawDataDownload&StudyID=ST002808', 'https://www.metabolomicsworkbench.org/data/study_textformat_list.php?JSON=YES&STUDY_ID=ST002808', 'True'],
            ['ST002811', 'Metabolomics panel associated with cystic fibrosis-related diabetes towards biomarker discovery', 'Homo sapiens', 'King Faisal Specialist Hospital and Research Centre (KFSHRC)', 'LC-MS#', '2024-08-05', '1', '72', '/data/DRCCStudySummary.php?Mode=SetupRawDataDownload&StudyID=ST002811', 'https://www.metabolomicsworkbench.org/data/study_textformat_list.php?JSON=YES&STUDY_ID=ST002811', 'True']
        ]

        with mock.patch('builtins.open', mock.mock_open(read_data='\n'.join([','.join(row) for row in mock_csv_data]))) as mock_file:
            studies = mbw_get_all_studies()

        assert len(studies) == 3

        # Additional assert tests
        assert studies[0]['study_id'] == 'ST002258'
        assert studies[0]['title'] == 'Lipidomic profiling reveals age-dependent changes in complex plasma membrane lipids that regulate neural stem cell aging (Part 2)'
        assert studies[0]['species'] == 'Mus musculus'
        assert studies[0]['institution'] == 'Stanford University'
        assert studies[0]['technique'] == 'LC-MS#'
        assert studies[0]['date'] == '2024-08-05'
        assert studies[0]['replicates'] == '1'
        assert studies[0]['samples'] == '48'
        assert studies[0]['download_link'] == '/data/DRCCStudySummary.php?Mode=SetupRawDataDownload&StudyID=ST002258'
        assert studies[0]['metadata_link'] == 'https://www.metabolomicsworkbench.org/data/study_textformat_list.php?JSON=YES&STUDY_ID=ST002258'
        assert studies[0]['downloaded'] == 'True'

        assert studies[1]['study_id'] == 'ST002808'
        assert studies[1]['title'] == 'The ECHO Cohort Exposome: First Steps using HHEAR Analysis – An Opportunity for ALL ECHO Cohorts to Contribute Type A Samples – Untargeted Analysis (DINE Cohorts)'
        assert studies[1]['species'] == 'Homo sapiens'
        assert studies[1]['institution'] == 'Zucker School of Medicine at Hofstra / Northwell'
        assert studies[1]['technique'] == 'LC-MS#'
        assert studies[1]['date'] == '2024-08-05'
        assert studies[1]['replicates'] == '1'
        assert studies[1]['samples'] == '526'
        assert studies[1]['download_link'] == '/data/DRCCStudySummary.php?Mode=SetupRawDataDownload&StudyID=ST002808'
        assert studies[1]['metadata_link'] == 'https://www.metabolomicsworkbench.org/data/study_textformat_list.php?JSON=YES&STUDY_ID=ST002808'
        assert studies[1]['downloaded'] == 'True'

        assert studies[2]['study_id'] == 'ST002811'
        assert studies[2]['title'] == 'Metabolomics panel associated with cystic fibrosis-related diabetes towards biomarker discovery'
        assert studies[2]['species'] == 'Homo sapiens'
        assert studies[2]['institution'] == 'King Faisal Specialist Hospital and Research Centre (KFSHRC)'
        assert studies[2]['technique'] == 'LC-MS#'
        assert studies[2]['date'] == '2024-08-05'
        assert studies[2]['replicates'] == '1'
        assert studies[2]['samples'] == '72'
        assert studies[2]['download_link'] == '/data/DRCCStudySummary.php?Mode=SetupRawDataDownload&StudyID=ST002811'
        assert studies[2]['metadata_link'] == 'https://www.metabolomicsworkbench.org/data/study_textformat_list.php?JSON=YES&STUDY_ID=ST002811'
        assert studies[2]['downloaded'] == 'True'