import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from parsing.article_asseser import assess_article

def main():
    # Example usage:
    article_url = "https://www.ebi.ac.uk/pride/archive/projects/PXD054577"
    print(assess_article(article_url, "tests/mock_data/test_file.txt"))

    

if __name__ == "__main__":
    main()