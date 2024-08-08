# folder structure:
# /Metabolights/MTBLSxx/MTBLSxx_xxxx/i_Investigation.txt
# open this file and extract the study id

import os

def open_investigation_file(file_path):
    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith('Study Identifier'):
                return line.split('\t')[1].strip()
    return None


# get this line: Study Protocol Name and Study Protocol Type
def get_protocol(file_path):
    with open(file_path, 'r') as file:
        for line in file:
            tab_split = line.split('\t')
            if tab_split[0] == ('Study Protocol Name'):
                # print(f"Protocol Name: {line}")
                protocol_name = line.split('\t')[1:]
                protocol_name = [item.strip() for item in protocol_name]
            if tab_split[0] == ('Study Protocol Type'):
                # print(f"Protocol Type: {line}")
                protocol_type = line.split('\t')[1:]
                protocol_type = [item.strip() for item in protocol_type]
    return protocol_name, protocol_type


# print(get_protocol('/home/surtr/Downloads/Metabolights/MTBLS1/MTBLS1_193335/i_Investigation.txt'))  # MTBLS1

def get_all_investigation_files(main_folder):
    investigation_files = []
    for root, _, files in os.walk(main_folder):
        for file_name in files:
            if file_name == 'i_Investigation.txt':
                file_path = os.path.join(root, file_name)
                investigation_files.append(file_path)
    return investigation_files

main_folder = '/home/surtr/Downloads/'  # Add the path to the main folder containing the Metabolights subfolders
investigation_files = get_all_investigation_files(main_folder)

# validate all files
def validate_investigation_files(investigation_files):
    for file_path in investigation_files:
        Pname, Ptype  = get_protocol(file_path)
        if not Pname:
            print(f"Error: Study ID not found in {file_path}")
        if not Ptype:
            print(f"Error: Protocol not found in {file_path}")
        if Pname != Ptype:
            print(f"Error: Protocol Name and Protocol Type do not match in {file_path}")

validate_investigation_files(investigation_files)