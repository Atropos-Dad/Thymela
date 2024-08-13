from dbwrap.conn_pool import DatabasePool
from dbwrap.db_idvalid import classify_study_id

async def get_result(study_id):
    async with DatabasePool.acquire() as conn:
        async with conn.transaction():
            try:
                sql = 'SELECT * FROM public."processed_Studies" WHERE "studyId" = $1'
                result = await conn.fetchval(sql, study_id)
                return result
                
            except Exception as e:
                # Handle the error appropriately
                print(f"Error retrieving data for study ID {study_id}: {e}")
                pass



# get all results
async def get_all_results(limit=None):
    async with DatabasePool.acquire() as conn:
        async with conn.transaction():
            try:
                sql = 'SELECT * FROM public."processed_Studies"'
                if limit:
                    sql += f' LIMIT {limit}'
                
                results = await conn.fetch(sql)
                return results
                
            except Exception as e:
                # Handle the error appropriately
                print(f"Error retrieving data: {e}")
                pass