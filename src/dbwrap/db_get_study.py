from dbwrap.conn_single import PostgresSingleton


def get_study(id):
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
    
    table_name = f"{type}_Studies"
    sql = f'SELECT * FROM public."{table_name}" WHERE "StudyId" = %s'
    
    conn = PostgresSingleton().get_connection()
    cur = conn.cursor()
    cur.execute(sql, (id,))
    study = cur.fetchone()
    cur.close()

    return study


def get_n_studies(number, study_type="PRIDE"):
    # get n studies of a from a given table name
    if study_type not in ["PRIDE", "MBW", "Metabolights"]:
        raise ValueError("Invalid study type")
    
    table_name = f"{study_type}_Studies"
    sql = f'SELECT * FROM public."{table_name}" LIMIT %s'

    conn = PostgresSingleton().get_connection()
    cur = conn.cursor()
    cur.execute(sql, (number,))
    studies = cur.fetchall()
    cur.close()

    return studies
    

