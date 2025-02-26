from dbwrap.conn_pool import DatabasePool
from dbwrap.db_idvalid import classify_study_id

import logging; logger = logging.getLogger(__name__)

async def add_result(study_id, response):
    source = classify_study_id(study_id)

    async with DatabasePool.acquire() as conn:
        async with conn.transaction():
            try:
                sql = 'INSERT INTO public."processed_Studies" ("studyId", "response", "source") VALUES ($1, $2, $3)'
                await conn.execute(sql, study_id, response, source)
                
            except Exception as e:
                # Handle the error appropriately
                logging.error(f"Error inserting data for study ID {study_id}: {e}")
                logging.error(f"Data: {study_id}, {response}, {source}")
                pass # auto roll back