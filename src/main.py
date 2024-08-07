import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from parsing.article_asseser import assess_article

def main():
    # Example usage:
    article_url = ""
    print(assess_article(article_url, "tests/mock_data/Testing_File.txt"))

    

if __name__ == "__main__":
    main()