# Thymela

<div style="display: flex; flex-direction: row; align-items: center;">
    <img src="https://github.com/user-attachments/assets/9df51345-5285-42ba-98da-e58d418a96a6" width="240" style="margin-right: 10px;">
    <img src="https://github.com/user-attachments/assets/558cd0aa-bf88-4f1d-a44b-a630e7243344" width="240">
</div>

Thymela is a web application designed to analyze and search biomedical articles, with a particular focus on proteomics research data. The project provides a comprehensive suite of tools for scraping, analyzing, and searching research articles and their associated metadata. It was developed in collaboration with Meta-Flux @ DogpatchLabs! 

**<ins>NOTE - This is a prototype developed over the course of a week and has not been fully tested. As a result, proper formatting and 'best practices' are yet to be implemented.</ins>**

## Features

- **Web Scraping**: Automated scraping of research articles from multiple sources including:
  - Metabolomics Workbench (MWB)
  - PRIDE database
  - MetaboLights
  
- **Metadata Analysis**: 
  - Extracts and processes metadata from research articles
  - Handles various data formats and structures
  - Post-processing capabilities for different data sources

- **Search Functionality**:
  - search capabilities using vector indexing (via Pinecone! <3)

## Project Structure

```
src/
├── analyse_articles.py     # Core article analysis functionality
├── dbwrap/                 # Database wrapper and operations
├── parsing/                # Article parsing and API integration
├── prompting/              # Prompt management for analysis
├── searching/              # Search functionality implementation
├── templates/              # HTML templates
├── webapp/                 # Web application components
└── webscraping/            # Web scraping modules
```


![image](https://github.com/user-attachments/assets/28d321bf-e5d1-4045-bc67-fce1016a83a1)

