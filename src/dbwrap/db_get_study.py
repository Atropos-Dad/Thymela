from dbwrap.conn_single import PostgresSingleton
from dbwrap.db_idvalid import classify_study_id


def get_study(id):
    type = classify_study_id(id)
    
    table_name = f"{type}_Studies"
    sql = f'SELECT * FROM public."{table_name}" WHERE "studyId" = %s'
    
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
    

def get_studies_to_be_analysed(study_type="PRIDE", limit=None):
    # get all studies that have not been analysed
    if study_type not in ["PRIDE", "MBW", "Metabolights"]:
        raise ValueError("Invalid study type")
    
    table_name = f"{study_type}_Studies"
    sql = f'SELECT "studyId" FROM public."{table_name}" WHERE "studyId" NOT IN (SELECT "studyId" FROM public."processed_Studies")'
    
    if limit is not None:
        sql += f' LIMIT {limit}'

    conn = PostgresSingleton().get_connection()
    cur = conn.cursor()
    cur.execute(sql)
    studies = cur.fetchall()
    cur.close()

    return studies


