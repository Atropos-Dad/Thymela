def classify_study_id(id):
    # check which type the id is:
    # PXD053960 - pride
    # or
    # ST000001 - mwb
    # or 
    # MTBLS10401 - metabolights
    
    
    if id.startswith("PXD"):
        type = "PRIDE"
    elif id.startswith("ST"):
        type = "MBW"
    elif id.startswith("MTBLS"):
        type = "Metabolights"
    else:
        raise ValueError("Invalid study id")
    return type
