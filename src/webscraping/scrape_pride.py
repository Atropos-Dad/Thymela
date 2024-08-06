# search_url = "https://www.ebi.ac.uk/pride/ws/archive/v2/search/projects?sortDirection=DESC&page=471&pageSize=60&dateGap=+1YEAR&keyword=*:*"

import requests
import json


# save the results to a file
def save_results(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f)


def make_search(page, num_results=100): 
    url = f"https://www.ebi.ac.uk/pride/ws/archive/v2/search/projects?sortDirection=DESC&page={page}&pageSize={num_results}&dateGap=+1YEAR&keyword=*:*"
    response = requests.get(url)
    return response.json()


# json schema for the search results
# {
#   "$schema": "http://json-schema.org/draft-07/schema#",
#   "title": "Generated schema for Root",
#   "type": "object",
#   "properties": {
#     "_embedded": {
#       "type": "object",
#       "properties": {
#         "compactprojects": {
#           "type": "array",
#           "items": {
#             "type": "object",
#             "properties": {
#               "highlights": {
#                 "type": "object",
#                 "properties": {},
#                 "required": []
#               },
#               "accession": {
#                 "type": "string"
#               },
#               "title": {
#                 "type": "string"
#               },
#               "projectDescription": {
#                 "type": "string"
#               },
#               "sampleProcessingProtocol": {
#                 "type": "string"
#               },
#               "dataProcessingProtocol": {
#                 "type": "string"
#               },
#               "keywords": {
#                 "type": "array",
#                 "items": {
#                   "type": "string"
#                 }
#               },
#               "submissionDate": {
#                 "type": "string"
#               },
#               "publicationDate": {
#                 "type": "string"
#               },
#               "license": {
#                 "type": "string"
#               },
#               "updatedDate": {
#                 "type": "string"
#               },
#               "submitters": {
#                 "type": "array",
#                 "items": {
#                   "type": "string"
#                 }
#               },
#               "labPIs": {
#                 "type": "array",
#                 "items": {
#                   "type": "string"
#                 }
#               },
#               "affiliations": {
#                 "type": "array",
#                 "items": {
#                   "type": "string"
#                 }
#               },
#               "instruments": {
#                 "type": "array",
#                 "items": {
#                   "type": "string"
#                 }
#               },
#               "organisms": {
#                 "type": "array",
#                 "items": {
#                   "type": "string"
#                 }
#               },
#               "organismParts": {
#                 "type": "array",
#                 "items": {
#                   "type": "string"
#                 }
#               },
#               "references": {
#                 "type": "array",
#                 "items": {
#                   "type": "string"
#                 }
#               },
#               "queryScore": {
#                 "type": "number"
#               },
#               "_links": {
#                 "type": "object",
#                 "properties": {
#                   "self": {
#                     "type": "object",
#                     "properties": {
#                       "href": {
#                         "type": "string"
#                       }
#                     },
#                     "required": [
#                       "href"
#                     ]
#                   },
#                   "datasetFtpUrl": {
#                     "type": "object",
#                     "properties": {
#                       "href": {
#                         "type": "string"
#                       }
#                     },
#                     "required": [
#                       "href"
#                     ]
#                   }
#                 },
#                 "required": [
#                   "self",
#                   "datasetFtpUrl"
#                 ]
#               },
#               "diseases": {
#                 "type": "array",
#                 "items": {
#                   "type": "string"
#                 }
#               },
#               "projectTags": {
#                 "type": "array",
#                 "items": {
#                   "type": "string"
#                 }
#               }
#             },
#             "required": [
#               "highlights",
#               "accession",
#               "title",
#               "projectDescription",
#               "sampleProcessingProtocol",
#               "dataProcessingProtocol",
#               "keywords",
#               "submissionDate",
#               "publicationDate",
#               "license",
#               "updatedDate",
#               "submitters",
#               "labPIs",
#               "affiliations",
#               "instruments",
#               "organisms",
#               "references",
#               "queryScore",
#               "_links"
#             ]
#           }
#         }
#       },
#       "required": [
#         "compactprojects"
#       ]
#     },
#     "_links": {
#       "type": "object",
#       "properties": {
#         "self": {
#           "type": "object",
#           "properties": {
#             "href": {
#               "type": "string"
#             }
#           },
#           "required": [
#             "href"
#           ]
#         },
#         "next": {
#           "type": "object",
#           "properties": {
#             "href": {
#               "type": "string"
#             }
#           },
#           "required": [
#             "href"
#           ]
#         },
#         "previous": {
#           "type": "object",
#           "properties": {
#             "href": {
#               "type": "string"
#             }
#           },
#           "required": [
#             "href"
#           ]
#         },
#         "first": {
#           "type": "object",
#           "properties": {
#             "href": {
#               "type": "string"
#             }
#           },
#           "required": [
#             "href"
#           ]
#         },
#         "last": {
#           "type": "object",
#           "properties": {
#             "href": {
#               "type": "string"
#             }
#           },
#           "required": [
#             "href"
#           ]
#         },
#         "facets": {
#           "type": "object",
#           "properties": {
#             "href": {
#               "type": "string"
#             }
#           },
#           "required": [
#             "href"
#           ]
#         }
#       },
#       "required": [
#         "self",
#         "next",
#         "previous",
#         "first",
#         "last",
#         "facets"
#       ]
#     },
#     "page": {
#       "type": "object",
#       "properties": {
#         "size": {
#           "type": "number"
#         },
#         "totalElements": {
#           "type": "number"
#         },
#         "totalPages": {
#           "type": "number"
#         },
#         "number": {
#           "type": "number"
#         }
#       },
#       "required": [
#         "size",
#         "totalElements",
#         "totalPages",
#         "number"
#       ]
#     }
#   },
#   "required": [
#     "_embedded",
#     "_links",
#     "page"
#   ]
# }

def parse_search_results(search_results):
    # grab the list of projects from the search results
    # for each project, grab all the metadata
    # return a list of dictionaries
    projects = search_results['_embedded']['compactprojects']
    project_data = []

    for project in projects:
        project_dict = {
            'accession': project.get('accession', 'unknown'),
            'title': project.get('title', 'unknown'),
            'projectDescription': project.get('projectDescription', 'unknown'),
            'sampleProcessingProtocol': project.get('sampleProcessingProtocol', 'unknown'),
            'dataProcessingProtocol': project.get('dataProcessingProtocol', 'unknown'),
            'keywords': project.get('keywords', 'unknown'),
            'submissionDate': project.get('submissionDate', 'unknown'),
            'publicationDate': project.get('publicationDate', 'unknown'),
            'license': project.get('license', 'unknown'),
            'updatedDate': project.get('updatedDate', 'unknown'),
            'submitters': project.get('submitters', 'unknown'),
            'labPIs': project.get('labPIs', 'unknown'),
            'affiliations': project.get('affiliations', 'unknown'),
            'instruments': project.get('instruments', 'unknown'),
            'organisms': project.get('organisms', 'unknown'),
            'organismParts': project.get('organismParts', 'unknown'),
            'references': project.get('references', 'unknown'),
            'queryScore': project.get('queryScore', 'unknown'),
            'diseases': project.get('diseases', 'unknown'),
            'projectTags': project.get('projectTags', 'unknown')
        }
        project_data.append(project_dict)

    return project_data


# test with pride_search_page1.json
with open('pride_search_page1.json') as f:
    mock_data = json.load(f)
    print(parse_search_results(mock_data)[0])
