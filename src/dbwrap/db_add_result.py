from dbwrap.conn_single import PostgresSingleton
from dbwrap.db_idvalid import classify_study_id

def add_result(study_id, response):
    # StudyID: string, response: json, created: date, source: string
    source = classify_study_id(study_id)

    sql = f'INSERT INTO public."processed_Studies" ("studyId", "response", "source") VALUES (%s, %s, %s)'
    conn = PostgresSingleton().get_connection()
    cur = conn.cursor()
    cur.execute(sql, (study_id, response, source))
    conn.commit()
    cur.close()

    