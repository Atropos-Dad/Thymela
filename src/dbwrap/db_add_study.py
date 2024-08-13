import psycopg2
import logging; logger = logging.getLogger(__name__)
from dbwrap.conn_single import PostgresSingleton
import json 

def add_to_MBW_studies(input_dict):
    """
    Add a single row to the "MBW_Studies" table in a PostgreSQL database.

    Args:
        input_dict (dict): A dictionary containing the data for a single row to be inserted.
                          The keys in the dictionary should be: 'studyId', 'mwTab', 'studyTitle', 'species', 'institute', 'analysis', 'release', 'samples', 'metadataLink'.
    """
    try:
        # Validate the input data
        if not isinstance(input_dict, dict):
            raise Exception("Input should be a dictionary")
        if "studyId" not in input_dict:
            raise Exception("Missing 'studyId' key in input")
        if "mwTab" not in input_dict:
            raise Exception("Missing 'mwTab' key in input")
        if "studyTitle" not in input_dict:
            raise Exception("Missing 'studyTitle' key in input")
        if "species" not in input_dict:
            raise Exception("Missing 'species' key in input")
        if "institute" not in input_dict:
            raise Exception("Missing 'institute' key in input")
        if "analysis" not in input_dict:
            raise Exception("Missing 'analysis' key in input")
        if "release" not in input_dict:
            raise Exception("Missing 'release' key in input")
        if "samples" not in input_dict:
            raise Exception("Missing 'samples' key in input")
        if "metadataLink" not in input_dict:
            raise Exception("Missing 'metadataLink' key in input")

        if type(input_dict["studyId"]) != str:
            raise Exception(f"Expected studyId to be a string, but got {type(input_dict['studyId']).__name__} instead")
        if type(input_dict["mwTab"]) != dict:
            try:
                input_dict["mwTab"] = json.loads(input_dict["mwTab"])
            except:
                raise Exception(f"Expected mwTab to be a dictionary/valid json, but got {type(input_dict['mwTab']).__name__} instead")

        if type(input_dict["studyTitle"]) != str:
            raise Exception(f"Expected studyTitle to be a string, but got {type(input_dict['studyTitle']).__name__} instead")
        if type(input_dict["species"]) != list:
            try:
                input_dict["species"] = [input_dict["species"]]
            except:
                raise Exception(f"Expected species to be a list of strings, but got {type(input_dict['species']).__name__} instead")
        if type(input_dict["institute"]) != str:
            raise Exception(f"Expected institute to be a string, but got {type(input_dict['institute']).__name__} instead")
        if type(input_dict["analysis"]) != str:
            raise Exception(f"Expected analysis to be a string, but got {type(input_dict['analysis']).__name__} instead")
        if type(input_dict["release"]) != str:
            raise Exception(f"Expected release to be a string, but got {type(input_dict['release']).__name__} instead")
        if type(input_dict["samples"]) != int:
            try:
                input_dict["samples"] = int(input_dict["samples"])
            except:
                raise Exception(f"Expected samples to be an integer, but got {type(input_dict['samples']).__name__} instead")
        if type(input_dict["metadataLink"]) != str:
            raise Exception(f"Expected metadataLink to be a string, but got {type(input_dict['metadataLink']).__name__} instead")
    except Exception as e:
        logging.error(f"Error with input: {input_dict['studyId']}")
        logging.error(e)
        return

    # Convert the dictionary to Json
    mwTab_json = psycopg2.extras.Json(input_dict["mwTab"])

    # Define the SQL query
    sql = """INSERT INTO "MBW_Studies" ("studyId", "mwTab", "studyTitle", "species", "institute", "analysis", "release", "samples", "metadataLink")
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);"""

    # Execute the SQL query
    conn = PostgresSingleton().get_connection()
    cur = conn.cursor()
    cur.execute(sql, (input_dict["studyId"], mwTab_json, input_dict["studyTitle"], input_dict["species"], input_dict["institute"], input_dict["analysis"], input_dict["release"], input_dict["samples"], input_dict["metadataLink"]))
    conn.commit()


