import csv


def check_for_dups():
    with open("mwb.csv", "r") as file:
        reader = csv.reader(file)
        # check if values of study ID column repeats ever
        study_ids = []
        for row in reader:
            study_id = row[0]
            if study_id in study_ids:
                print(f"Study ID {study_id} is repeated")
            study_ids.append(study_id)



# add a column to the csv with the metadata download link
def add_metadata_link():
    with open("mwb.csv", "r") as file:
        reader = csv.reader(file)
        rows = []
        header = next(reader)
        header.append("Metadata Download")
        rows.append(header)
        for row in reader:
            study_id = row[0]
            metadata_link = f"https://www.metabolomicsworkbench.org/data/study_textformat_list.php?JSON=YES&STUDY_ID={study_id}"
            row.append(metadata_link)
            rows.append(row)

    with open("src/webscraping/mwb_csvs/mwb_with_metadata_link.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(rows) 


import os
# for each study with a file in mwb_results folder, add a column with the 'downloaded' bool
def add_downloaded_column():
    with open("src/webscraping/mwb_csvs/mwb_with_metadata_link.csv", "r") as file:
        reader = csv.reader(file)
        rows = []
        header = next(reader)
        header.append("Downloaded")
        rows.append(header)
        for row in reader:
            study_id = row[0]
            downloaded = "True" if os.path.exists(f"src/webscraping/mwb_results/study_{study_id}_metadata.json") else "False"
            row.append(downloaded)
            rows.append(row)

    with open("src/webscraping/mwb_csvs/mwb_with_downloaded_column.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(rows)

def success_rate():
    # calculate the success rate of downloads
    with open("src/webscraping/mwb_csvs/mwb_with_downloaded_column.csv", "r") as file:
        reader = csv.reader(file)
        header = next(reader)
        downloaded_col = header.index("Downloaded")
        total = 0
        downloaded = 0
        for row in reader:
            total += 1
            if row[downloaded_col] == "True":
                downloaded += 1
        print(f"Success rate: {downloaded}/{total} ({downloaded/total:.2%})")

def mbw_get_all_studies():
    # for populating the db
    studies = []
    with open("src/webscraping/mwb_csvs/mwb_with_downloaded_column.csv", "r") as file:
        reader = csv.reader(file)
        header = next(reader)
        for row in reader:
            study = {
                "studyId": row[0],
                "studyTitle": row[1],
                "species": row[2],
                "institute": row[3],
                "analysis": row[4],
                "release": row[5],
                "samples": row[7],
                "metadataLink": row[9]
            }

            # get the mwTab from the json file
            study_id = (study["studyId"]).strip()
            try:   
                with open(f"src/webscraping/mwb_results/study_{study_id}_metadata.json", "r") as json_file:
                    study["mwTab"] = json_file.read()
            except FileNotFoundError:
                print(f"Could not find metadata file for study {study_id}")
                # dont add the study to the list
                continue

            studies.append(study)

    return studies


