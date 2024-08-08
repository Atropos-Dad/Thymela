import os
import sys
from tqdm import tqdm
from parsing.article_asseser import assess_article
from parsing.article_asseser import assess_multiple_studies

def main():
    print(assess_multiple_studies(10))
            
if __name__ == "__main__":
    main()