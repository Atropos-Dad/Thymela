import os
import json
def verify_type():
    # for each result in pride_results, verify that the type is dict, and then check if organisms key for each project is not a list
    for filename in os.listdir("src/webscraping/pride_results"):
        with open(f"src/webscraping/pride_results/{filename}", "r") as file:
            data = json.load(file)
            for project in data:    
                try:
                    assert isinstance(project, dict), "project is not a dict"
                    organisms = project["diseases"]
                    if isinstance(organisms, list):
                        if len(organisms) == 1:
                            print("Single organism")
                        else:
                            assert False, "organisms key is a list"
                except:
                    print(f"Error in {filename}")
                    print(project)
                    print(project["diseases"])
                    print()
                    exit()
                

def pride_get_all_studies():
    # for populating the db
    studies = []
    for filename in os.listdir("src/webscraping/pride_results"):
        with open(f"src/webscraping/pride_results/{filename}", "r") as file:
            data = json.load(file)
            for project in data:
                studies.append(project)

    return studies
