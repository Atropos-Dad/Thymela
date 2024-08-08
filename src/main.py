import os
import sys
from tqdm import tqdm
from dbwrap.db_get_study import get_n_studies
from parsing.article_asseser import assess_article

def main():

    studies = get_n_studies(10, "PRIDE")
    for study in tqdm(studies):
        article_url = ""
        output = assess_article(study) 
            
if __name__ == "__main__":
    main()