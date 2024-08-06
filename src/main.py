import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from parsing.article_asseser import assess_article

def main():
    # Example usage:
    article_url = "https://www.ebi.ac.uk/pride/archive/projects/PXD054577"
    metadata_json = assess_article(article_url)
    print("Extracted Metadata JSON:", metadata_json)

    

if __name__ == "__main__":
    main()