def add_to_MBW_studies_batch(inputs):
    """
    Add multiple rows to the "MBW_Studies" table in a PostgreSQL database using a batch insert.

    Args:
        inputs (list[dict]): A list of dictionaries, where each dictionary represents the data for one row to be inserted.
                             The keys in each dictionary should be: 'studyId', 'mwTab', 'studyTitle', 'species', 'institute', 'analysis', 'release', 'samples', 'metadataLink'.
    """
    # Validate the input data
    for input_dict in inputs:
        try:
            if not isinstance(input_dict, dict):
                raise Exception("Input should be a dictionary")
            if "studyId" not in input_dict:
                raise Exception("Missing 'studyId' key in input")
            if "mwTab" not in input_dict:
                raise Exception("Missing 'mwTab' key in input")
            if "studyTitle" not in input_dict:
                raise Exception("Missing 'studyTitle' key in input")
            if "species" not in input_dict:
                raise Exception("Missing 'species' key in input")
            if "institute" not in input_dict:
                raise Exception("Missing 'institute' key in input")
            if "analysis" not in input_dict:
                raise Exception("Missing 'analysis' key in input")
            if "release" not in input_dict:
                raise Exception("Missing 'release' key in input")
            if "samples" not in input_dict:
                raise Exception("Missing 'samples' key in input")
            if "metadataLink" not in input_dict:
                raise Exception("Missing 'metadataLink' key in input")
            

            if type(input_dict["studyId"]) != str:
                raise Exception(f"Expected studyId to be a string, but got {type(input_dict['studyId']).__name__} instead")
            if type(input_dict["mwTab"]) != dict:
                try:
                    input_dict["mwTab"] = json.loads(input_dict["mwTab"])
                except:
                    raise Exception(f"Expected mwTab to be a dictionary/valid json, but got {type(input_dict['mwTab']).__name__} instead")
            
            if type(input_dict["studyTitle"]) != str:
                raise Exception(f"Expected studyTitle to be a string, but got {type(input_dict['studyTitle']).__name__} instead")
            if type(input_dict["species"]) != list:
                try:
                    input_dict["species"] = [input_dict["species"]]
                except:
                    raise Exception(f"Expected species to be a list of strings, but got {type(input_dict['species']).__name__} instead")
            if type(input_dict["institute"]) != str:
                raise Exception(f"Expected institute to be a string, but got {type(input_dict['institute']).__name__} instead")
            if type(input_dict["analysis"]) != str:
                raise Exception(f"Expected analysis to be a string, but got {type(input_dict['analysis']).__name__} instead")
            if type(input_dict["release"]) != str:
                raise Exception(f"Expected release to be a string, but got {type(input_dict['release']).__name__} instead")
            if type(input_dict["samples"]) != int:
                try:
                    input_dict["samples"] = int(input_dict["samples"])
                except:
                    raise Exception(f"Expected samples to be an integer, but got {type(input_dict['samples']).__name__} instead")
            if type(input_dict["metadataLink"]) != str:
                raise Exception(f"Expected metadataLink to be a string, but got {type(input_dict['metadataLink']).__name__} instead")
        except Exception as e:
            logging.error(f"Error with input: {input_dict['studyId']}")
            # input(f"{input_dict}")
            logging.error(e)
            input_dict["valid"] = False

    # Filter out invalid inputs
    valid_inputs = [input for input in inputs if input.get("valid", True)]
    # Convert the dictionaries to Json
    converted_inputs = [(input["studyId"], psycopg2.extras.Json(input["mwTab"]), input["studyTitle"], input["species"], input["institute"], input["analysis"], input["release"], input["samples"], input["metadataLink"]) for input in inputs]

    logging.info("Compiled valid studies... ready to insert")
    logging.debug(f"Number of valid studies: {len(valid_inputs)}")
    logging.debug(f"Original number of studies: {len(inputs)}")
    logging.debug(f"Number of invalid studies: {len(inputs) - len(valid_inputs)}")
    logging.debug(f"Success rate: {len(valid_inputs)/len(inputs):.2%}")
    input("press enter to continue")

    # Define the SQL query
    sql = """INSERT INTO "MBW_Studies" ("studyId", "mwTab", "studyTitle", "species", "institute", "analysis", "release", "samples", "metadataLink")
             VALUES %s;"""

    # Execute the SQL query
    conn = PostgresSingleton().get_connection()
    cur = conn.cursor()
    psycopg2.extras.execute_values(cur, sql, converted_inputs, page_size=100)
    conn.commit()


def add_to_Pride_studies(input):
    conn = PostgresSingleton().get_connection()
    cur = conn.cursor()

    # verify input
#     CREATE TABLE "PRIDE_Studies" (
# 	"id" SERIAL NOT NULL UNIQUE,
# 	"accession" VARCHAR,
# 	"title" VARCHAR,
# 	"projectDescription" TEXT,
# 	"sampleProcessingProtocol" TEXT,
# 	"dataProcessingProtocol" TEXT,
# 	"keywords" VARCHAR ARRAY,
# 	"organisms" VARCHAR ARRAY,
# 	"organismParts" VARCHAR ARRAY,
# 	"diseases" VARCHAR ARRAY,
# 	"projectTags" VARCHAR ARRAY,
# 	"instruments" VARCHAR ARRAY,
# 	PRIMARY KEY("id")
# );

    # for each type expected to be list, check if it is a list of strings. If it's a string, convert it to a list of strings
    for i in range(5, 11):
        if type(input[i]) == str:
            input[i] = [input[i]]

    if len(input) != 11:
        raise Exception(f"Input should have 11 elements, but got {len(input)} elements")
    if type(input[0]) != str:
        raise Exception(f"Expected accession to be a string, but got {type(input[0]).__name__} instead")
    if type(input[1]) != str:
        raise Exception(f"Expected title to be a string, but got {type(input[1]).__name__} instead")
    if type(input[2]) != str:
        raise Exception(f"Expected projectDescription to be a string, but got {type(input[2]).__name__} instead")
    if type(input[3]) != str:
        raise Exception(f"Expected sampleProcessingProtocol to be a string, but got {type(input[3]).__name__} instead")
    if type(input[4]) != str:
        raise Exception(f"Expected dataProcessingProtocol to be a string, but got {type(input[4]).__name__} instead")
    if type(input[5]) != list:
        raise Exception(f"Expected keywords to be a list of strings, but got {type(input[5]).__name__} instead")
    if type(input[6]) != list:
        raise Exception(f"Expected organisms to be a list of strings, but got {type(input[6]).__name__} instead")
    if type(input[7]) != list:
        raise Exception(f"Expected organismParts to be a list of strings, but got {type(input[7]).__name__} instead")
    if type(input[8]) != list:
        raise Exception(f"Expected diseases to be a list of strings, but got {type(input[8]).__name__} instead")
    if type(input[9]) != list:
        raise Exception(f"Expected projectTags to be a list of strings, but got {type(input[9]).__name__} instead")
    if type(input[10]) != list:
        raise Exception(f"Expected instruments to be a list of strings, but got {type(input[10]).__name__} instead")

    # Define the SQL query
    sql = """INSERT INTO "PRIDE_Studies" ("accession", "title", "projectDescription", "sampleProcessingProtocol", "dataProcessingProtocol", "keywords", "organisms", "organismParts", "diseases", "projectTags", "instruments")
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
    
    # Execute the SQL query
    cur.execute(sql, input)

    # Commit the transaction
    conn.commit()



